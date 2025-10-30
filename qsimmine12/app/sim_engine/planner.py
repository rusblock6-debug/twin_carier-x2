from __future__ import annotations

import logging
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Tuple, List, Optional
from math import floor
from ortools.sat.python import cp_model

from pulp import (
    LpProblem, LpMaximize, LpVariable, LpBinary, LpInteger, lpSum, LpStatus, value, PULP_CBC_CMD, HiGHS_CMD, SCIP_CMD,
)


import os

from app.sim_engine.core.calculations.shovel import ShovelCalc
from app.sim_engine.core.calculations.truck import TruckCalc
from app.sim_engine.core.calculations.unload import UnloadCalc
from app.sim_engine.core.geometry import build_route_edges_by_road_net, build_route_edges_by_road_net_from_position
from app.sim_engine.core.props import SimData, PlannedTrip
from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver as DR
from app.sim_engine.enums import ObjectType

logger = logging.getLogger(__name__)


@dataclass
class InputPlanningData:
    N: int  # количество самосвалов
    M: int  # количество экскаваторов
    Z: int  # количество площадок разгрузки
    D_work: int  # длительность смены (мин)

    # Матрицы/словари времени:
    T_haul: Dict[Tuple[int, int, int], int]  # ключ (i,j,z)
    T_return: Dict[Tuple[int, int, int], int]  # ключ (i,j,z)
    T_load: Dict[Tuple[int, int], int]  # ключ (i,j)
    T_unload: Dict[Tuple[int, int], int]  # ключ (i,z)
    T_start: Dict[Tuple[int, int], int]  # ключ (i,j)
    T_end: Dict[Tuple[int, int], int]  # ключ (i,z)

    # тоннаж на рейс
    m_tons: Dict[Tuple[int, int], float]  # ключ (i,j)

    # верхняя граница числа рейсов для каждого самосвала
    Kmax_by_truck: Optional[Dict[int, int]] = None

    # Удобные множества ID
    @property
    def truck_ids(self) -> List[int]:
        return sorted({i for (i, _) in self.T_load.keys()})

    @property
    def shovel_ids(self) -> List[int]:
        return sorted({j for (_, j) in self.T_load.keys()})

    @property
    def unload_ids(self) -> List[int]:
        return sorted({z for (_, z) in self.T_unload.keys()})


def compute_Kmax_i(inst: InputPlanningData, i: int) -> int:
    """Грубая верхняя граница числа рейсов для самосвала i"""
    js = {j for (ti, j) in inst.T_start.keys() if ti == i}
    zs = {z for (ti, z) in inst.T_end.keys() if ti == i}
    min_start = min(inst.T_start[i, j] for j in js)
    min_end = min(inst.T_end[i, z] for z in zs)
    min_d = min(
        inst.T_haul[i, j, z] + inst.T_return[i, z, j] + inst.T_load[i, j] + inst.T_unload[i, z]
        for j in js for z in zs
    )
    available = inst.D_work - min_start - min_end
    return max(0, floor(available / max(1, min_d)))


def default_Kmax(inst: InputPlanningData) -> Dict[int, int]:
    """Если Kmax не задан, вычислить его для каждого самосвала"""
    return {i: compute_Kmax_i(inst, i) for i in inst.truck_ids}


