import math


class TrucksNeededCalculator:
    """
        Калькулятор для расчёта требуемого количество самосвалов для достижения указанной целевой загрузки экскаваторов
    """
    T_rot = 15  # Продолжительность маневра в секундах

    @staticmethod
    def _erlang_c(lam, mu, c):
        """
        M/M/c
        Формулы:
          a = λ/μ,
          P(wait) = [ (a^c / c!) * (c / (c - a)) ] / [ sum_{k=0}^{c-1} a^k/k! + (a^c / c!) * (c / (c - a)) ],  ρ = λ/(c μ) < 1
        Возвращает P(wait)
        """
        a = lam / mu
        rho = lam / (c * mu)
        if rho >= 1:
            return 1.0
        # sum_{k=0}^{c-1} a^k/k!
        sum0 = 0.0
        term = 1.0  # a^0/0!
        for k in range(c):
            if k > 0:
                term *= a / k
            sum0 += term
        termc = (a ** c) / math.factorial(c) * (c / (c - a))
        Pw = termc / (sum0 + termc)
        return Pw

    @classmethod
    def _Wq_allen_cunneen(cls, lam, mu, c, ca2, cs2):
        """
        Поправка Аллена–Куннена для G/G/c
        Формулы:
          Wq^(M/M/c) = P(wait) / (c μ - λ)
          Wq^(G/G/c) ≈ ((c_a^2 + c_s^2)/2) * Wq^(M/M/c)
        """
        rho = lam / (c * mu)
        if rho >= 1:
            return float('inf')
        Pw = cls._erlang_c(lam, mu, c)
        Wq_mm = Pw / (c * mu - lam)
        return 0.5 * (ca2 + cs2) * Wq_mm

    @classmethod
    def _trucks_needed(
            cls,
            u_star: float,
            M: int,
            Z: int,

            T_load: float,
            T_unload: float,
            T_haul: float,
            T_return: float,

            cs2_load: float,
            cs2_unload: float,
            ca2_load: float,
            ca2_unload: float,

            Dur_work: float,
            Dur_rep: float,
            Dur_idle: float,
            Dur_blast: float,
            Dur_lunch: float,
    ):
        """
        Итоговая формула N = λ * T_cycle.
        где
          μ_load = 1/T_load,  μ_unload = 1/T_unload
          λ = u* * M * μ_load
          Wq_load аппроксимация для G (Allen-Cunnen)
          Wq_unload аппроксимация для G (Allen-Cunnen)
          T_cycle = T_haul + T_return + T_load + T_unload + Wq_load + Wq_unload
          N = λ * T_cycle
        """
        mu_load = 1.0 / T_load
        mu_unld = 1.0 / T_unload
        u_star2 = 1 - (Dur_rep + Dur_idle + Dur_blast + Dur_lunch) / (Dur_work * M)
        lam = u_star * u_star2 * M * mu_load

        Wq_load = cls._Wq_allen_cunneen(lam, mu_load, M, ca2_load, cs2_load)
        Wq_unld = cls._Wq_allen_cunneen(lam, mu_unld, Z, ca2_unload, cs2_unload)

        T_cycle = T_haul + T_return + T_load + T_unload + Wq_load + Wq_unld + cls.T_rot
        N = lam * T_cycle
        return {
            "lambda": lam,
            "Wq_load": Wq_load,
            "Wq_unload": Wq_unld,
            "T_cycle": T_cycle,
            "N_required": N
        }

    @classmethod
    def calculate_trucks_needed(
        cls,
        target_shovels_utilization : float,
        duration: float,

        shovels_quantity: int,
        unloads_quantity: int,

        mean_load_duration: float,
        variance_load_duration: float,
        mean_unload_duration: float,
        variance_unload_duration: float,

        mean_moving_loaded_duration: float,
        mean_moving_empty_duration: float,

        mean_shovels_waiting_trucks_duration: float,
        variance_shovels_waiting_trucks_duration: float,
        mean_unloads_waiting_trucks_duration: float,
        variance_unloads_waiting_trucks_duration: float,

        shovels_repair_duration: float,
        shovels_planned_idle_duration: float,
        shovels_blast_waiting_duration: float,
        shovels_lunches_duration: float,
    ) -> int | None:
        """
            Производит расчёт требуемого количество самосвалов для достижения указанной целевой загрузки экскаваторов.

            u_start - целевая загрузка экскаваторов
            duration - промежуток времени, для которого производится расчёт

            shovels_quantity - количество экскаваторов
            unloads_quantity - количество пунктов разгрузки

            mean_load_duration - среднее время погрузки
            variance_load_duration - разброс (дисперсия) времени погрузки
            mean_unload_duration - среднее время разгрузки
            variance_unload_duration - разброс (дисперсия) времени разгрузки

            mean_moving_loaded_duration - среднее время движения гружёным
            mean_moving_empty_duration - среднее время движения порожним

            mean_shovels_waiting_trucks_duration - среднее время ожидания экскаватором приезда самосвала
            variance_shovels_waiting_trucks_duration - разброс (дисперсия) времени ожидания экскаватором приезда самосвала
            mean_unloads_waiting_trucks_duration - среднее время ожидания пунктом разгрузки приезда самосвала
            variance_unloads_waiting_trucks_duration - разброс (дисперсия) времени ожидания пунктом разгрузки приезда самосвала

            shovels_repair_duration: - общее время экскаватора, проведённое в ремонтах
            shovels_planned_idle_duration - общее время экскаватора, проведённое в запланированных простоях
            shovels_blast_waiting_duration - общее время экскаватора, проведённое в ожидании взрывных работ
            shovels_lunches_duration - общее время экскаватора, проведённое в обеденных перерывах

            Результат: количество самосвалов, достаточное для требуемой загрузки экскаваторов
        """

        # mu = T.среднее()
        # s2 = T.дисперсия()
        # s2 / (mu * mu)
        cs2_load = variance_load_duration / (mean_load_duration ** 2)
        cs2_unload = variance_unload_duration / (mean_unload_duration ** 2)
        ca2_load = variance_shovels_waiting_trucks_duration / (mean_shovels_waiting_trucks_duration ** 2)
        ca2_unload = variance_unloads_waiting_trucks_duration / (mean_unloads_waiting_trucks_duration ** 2)

        result = cls._trucks_needed(
            u_star=target_shovels_utilization,
            M=shovels_quantity,
            Z=unloads_quantity,

            T_load=mean_load_duration,
            T_unload=mean_unload_duration,
            T_haul=mean_moving_loaded_duration,
            T_return=mean_moving_empty_duration,

            cs2_load=cs2_load,
            cs2_unload=cs2_unload,
            ca2_load=ca2_load,
            ca2_unload=ca2_unload,

            Dur_work=duration,
            Dur_rep=shovels_repair_duration,
            Dur_idle=shovels_planned_idle_duration,
            Dur_blast=shovels_blast_waiting_duration,
            Dur_lunch=shovels_lunches_duration,
        )
        return result.get('N_required', None)
