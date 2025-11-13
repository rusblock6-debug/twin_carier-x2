import random
from datetime import datetime


class BreakdownCalc:
    """Расчеты Поломок/Восстановлений"""

    def __init__(self, seeded_random: random.Random):
        self.seeded_random = seeded_random

    def _calculate_rates(
            self, **kwargs
    ):
        T_A = kwargs["initial_operating_time"]
        MTTR = kwargs["average_repair_duration"]
        N_F = kwargs["initial_failure_count"]

        MTBF = T_A / N_F  # Среднее время между отказами
        failure_rate = 1 / MTBF  # Интенсивность отказов λ
        repair_rate = 1 / MTTR  # Параметр экспоненциального закона восстановления

        return {
            "failure_rate": failure_rate,
            "repair_rate": repair_rate,
        }

    def calculate_failure_time(self, **kwargs):
        """
        Время не секунд семуляции, а секунд работы актора
        самосвал: работа - движение груженым, движение порожним, разгрузка
        экскаватор: работа - погрузка
        ПР: во время разгрузки
        """
        rates = self._calculate_rates(**kwargs)
        return self.seeded_random.expovariate(rates["failure_rate"])

    def calculate_repair_time(self, **kwargs):
        rates = self._calculate_rates(**kwargs)
        return self.seeded_random.expovariate(rates["repair_rate"])


class FuelCalc:

    @staticmethod
    def calculate_fuel_level_while_moving(fuel_lvl, sfc, density, p_engine):
        fuel_rate = ((sfc / (1000 * density)) * p_engine) / 3600
        fuel_lvl -= fuel_rate
        return fuel_lvl

    @staticmethod
    def calculate_fuel_level_while_idle(fuel_lvl, fuel_idle_lph):
        fuel_rate = fuel_idle_lph / 3600
        fuel_lvl -= fuel_rate
        return fuel_lvl


class LunchCalc:
    """Расчёты времён обеденных перерывов"""

    @staticmethod
    def calculate_lunch_times(
            sim_start_time: datetime,
            lunch_times: list[tuple[datetime, datetime]]
    ) -> list[tuple[int, int]]:
        """Рассчитываем моменты начала и конца обеденных перерывов относительно времени симуляции"""
        result = []

        for lunch_start, lunch_end in lunch_times:
            if lunch_start <= sim_start_time <= lunch_end:
                end_time = (lunch_end-sim_start_time).total_seconds()
                result.append(
                    (0, end_time)
                )
            if sim_start_time < lunch_start < lunch_end:
                result.append(
                    (
                        (lunch_start - sim_start_time).total_seconds(),
                        (lunch_end - sim_start_time).total_seconds(),
                    )
                )
        return result
