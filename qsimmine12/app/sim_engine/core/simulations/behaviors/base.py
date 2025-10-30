from abc import ABC
from typing import List, Any

from app.sim_engine.core.calculations.base import BreakdownCalc, FuelCalc, LunchCalc
from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver as DR
from app.sim_engine.enums import ObjectType
from app.sim_engine.events import EventType
from app.sim_engine.states import TruckState, ExcState


class BaseBehavior(ABC):
    """
    Абстрактный базовый класс для всех поведений в симуляции.
    Определяет общий интерфейс и шаблоны выполнения.
    """

    def __init__(self, target: Any, props: Any = None):
        env = DR.env()
        self.env = env
        self.target = target
        self.props = props
        self.process = env.process(self.run())

    def run(self):
        """Основной цикл выполнения поведения"""
        yield self.env.timeout(0)


class BaseTickBehavior:
    """
    Класс определяющий базовую последовательность в логике расчетов каждый тик(фрейм)
    Этапы:
    1. Расчеты для состояния актора. Метод state_process
    2. Упаковка телеметрии. Метод telemetry_process
    """

    def __init__(self, target):
        env = DR.env()
        self.env = env
        self.target = target
        self.process = env.process(self.run())

    def run(self):
        while True:
            if hasattr(self.target, "main_tic_process"):
                self.target.main_tic_process()
            if hasattr(self.target, "telemetry_process"):
                self.target.telemetry_process()
            yield self.env.timeout(self.target.tick)


class BreakdownBehavior(BaseBehavior):
    """
    Класс вычисляющий Поломки/Восстановления
    """

    def __init__(self, target, props):
        self.calc = BreakdownCalc(target.quarry.seeded_random)
        super().__init__(target, props)

    def run(self):

        input_data = {
            "initial_operating_time": self.props.initial_operating_time * 60 * 60,
            "average_repair_duration": self.props.average_repair_duration * 60,
            "initial_failure_count": self.props.initial_failure_count
        }

        while True:
            # Вычисляем время поломки, ждем, переходим в поломку
            time_to_failure = self.calc.calculate_failure_time(**input_data)
            time_to_failure = int(time_to_failure)

            while time_to_failure != 0:
                if self.target.state.is_work:
                    time_to_failure -= 1
                yield self.env.timeout(1)

            self.target.broken = True
            self.target.push_event(event_type=EventType.BREAKDOWN_BEGIN)
            input_data["initial_failure_count"] += 1
            input_data["initial_operating_time"] += time_to_failure

            # Вычисляем время починки, ждем, переходим в починку
            time_to_repair = self.calc.calculate_repair_time(**input_data)
            yield self.env.timeout(time_to_repair)
            self.target.broken = False
            self.target.push_event(event_type=EventType.BREAKDOWN_END)


class FuelBehavior(BaseBehavior):
    """
    Класс Управляющий топливом
    """

    def __init__(self, target, props):
        self.calc = FuelCalc()
        super().__init__(target, props)

    def run(self):

        while True:
            if self.target.state.is_moving:
                self.target.fuel = self.calc.calculate_fuel_level_while_moving(
                    fuel_lvl=self.target.fuel,
                    sfc=self.target.properties.fuel_specific_consumption,
                    density=self.target.properties.fuel_density,
                    p_engine=self.target.properties.engine_power_kw,
                )
            else:
                self.target.fuel = self.calc.calculate_fuel_level_while_idle(
                    fuel_lvl=self.target.fuel,
                    fuel_idle_lph=self.target.properties.fuel_idle_lph
                )

            if self.target.fuel < self.target.properties.fuel_threshold_planned:
                self.target.fuel_empty = True

            yield self.env.timeout(1)


class LunchBehavior(BaseBehavior):
    """ Класс для техники, управляющий отслеживанием обедов и запуском обеденного простоя"""

    def __init__(self, target):
        self.calc = LunchCalc()
        super().__init__(target)

    def run(self):
        lunch_start_times: List[tuple[int, int]] = self.calc.calculate_lunch_times(
            sim_start_time=self.target.start_time,
            lunch_times=self.target.quarry.sim_data.lunch_times
        )

        while lunch_start_times:
            # Ждём ближайшего обеда
            nearest_lunch_start, nearest_lunch_end = lunch_start_times.pop(0)
            time_to_lunch: int = nearest_lunch_start - self.env.now
            yield self.env.timeout(time_to_lunch)

            # Обед начался, отслеживаем его до конца
            while self.env.now < nearest_lunch_end:
                # если объект в рабочем состоянии - отправляем на обед
                if self.target.state.is_work and not self.target.at_lunch:
                    self.target.at_lunch = True
                    self.target.push_event(event_type=EventType.LUNCH_BEGIN)
                    lunch_time_remaining: int = nearest_lunch_end - self.env.now
                    yield self.env.timeout(lunch_time_remaining)
                else:
                    # если не в рабочем, просто ждём
                    yield self.env.timeout(1)

            # Обед закончился
            if self.target.at_lunch:
                # Если объект находился в обеде - заканчиваем обед
                self.target.at_lunch = False
                self.target.push_event(event_type=EventType.LUNCH_END)


class PlannedIdleBehavior(BaseBehavior):
    """ Класс для техники, управляющий отслеживанием и запуском запланированных простоев"""

    def __init__(self, target, object_type: ObjectType):
        self.object_type = object_type
        super().__init__(target)

    def _calculate_idles_times(self, target) -> list[tuple[int, int]]:
        """Собирает из данных о плановых простоях список периодов простоев"""

        # поиск происходит в словаре, где ключи вида ('shovel', 3) - нам нужен строковый ключ
        key = (self.object_type.key(), target.id)

        idles_times = []
        for idle in target.quarry.sim_data.planned_idles.get(key, []):
            start_time = (idle.start_time - target.start_time).total_seconds()
            end_time = (idle.end_time - target.start_time).total_seconds()
            idles_times.append(
                (start_time, end_time)
            )
        return idles_times

    def _should_start_planned_idle(self) -> bool:
        """Проверка возможности начать плановый простой"""
        if not self.target.at_planned_idle:
            if self.object_type == ObjectType.TRUCK and self.target.state in [TruckState.MOVING_EMPTY,
                                                                              TruckState.WAITING]:
                return True
            if self.object_type == ObjectType.SHOVEL and self.target.state in [ExcState.WAITING]:
                return True
        return False

    def run(self):
        planned_idles: list[tuple[int, int]] = self._calculate_idles_times(self.target)

        while planned_idles:
            nearest_idle_start, nearest_idle_end = planned_idles.pop(0)

            wait_time = nearest_idle_start - self.env.now
            yield self.env.timeout(wait_time)

            while self.env.now < nearest_idle_end:
                # Если можем отправить в простой - отправляем
                if self._should_start_planned_idle():
                    self.target.at_planned_idle = True
                    self.target.push_event(event_type=EventType.PLANNED_IDLE_BEGIN)

                    idle_time_remaining: int = nearest_idle_end - self.env.now
                    yield self.env.timeout(idle_time_remaining)
                else:
                    # если не в рабочем, просто ждём
                    yield self.env.timeout(1)

            # Простой закончился
            if self.target.at_planned_idle:
                # Если объект находился в простое - заканчиваем простой
                self.target.at_planned_idle = False
                self.target.push_event(event_type=EventType.PLANNED_IDLE_END)