def build_model(inst: InputPlanningData, shovel_queue: bool = True):
    """Собираем все ограничения и условия поиска решения"""
    I = inst.truck_ids
    J = inst.shovel_ids
    Z = inst.unload_ids

    # Верхние границы числа рейсов по самосвалам
    Kmax = inst.Kmax_by_truck or default_Kmax(inst)

    # Полный список потенциальных рейсов
    P: List[Tuple[int, int]] = [(i, k) for i in I for k in range(1, Kmax[i] + 1)]

    # Оптимизационная задача: максимизация добычи
    model = LpProblem("MaxVolume", LpMaximize)

    # Константы Big‑M и эпсилон:
    #   Mbig — должна быть достаточной верхней границей времени (тут — длительность смены)
    #   eps  — минимальный «зазор» для строгого порядка выполнения погрузки (1 единица времени)
    Mbig = inst.D_work
    eps = 1

    # Переменные
    x = {(i, k, j, z): LpVariable(f"x_{i}_{k}_{j}_{z}", 0, 1, LpBinary)
         for (i, k) in P for j in J for z in Z}

    # y[i,k] ∈ {0,1} — k-ый рейс i-ого самосвала существует
    y = {(i, k): LpVariable(f"y_{i}_{k}", 0, 1, LpBinary) for (i, k) in P}

    # Временные переменные (целочисленные):
    #   s_load   — старт погрузки
    #   s_unload — старт разгрузки
    #   a_arr    — прибытие к экскаватору перед погрузкой
    s_load = {(i, k): LpVariable(f"sLoad_{i}_{k}", lowBound=0, cat=LpInteger) for (i, k) in P}
    s_unload = {(i, k): LpVariable(f"sUnload_{i}_{k}", lowBound=0, cat=LpInteger) for (i, k) in P}
    a_arr = {(i, k): LpVariable(f"aArr_{i}_{k}", lowBound=0, cat=LpInteger) for (i, k) in P}
    q = {(i, k, j, z): LpVariable(f"q_{i}_{k}_{j}_{z}", 0, 1, LpBinary)
         for i in I for k in range(1, Kmax[i]) for j in J for z in Z}
    ell = {(i, k): LpVariable(f"ell_{i}_{k}", 0, 1, LpBinary) for (i, k) in P}

    # w[p,q,j] ∈ {0,1} — порядок обслуживания очереди экскаватора для пар рейсов p<q на экскаваторе j
    w = {}
    if shovel_queue:
        for j in J:
            for idx_p in range(len(P)):
                for idx_q in range(idx_p + 1, len(P)):
                    p = P[idx_p]
                    q_ = P[idx_q]
                    w[p, q_, j] = LpVariable(
                        f"w_{p[0]}_{p[1]}__{q_[0]}_{q_[1]}__j{j}", 0, 1, LpBinary
                    )

    # Вспомогательные суммы
    def a_use(i, k, j):
        return lpSum(x[i, k, j, z] for z in Z)

    def b_use(i, k, z):
        return lpSum(x[i, k, j, z] for j in J)

    # Ограничения
    for (i, k) in P:
        model += lpSum(x[i, k, j, z] for j in J for z in Z) == y[i, k]

    # (A2) Непрерывность по k
    for i in I:
        for k in range(1, Kmax[i]):
            model += y[i, k + 1] <= y[i, k]

    # (A3) Для первого рейса прибытие в начале смены и запрет начинать раньше
    for i in I:
        if Kmax[i] == 0:
            continue
        k = 1
        # s_load[i,1] ≥ a_arr[i,1]
        model += s_load[i, k] >= a_arr[i, k]
        # a_arr[i,1] = Σ_j T_start[i,j] * a_use(i,1,j)
        model += a_arr[i, k] == lpSum(inst.T_start[i, j] * a_use(i, k, j) for j in J)

    # (A4) Начало разгрузки не раньше завершения погрузки + гружёного хода
    for (i, k) in P:
        model += s_unload[i, k] >= s_load[i, k] + lpSum(
            x[i, k, j, z] * (inst.T_load[i, j] + inst.T_haul[i, j, z])
            for j in J for z in Z
        )

    # (A5) Прибытие к экскаватору на (k+1) после разгрузки (k) и порожнего хода
    for i in I:
        for k in range(1, Kmax[i]):
            model += a_arr[i, k + 1] >= s_unload[i, k] + \
                     lpSum(b_use(i, k, z) * inst.T_unload[i, z] for z in Z) + \
                     lpSum(q[i, k, j, z] * inst.T_return[i, z, j] for j in J for z in Z)
            # Связки для q: выбранная пара (z пред., j след.) должна существовать
            model += lpSum(q[i, k, j, z] for j in J for z in Z) == y[i, k + 1]
            for z in Z:
                model += lpSum(q[i, k, j, z] for j in J) <= b_use(i, k, z)
            for j in J:
                model += lpSum(q[i, k, j, z] for z in Z) <= a_use(i, k + 1, j)

    # (A6) Погрузка не раньше прибытия (для всех рейсов)
    for (i, k) in P:
        model += s_load[i, k] >= a_arr[i, k]

    # (A7) Последний рейс и возврат до конца смены
    for i in I:
        for k in range(1, Kmax[i] + 1):
            # согласование ell с y и y на следующем k
            model += ell[i, k] <= y[i, k]
            if k < Kmax[i]:
                model += ell[i, k] <= 1 - y[i, k + 1]
                model += ell[i, k] >= y[i, k] - y[i, k + 1]
            else:
                model += ell[i, k] == y[i, k]
            # если это последний рейс, успеваем разгрузиться и вернуться до D_work
            model += s_unload[i, k] + \
                     lpSum(b_use(i, k, z) * (inst.T_unload[i, z] + inst.T_end[i, z]) for z in Z) \
                     <= inst.D_work + Mbig * (1 - ell[i, k])
        # ровно один «последний» при наличии хотя бы одного рейса
        if Kmax[i] >= 1:
            model += lpSum(ell[i, k] for k in range(1, Kmax[i] + 1)) == y[i, 1]

    # --- (A8) Каждый самосвал должен выполнить хотя бы один рейс ---
    # for i in I:
    #     model += lpSum(y[i, k] for k in range(1, Kmax[i] + 1)) >= 1

    # Учёт очередей
    if shovel_queue and len(P) >= 2:
        for j in J:
            for idx_p in range(len(P)):
                for idx_q in range(idx_p + 1, len(P)):
                    p = P[idx_p]
                    q_ = P[idx_q]
                    wvar = w[p, q_, j]

                    #  Связь порядка с временами прибытия (ровно один порядок)
                    #  a_p − a_q ≤ M(1 − w)
                    #  a_q − a_p ≤ M w − eps
                    model += a_arr[p] - a_arr[q_] <= Mbig * (1 - wvar)
                    model += a_arr[q_] - a_arr[p] <= Mbig * wvar - eps

                    xpj = a_use(p[0], p[1], j)
                    xqj = a_use(q_[0], q_[1], j)

                    # Время погрузки от количество грузящихся на время погрузки
                    load_p = lpSum(x[p[0], p[1], j, z] * inst.T_load[p[0], j] for z in Z)
                    load_q = lpSum(x[q_[0], q_[1], j, z] * inst.T_load[q_[0], j] for z in Z)

                    # Если p раньше q (w=1): s_q ≥ s_p + load_p
                    # Если q раньше p (w=0): s_p ≥ s_q + load_q

                    model += s_load[q_] >= s_load[p] + load_p - Mbig * (1 - wvar) - Mbig * (2 - xpj - xqj)
                    model += s_load[p] >= s_load[q_] + load_q - Mbig * wvar - Mbig * (2 - xpj - xqj)

    # ЦЕЛЕВАЯ ФУНКЦИЯ
    # Максимизируем тоннаж
    obj_tons = lpSum(inst.m_tons[i, j] * x[i, k, j, z] for (i, k) in P for j in J for z in Z)
    obj_trips = lpSum(x[i, k, j, z] for (i, k) in P for j in J for z in Z)
    model += obj_tons

    vars_pack = dict(x=x, y=y, s_load=s_load, s_unload=s_unload, a_arr=a_arr,
                     q=q, ell=ell, w=w, Kmax=Kmax, P=P)
    return model, vars_pack


