import logging

from math import floor
from ortools.sat.python import cp_model

from app.sim_engine.core.planner.entities import InputPlanningData

logger = logging.getLogger(__name__)


class CPSolver:
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
    def build_cp_model(cls, inst: InputPlanningData, use_individual_kmax: bool = True):
        model = cp_model.CpModel()

        I = inst.truck_ids
        J = inst.shovel_ids  # экскаваторы
        Zs = inst.unload_ids  # площадки разгрузки

        # Горизонт (безопасная верхняя граница)
        H = 2 * inst.D_work

        # Индивидуальные горизонты рейсов
        if inst.Kmax_by_truck:
            Kmax_i = dict(inst.Kmax_by_truck)
        else:
            Kmax_i = {i: cls.compute_Kmax_i(inst, i) for i in I}
        if not use_individual_kmax:
            K = max(Kmax_i.values() or [0])
            Kmax_i = {i: K for i in I}

        # Переменные и структуры
        load_itv = {}  # (i,k,j) -> optional interval
        unload_itv = {}  # (i,k,z) -> optional interval
        load_pres = {}  # presence literals
        unload_pres = {}
        s_load = {}
        e_load = {}
        s_unload = {}
        e_unload = {}

        shovel_to_intervals = {j: [] for j in J}
        dump_to_intervals = {z: [] for z in Zs}

        choose_shovel = {}  # (i,k,j) -> Bool
        choose_dump = {}  # (i,k,z) -> Bool

        # Создание интервалов
        for i in I:
            for k in range(1, Kmax_i[i] + 1):
                # Погрузка — выбор экскаватора
                for j in J:
                    dur = inst.T_load[i, j]
                    pres = model.NewBoolVar(f"pres_load_{i}_{k}_E{j}")
                    start = model.NewIntVar(0, H, f"s_load_{i}_{k}_E{j}")
                    end = model.NewIntVar(0, H, f"e_load_{i}_{k}_E{j}")
                    itv = model.NewOptionalIntervalVar(start, dur, end, pres, f"itv_load_{i}_{k}_E{j}")
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
                    end = model.NewIntVar(0, H, f"e_unload_{i}_{k}_Z{z}")
                    itv = model.NewOptionalIntervalVar(start, dur, end, pres, f"itv_unload_{i}_{k}_Z{z}")
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
                    model.Add(sum(choose_shovel[i, k, j] for j in J) <= sum(choose_shovel[i, k - 1, j] for j in J))

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
                            model.Add(choose_shovel[i, k + 1, j2] == 1).OnlyEnforceIf(b2)
                            model.AddBoolOr([choose_dump[i, k, z].Not(), choose_shovel[i, k + 1, j2].Not(), b2])
                            t_r = inst.T_return[i, z, j2]
                            model.Add(s_load[i, k + 1, j2] >= e_unload[i, k, z] + t_r).OnlyEnforceIf(b2)

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

    @classmethod
    def run(cls, inst: InputPlanningData):
        """Решение CP‑SAT и извлечение расписания в прежнем формате."""

        if cls.msg_out:
            logger.info("Start builing cp model")
        model, V = cls.build_cp_model(inst, use_individual_kmax=True)

        if cls.msg_out:
            logger.info("End builing cp model")

        solver = cp_model.CpSolver()
        if cls.time_limit is not None:
            solver.parameters.max_time_in_seconds = float(cls.time_limit)
        solver.parameters.num_search_workers = cls.workers
        solver.parameters.log_search_progress = cls.msg_out
        solver.parameters.cp_model_presolve = True

        if cls.msg_out:
            logger.info("Start solve")

        status_code = solver.Solve(model)

        if cls.msg_out:
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
