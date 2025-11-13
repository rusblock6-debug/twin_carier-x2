import logging
from math import floor
from typing import Dict, List, Tuple

from pulp import (
    LpProblem, LpMaximize, LpVariable, LpBinary, LpInteger, lpSum, LpStatus, value, PULP_CBC_CMD, HiGHS_CMD, )

from app.sim_engine.core.planner.entities import InputPlanningData
from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver as DR
from app.sim_engine.enums import SolverType

logger = logging.getLogger(__name__)


class MILPSolver:
    solver_type: SolverType
    msg_out: bool
    time_limit: int
    workers: int

    @staticmethod
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

    @classmethod
    def default_Kmax(cls, inst: InputPlanningData) -> Dict[int, int]:
        """Если Kmax не задан, вычислить его для каждого самосвала"""
        return {i: cls.compute_Kmax_i(inst, i) for i in inst.truck_ids}

    @classmethod
    def build_model(cls, inst: InputPlanningData, shovel_queue: bool = True):
        """Собираем все ограничения и условия поиска решения"""
        I = inst.truck_ids
        J = inst.shovel_ids
        Z = inst.unload_ids

        # Верхние границы числа рейсов по самосвалам
        Kmax = inst.Kmax_by_truck or cls.default_Kmax(inst)

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

    @classmethod
    def run(cls, inst: InputPlanningData):
        """Решить модель и получить расписание
        """

        if cls.msg_out:
            logger.info("Start builing model")

        model, V = cls.build_model(inst)

        if cls.msg_out:
            logger.info("End builing model")

        if cls.solver_type == SolverType.CBC:
            logger.info(SolverType.CBC.key())
            cmd = PULP_CBC_CMD(
                msg=cls.msg_out,
                timeLimit=cls.time_limit
            )

        elif cls.solver_type == SolverType.HIGHS:
            logger.info(SolverType.HIGHS.key())
            cmd = HiGHS_CMD(
                msg=cls.msg_out,
                timeLimit=cls.time_limit,
                threads=cls.workers,
            )

        else:
            sim_conf = DR.sim_conf()
            raise ValueError(f"Неизвестный солвер: {sim_conf["solver"]}")

        if cls.msg_out:
            logger.info("Start solve")

        status = model.solve(cmd)

        if cls.msg_out:
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