def solve_and_extract(inst: InputPlanningData):
    """Решить модель и получить расписание
    """

    logger.info("Start build model")
    model, V = build_model(inst)
    logger.info("End build model")

    sim_conf = DR.sim_conf()

    if sim_conf["solver"] == "CBC":
        logger.info("CBC")
        cmd = PULP_CBC_CMD(
            msg=sim_conf["msg"],
            timeLimit=sim_conf["time_limit"]
        )

    elif sim_conf["solver"] == "HIGHS":
        logger.info("HIGHS")
        cmd = HiGHS_CMD(
            msg=sim_conf["msg"],
            timeLimit=sim_conf["time_limit"],
            threads=os.cpu_count()
        )

    else:
        raise ValueError(f"Неизвестный солвер: {sim_conf["solver"]}")

    logger.info("Start solve")
    status = model.solve(cmd)
    logger.info("End solve")

    result = {
        "status": LpStatus[model.status],
        "objective": value(model.objective),
        "trips": [],
    }

    # Если решения нет (Infeasible и т.п.), вернём «пусто»
    if LpStatus[model.status] not in ("Optimal", "Optimal_Infeasible", "Not Solved", "Feasible"):
        return result

    # Извлекаем расписание, находим активные рейсы (y=1) и их (j,z)
    x = V["x"]
    y = V["y"]
    sL = V["s_load"]
    sU = V["s_unload"]
    Kmax = V["Kmax"]
    I = inst.truck_ids
    J = inst.shovel_ids
    Z = inst.unload_ids

    for i in I:
        for k in range(1, Kmax[i] + 1):
            if y[i, k].value() is None or y[i, k].value() < 0.5:
                continue
            # выбранные (j, z)
            chosen = [(j, z) for j in J for z in Z if x[i, k, j, z].value() and x[i, k, j, z].value() > 0.5]
            if not chosen:
                continue
            j, z = chosen[0]
            result["trips"].append({
                "truck_id": i,
                "order": k,
                "shovel_id": j,
                "unload_id": z,
                "start_load": int(round(sL[i, k].value() or 0)),
                "start_unload": int(round(sU[i, k].value() or 0)),
                "volume, t": inst.m_tons[i, j],
            })

    # Для удобства — сортировка по самосвалу и номеру рейса
    result["trips"].sort(key=lambda r: (r["truck_id"], r["order"]))
    return result



