SIM_CONFIG = {
    "breakdown": True,
    "refuel": True,
    "lunch": True,
    "planned_idle": True,
    "blasting": True,
    "mode": "manual",  # auto/manual

    # Настройки солвера
    "time_limit": 10,  # SolverType: CBC,HIGHS,CP
    "msg": True,  # SolverType: GREEDY,CBC,HIGHS,CP
    "workers": 16,  # SolverType: CBC,HIGHS,CP

    # Настройки расчёта достоверного результата
    "reliability_calc_enabled": False,
    "rel_process_num": None,  # Кол-во параллельных процессов (None - авто)
    "rel_init_runs_num": 15,
    "rel_step_runs_num": 15,
    "rel_max_runs_num": 30,
    "rel_alpha": 0.05,
    "rel_r_target": 0.05,
    "rel_delta_target": 0.01,
    "rel_consecutive": 2,
    "rel_boot_b": 5000,
}