def build_cp_model(inst: InputPlanningData, use_individual_kmax: bool = True):
    model = cp_model.CpModel()

    I = inst.truck_ids
    J = inst.shovel_ids           # экскаваторы
    Zs = inst.unload_ids          # площадки разгрузки

    # Горизонт (безопасная верхняя граница)
    H = 2 * inst.D_work

    # Индивидуальные горизонты рейсов
    if inst.Kmax_by_truck:
        Kmax_i = dict(inst.Kmax_by_truck)
    else:
        Kmax_i = {i: compute_Kmax_i(inst, i) for i in I}
    if not use_individual_kmax:
        K = max(Kmax_i.values() or [0])
        Kmax_i = {i: K for i in I}

    # Переменные и структуры
    load_itv = {}     # (i,k,j) -> optional interval
    unload_itv = {}   # (i,k,z) -> optional interval
    load_pres = {}    # presence literals
    unload_pres = {}
    s_load = {}
    e_load = {}
    s_unload = {}
    e_unload = {}

    shovel_to_intervals = {j: [] for j in J}
    dump_to_intervals = {z: [] for z in Zs}

    choose_shovel = {}   # (i,k,j) -> Bool
    choose_dump = {}  # (i,k,z) -> Bool

    # Создание интервалов
    for i in I:
        for k in range(1, Kmax_i[i] + 1):
            # Погрузка — выбор экскаватора
            for j in J:
                dur = inst.T_load[i, j]
                pres = model.NewBoolVar(f"pres_load_{i}_{k}_E{j}")
                start = model.NewIntVar(0, H, f"s_load_{i}_{k}_E{j}")
                end   = model.NewIntVar(0, H, f"e_load_{i}_{k}_E{j}")
                itv   = model.NewOptionalIntervalVar(start, dur, end, pres, f"itv_load_{i}_{k}_E{j}")
                load_itv[i, k, j] = itv
                load_pres[i, k, j] = pres
                s_load[i, k, j] = start
                e_load[i, k, j] = end
                shovel_to_intervals[j].append(itv)
                choose_shovel[i, k, j] = pres

            # Разгрузка — выбор площадки
            for z in Zs:
                dur = inst.T_unload[i, z]
                pres = model.NewBoolVar(f"pres_unload_{i}_{k}_Z{z}")
                start = model.NewIntVar(0, H, f"s_unload_{i}_{k}_Z{z}")
                end   = model.NewIntVar(0, H, f"e_unload_{i}_{k}_Z{z}")
                itv   = model.NewOptionalIntervalVar(start, dur, end, pres, f"itv_unload_{i}_{k}_Z{z}")
                unload_itv[i, k, z] = itv
                unload_pres[i, k, z] = pres
                s_unload[i, k, z] = start
                e_unload[i, k, z] = end
                dump_to_intervals[z].append(itv)
                choose_dump[i, k, z] = pres

            # Ровно один экскаватор и ровно одна ПР на рейс k (или рейс отсутствует)
            model.Add(sum(choose_shovel[i, k, j] for j in J) <= 1)
            model.Add(sum(choose_dump[i, k, z] for z in Zs) <= 1)
            # Требуем парность: если есть погрузка, должна быть и разгрузка (и наоборот)
            model.Add(sum(choose_shovel[i, k, j] for j in J) == sum(choose_dump[i, k, z] for z in Zs))

            # Монотонность наличия рейсов: если выбран k, то (k-1) тоже выбран
            if k > 1:
                model.Add(sum(choose_shovel[i, k, j] for j in J) <= sum(choose_shovel[i, k-1, j] for j in J))

    # Очереди: NoOverlap
    for j in J:
        model.AddNoOverlap(shovel_to_intervals[j])
    for z in Zs:
        model.AddNoOverlap(dump_to_intervals[z])

    # Связки «погрузка -> разгрузка -> след. погрузка»
    for i in I:
        for k in range(1, Kmax_i[i] + 1):
            # haul: load(i,k,j) -> unload(i,k,z)
            for j in J:
                for z in Zs:
                    b = model.NewBoolVar(f"pair_{i}_{k}_E{j}_Z{z}")
                    # b активна только когда выбраны и экскаватор, и ПР
                    model.Add(choose_shovel[i, k, j] == 1).OnlyEnforceIf(b)
                    model.Add(choose_dump[i, k, z] == 1).OnlyEnforceIf(b)
                    model.AddBoolOr([choose_shovel[i, k, j].Not(), choose_dump[i, k, z].Not(), b])
                    t_h = inst.T_haul[i, j, z]
                    model.Add(s_unload[i, k, z] >= e_load[i, k, j] + t_h).OnlyEnforceIf(b)

            # return: unload(i,k,z) -> load(i,k+1,j')
            if k < Kmax_i[i]:
                for z in Zs:
                    for j2 in J:
                        b2 = model.NewBoolVar(f"ret_{i}_{k}_Z{z}_E{j2}")
                        model.Add(choose_dump[i, k, z] == 1).OnlyEnforceIf(b2)
                        model.Add(choose_shovel[i, k+1, j2] == 1).OnlyEnforceIf(b2)
                        model.AddBoolOr([choose_dump[i, k, z].Not(), choose_shovel[i, k+1, j2].Not(), b2])
                        t_r = inst.T_return[i, z, j2]
                        model.Add(s_load[i, k+1, j2] >= e_unload[i, k, z] + t_r).OnlyEnforceIf(b2)

            # Начало смены для первой погрузки
            for j in J:
                model.Add(s_load[i, 1, j] >= inst.T_start[i, j]).OnlyEnforceIf(choose_shovel[i, 1, j])
            # Конец смены для любой выбранной разгрузки k
            for z in Zs:
                model.Add(e_unload[i, k, z] + inst.T_end[i, z] <= inst.D_work).OnlyEnforceIf(choose_dump[i, k, z])

    # Целевая функция — суммарные тонны (по выбранным погрузкам)
    terms = []
    for i in I:
        for k in range(1, Kmax_i[i] + 1):
            for j in J:
                ton = int(round(inst.m_tons[i, j]))
                terms.append(ton * choose_shovel[i, k, j])
    model.Maximize(sum(terms))

    # Пакуем ссылки для извлечения результатов
    V = dict(
        choose_shovel=choose_shovel, choose_dump=choose_dump,
        s_load=s_load, s_unload=s_unload,
        Kmax_i=Kmax_i,
    )
    return model, V


def solve_and_extract_cp(inst: InputPlanningData, time_limit: Optional[int] = None, num_workers: int = 16):
    """Решение CP‑SAT и извлечение расписания в прежнем формате."""

    sim_conf = DR.sim_conf()

    if sim_conf["msg"]:
        logger.info("Start builing cp model")
    model, V = build_cp_model(inst, use_individual_kmax=True)

    if sim_conf["msg"]:
        logger.info("End builing cp model")

    solver = cp_model.CpSolver()
    if time_limit is not None:
        solver.parameters.max_time_in_seconds = float(time_limit)
    solver.parameters.num_search_workers = num_workers
    solver.parameters.log_search_progress = sim_conf["msg"]
    solver.parameters.cp_model_presolve = True

    if sim_conf["msg"]:
        logger.info("Start solve")

    status_code = solver.Solve(model)

    if sim_conf["msg"]:
        logger.info("End solve")

    # Маппинг статусов к строкам как в MILP-версии
    status_map = {
        cp_model.OPTIMAL: "Optimal",
        cp_model.FEASIBLE: "Feasible",
        cp_model.INFEASIBLE: "Infeasible",
        cp_model.MODEL_INVALID: "Model Invalid",
        cp_model.UNKNOWN: "Not Solved",
    }
    status_str = status_map.get(status_code, "Not Solved")

    result = {
        "status": status_str,
        "objective": solver.ObjectiveValue() if status_code in (cp_model.OPTIMAL, cp_model.FEASIBLE) else 0.0,
        "trips": [],
    }

    if status_code not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return result

    choose_shovel = V["choose_shovel"]
    choose_dump = V["choose_dump"]
    s_load = V["s_load"]
    s_unload = V["s_unload"]
    Kmax_i = V["Kmax_i"]

    I = inst.truck_ids
    J = inst.shovel_ids
    Zs = inst.unload_ids

    # Извлекаем поездки, сохраняя прежний формат
    for i in I:
        kn = 1  # номер рейса для самосвала i
        for k in range(1, Kmax_i[i] + 1):
            # выбранный экскаватор и ПР (если рейс существует)
            chosen_j = None
            chosen_z = None
            for j in J:
                if solver.BooleanValue(choose_shovel[i, k, j]):
                    chosen_j = j
                    break
            for z in Zs:
                if solver.BooleanValue(choose_dump[i, k, z]):
                    chosen_z = z
                    break
            if chosen_j is None or chosen_z is None:
                # дальше рейсов не будет из-за монотонности
                break

            start_load = solver.Value(s_load[i, k, chosen_j])
            start_unload = solver.Value(s_unload[i, k, chosen_z])
            result["trips"].append({
                "truck_id": i,
                "order": kn,
                "shovel_id": chosen_j,
                "unload_id": chosen_z,
                "start_load": int(start_load),
                "start_unload": int(start_unload),
                "volume, t": inst.m_tons[i, chosen_j],
            })
            kn += 1

    # Сортировка как в исходнике
    result["trips"].sort(key=lambda r: (r["truck_id"], r["order"]))
    return result


def make_example() -> InputPlanningData:
    """ Заполняем исходные данные
    Количество техники, матрица времен выполнение каждой операции (полный перебор)
    """
    N = 5  # Количество самосвалов
    M = 2  # Количество экскаваторов
    Z = 2  # Количество площадок разгрузки (ПР)
    D_work = 12 * 60  # Продолжительность смены в минутах

    # Инициализация словарей параметров времени и объема (в тоннах)
    T_load: Dict[Tuple[int, int], int] = {}  # Время погрузки
    T_unload: Dict[Tuple[int, int], int] = {}  # Время разгрузки
    T_haul: Dict[Tuple[int, int, int], int] = {}  # Время движения груженым
    T_return: Dict[Tuple[int, int, int], int] = {}  # Время движения порожнего
    T_start: Dict[Tuple[int, int], int] = {}  #  Время движения из зонны пересменки к Экскаватору
    T_end: Dict[Tuple[int, int], int] = {}  #  Время движения с Экскаватора до зоны пересменки
    m_tons: Dict[Tuple[int, int], float] = {}  #  Количесво загружаемых тонн

    # Данные должны рассчитываться для каждого i-ого самосвала, j-ого экскаватора , z-ой ПР
    # на основании их параметров (как в симуляции сейчас)
    # T_load[i,j] - время погрузки (несколько ковшей, от момента Э зачерпнул до момента выкинул последний ковш в самосвал) i-ого самосвала у  j-ого экскаватора
    # T_start[i,j] - время на движение от площадки пересменки для i-ого самосвала  к j-ому экскаватору
    # m_tons[i,j] - количество тонн загруженных в i-ый самосвала на j-ом экскаваторе за один рейс
    # T_unload[i,z] - время разгрузки у z-ой ПР
    # T_haul[i,j,z] - время, которое i-ый самосвала выгружается у z-ой ПР
    # T_end[i,z] - время, которое i-ый самосвала едет от z-ой ПР к площадке пересменки
    # T_return[i,z,j] - время, которое i-ый самосвала едет от z-ой ПР к j-ому экскаватора

    # Здесь заполнение каким-то данными
    for i in range(1, N + 1):
        for j in range(1, M + 1):
            T_load[i, j] = 10 + 2 * (j - 1)
            T_start[i, j] = 15 + 3 * (i - 1)
            m_tons[i, j] = 180
        for z in range(1, Z + 1):
            T_unload[i, z] = 8 + (z - 1)
            T_end[i, z] = 20 + 5 * (z - 1)
        for j in range(1, M + 1):
            for z in range(1, Z + 1):
                T_haul[i, j, z] = 25 + 5 * (z - 1) + 3 * (i - 1)
                T_return[i, z, j] = 22 + 4 * (j - 1) + 2 * (i - 1)

    return InputPlanningData(
        N=N, M=M, Z=Z, D_work=D_work,
        T_haul=T_haul, T_return=T_return, T_load=T_load,
        T_unload=T_unload, T_start=T_start, T_end=T_end,
        m_tons=m_tons,
    )


def dummy_func():
    return 0


def get_planning_data(simdata: SimData) -> InputPlanningData:
    """
    Метод набивающий матрицу данных
    """
    truck_count = len(simdata.trucks)
    shovel_count = len(simdata.shovels)
    unl_count = len(simdata.unloads)
    shift_change_area = simdata.idle_areas.shift_change_areas[0]

    planning_data = InputPlanningData(
        N=truck_count,
        M=shovel_count,
        Z=unl_count,
        D_work=int(simdata.duration/60),

        T_haul=dict(),
        T_return=dict(),
        T_load=dict(),
        T_unload=dict(),
        T_start=dict(),
        T_end=dict(),
        m_tons=dict(),

        Kmax_by_truck=None
    )

    # Идем по самосвалам
    for truck in simdata.trucks.values():

        # Идем по экскаваторам
        for shovel in simdata.shovels.values():
            time_load, weight, _ = ShovelCalc.calculate_load_cycles(shovel.properties, truck.properties)

            planning_data.T_load[
                truck.id,
                shovel.id
            ] = int(time_load/60)

            if truck.initial_edge_id and truck.initial_lat and truck.initial_lon:
                start_route = build_route_edges_by_road_net_from_position(
                    lon=truck.initial_lon,
                    lat=truck.initial_lat,
                    edge_idx=truck.initial_edge_id,
                    height=None,
                    to_object_id=shovel.id,
                    to_object_type=ObjectType.SHOVEL,
                    road_net=simdata.road_net,
                )

            else:
                start_route = build_route_edges_by_road_net(
                    from_object_id=shift_change_area.id,
                    from_object_type=ObjectType.IDLE_AREA,
                    to_object_id=shovel.id,
                    to_object_type=ObjectType.SHOVEL,
                    road_net=simdata.road_net
                )

            planning_data.T_start[
                truck.id,
                shovel.id
            ] = int(TruckCalc.calculate_time_motion_by_edges(
                start_route,
                truck.properties,
                forward=True
            )/60)

            planning_data.m_tons[
                truck.id,
                shovel.id
            ] = int(weight)

            # Идем по пунктам разгрузки
            for unload in simdata.unloads.values():

                route = build_route_edges_by_road_net(
                    from_object_id=shovel.id,
                    from_object_type=ObjectType.SHOVEL,
                    to_object_id=unload.id,
                    to_object_type=ObjectType.UNLOAD,
                    road_net=simdata.road_net
                )
                planning_data.T_haul[
                    truck.id,
                    shovel.id,
                    unload.id
                ] = int(TruckCalc.calculate_time_motion_by_edges(
                    route,
                    truck.properties,
                    forward=True
                )/60)

                planning_data.T_return[
                    truck.id,
                    unload.id,
                    shovel.id
                ] = int(TruckCalc.calculate_time_motion_by_edges(
                    route,
                    truck.properties,
                    forward=False
                )/60)

        # Идем по пунктам разгрузки
        for unload in simdata.unloads.values():

            planning_data.T_unload[
                truck.id,
                unload.id
            ] = int(UnloadCalc.unload_calculation_by_norm(unload.properties, truck.properties)["t_total"]/60)

            end_route = build_route_edges_by_road_net(
                from_object_id=unload.id,
                from_object_type=ObjectType.UNLOAD,
                to_object_id=shift_change_area.id,
                to_object_type=ObjectType.IDLE_AREA,
                road_net=simdata.road_net
            )

            planning_data.T_end[
                truck.id,
                unload.id
            ] = int(TruckCalc.calculate_time_motion_by_edges(
                end_route,
                truck.properties,
                forward=True
            )/60)

    return planning_data


def run_planning(simdata: SimData):
    sim_conf = DR.sim_conf()
    planning_data = get_planning_data(simdata)
    # planning_data = make_example()

    if sim_conf["msg"]:
        logger.info(planning_data)

    out = solve_and_extract_cp(planning_data, time_limit=sim_conf["time_limit"])

    if sim_conf["msg"]:
        for trip in out["trips"]:
            if trip["order"] == 1:
                logger.info("-------------------------")
            logger.info(f"Самосвал: {trip["truck_id"]}; Экскаватор: {trip["shovel_id"]}; ПР: {trip["unload_id"]}; Рейс № {trip["order"]}")
    return out


def run_planning_trips(
        sim_data: SimData,
        exclude_objects: dict[str, list[int]],
) -> dict:

    sim_data.duration = int((sim_data.end_time - sim_data.start_time).total_seconds())

    exclude_trucks = exclude_objects["trucks"]
    exclude_shovels = exclude_objects["shovels"]
    exclude_unloads = exclude_objects["unloads"]

    for truck_id in exclude_trucks:
        sim_data.trucks.pop(truck_id, None)

    for shovel_id in exclude_shovels:
        sim_data.shovels.pop(shovel_id, None)

    for unload_id in exclude_unloads:
        sim_data.unloads.pop(unload_id, None)

    if not sim_data.shovels or not sim_data.unloads or not sim_data.trucks:
        return {}

    result = run_planning(simdata=sim_data)
    planned_trips = defaultdict(list)

    for trip in result["trips"]:
        planned_trip = PlannedTrip(
            truck_id=trip["truck_id"],
            shovel_id=trip["shovel_id"],
            unload_id=trip["unload_id"],
            order=trip["order"]
        )
        planned_trips[planned_trip.truck_id].append(planned_trip)
    return planned_trips
