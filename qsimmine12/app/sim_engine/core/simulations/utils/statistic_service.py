import logging
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Union, Optional, Dict

from app.sim_engine.core.calculations.trucks_needed import TrucksNeededCalculator
from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver as DR
from app.sim_engine.core.simulations.utils.helpers import sim_duration
from app.sim_engine.states import TruckState, ExcState, UnloadState

logger = logging.getLogger(__name__)


# region Statistics data classes
@dataclass
class UnloadStatistics:
    """Статистические данные по пунктам разгрузки"""
    unload_durations: List[float | int] = field(default_factory=list)
    """Длительности разгрузок"""
    truck_arrival_waiting_durations: List[float | int] = field(default_factory=list)
    """Длительности ожидания приезда самосвалов"""


@dataclass
class TruckStatistics:
    """Статистические данные по самосвалам"""
    moving_loaded_duration: List[float | int] = field(default_factory=list)
    """Длительности движения гружёным"""
    moving_empty_duration: List[float | int] = field(default_factory=list)
    """Длительности движения порожним"""


@dataclass
class TotalShovelStatistics:
    """Суммируемые статистические показатели экскаваторов"""
    repairs_duration: int | float = 0
    """Общее количество времени, проведённого в ремонтах"""
    planned_idles_duration: int | float = 0
    """Общее количество времени, проведённого в плановых простоях"""
    blast_waiting_duration: int | float = 0
    """Общее количество времени, проведённого в ожидании проведения взрывных работ"""
    lunches_duration: int | float = 0
    """Общее количество времени, проведённого в обеденных перерывах"""


@dataclass
class ShovelStatistics:
    """Статистические данные по экскаваторам"""
    load_durations: List[float | int] = field(default_factory=list)
    """Длительности погрузок"""
    truck_arrival_waiting_durations: List[float | int] = field(default_factory=list)
    """Длительности ожидания приезда самосвалов"""
    totals: TotalShovelStatistics = field(default_factory=TotalShovelStatistics)
    """Суммируемые статистические данные по экскаваторам"""


# endregion


# region Tracking data classes
@dataclass
class TruckTrackingData:
    """Данные для отслеживания текущего состояния самосвала"""
    cur_state: TruckState
    duration: float = 0


@dataclass
class ShovelTrackingData:
    """Данные для отслеживания текущего состояния экскаватора"""
    cur_state: ExcState
    duration: float = 0
    current_truck: Optional[int] = None


@dataclass
class UnloadTrackingData:
    """Данные для отслеживания текущего состояния пункта разгрузки"""
    cur_state: UnloadState
    duration: float = 0
    current_truck: Optional[int] = None


@dataclass
class StateTrackingContainer:
    """Контейнер данных для отслеживания состояний сущностей симуляции"""
    trucks: Dict[int, TruckTrackingData] = field(default_factory=dict)
    shovels: Dict[int, ShovelTrackingData] = field(default_factory=dict)
    unloads: Dict[int, UnloadTrackingData] = field(default_factory=dict)


# endregion


# region Shovel State handlers
class ShovelStateHandler(ABC):
    """Абстрактный обработчик состояния экскаватора."""

    @abstractmethod
    def on_enter(
            self,
            tracking_data: ShovelTrackingData,
            duration: float,
            loading_truck_id: int | None,
            loading_truck_state: TruckState | None,
            statistics: ShovelStatistics,
    ):
        """Вызывается при входе в новое состояние"""
        pass

    @abstractmethod
    def on_exit(
            self,
            tracking_data: ShovelTrackingData,
            new_state: ExcState,
            loading_truck_id: int | None,
            loading_truck_state: TruckState | None,
            statistics: ShovelStatistics,
    ):
        """Вызывается при выходе из текущего состояния"""
        pass

    @abstractmethod
    def on_update(
            self,
            tracking_data: ShovelTrackingData,
            duration: float,
            loading_truck_id: int | None,
            loading_truck_state: TruckState | None,
            statistics: ShovelStatistics,
    ):
        """Вызывается при обновлении текущего состояния"""
        pass


class WaitingStateHandler(ShovelStateHandler):
    """Обработчик состояния ожидания экскаватора"""

    def on_enter(
            self,
            tracking_data: ShovelTrackingData,
            duration: float,
            loading_truck_id: int | None,
            loading_truck_state: TruckState | None,
            statistics: ShovelStatistics,
    ):
        # Начинаем накапливать длительность ожидания
        tracking_data.duration += duration

    def on_exit(
            self,
            tracking_data: ShovelTrackingData,
            new_state: ExcState,
            loading_truck_id: int | None,
            loading_truck_state: TruckState | None,
            statistics: ShovelStatistics,
    ):
        # При выходе из ожидания фиксируем общую длительность
        statistics.truck_arrival_waiting_durations.append(tracking_data.duration)
        tracking_data.duration = 0

    def on_update(
            self,
            tracking_data: ShovelTrackingData,
            duration: float,
            loading_truck_id: int | None,
            loading_truck_state: TruckState | None,
            statistics: ShovelStatistics,
    ):
        # Продолжаем накапливать длительность ожидания
        tracking_data.duration += duration


class LoadingStateHandler(ShovelStateHandler):
    """Обработчик состояния погрузки экскаватора"""

    def on_enter(
            self,
            tracking_data: ShovelTrackingData,
            duration: float,
            loading_truck_id: int | None,
            loading_truck_state: TruckState | None,
            statistics: ShovelStatistics,
    ):
        # Начинаем новую погрузку
        tracking_data.duration += duration
        tracking_data.current_truck = loading_truck_id

    def on_exit(
            self,
            tracking_data: ShovelTrackingData,
            new_state: ExcState,
            loading_truck_id: int | None,
            loading_truck_state: TruckState | None,
            statistics: ShovelStatistics,
    ):
        # При выходе из погрузки фиксируем длительность, если не перешли в ремонт
        if new_state != ExcState.REPAIR:
            statistics.load_durations.append(tracking_data.duration)
            tracking_data.duration = 0
            tracking_data.current_truck = None
        elif new_state == ExcState.REPAIR and not loading_truck_id:
            # Если перешли в ремонт без самосвала, тоже фиксируем погрузку
            statistics.load_durations.append(tracking_data.duration)
            tracking_data.duration = 0
            tracking_data.current_truck = None

    def on_update(
            self,
            tracking_data: ShovelTrackingData,
            duration: float,
            loading_truck_id: int | None,
            loading_truck_state: TruckState | None,
            statistics: ShovelStatistics,
    ):
        current_truck_id = tracking_data.current_truck

        # Если сменился самосвал во время погрузки, фиксируем предыдущую погрузку
        if current_truck_id and current_truck_id != loading_truck_id:
            statistics.load_durations.append(tracking_data.duration)
            tracking_data.duration = 0
            tracking_data.current_truck = loading_truck_id

        # Если самосвал в состоянии погрузки, накапливаем длительность
        if loading_truck_state == TruckState.LOADING:
            tracking_data.duration += duration
            tracking_data.current_truck = loading_truck_id


class RepairStateHandler(ShovelStateHandler):
    """Обработчик состояния ремонта экскаватора"""

    def on_enter(
            self,
            tracking_data: ShovelTrackingData,
            duration: float,
            loading_truck_id: int | None,
            loading_truck_state: TruckState | None,
            statistics: ShovelStatistics,
    ):
        # Учитываем длительность ремонта в общей статистике
        statistics.totals.repairs_duration += duration

    def on_exit(
            self,
            tracking_data: ShovelTrackingData,
            new_state: ExcState,
            loading_truck_id: int | None,
            loading_truck_state: TruckState | None,
            statistics: ShovelStatistics,
    ):
        # При выходе из ремонта дополнительных действий не требуется
        pass

    def on_update(
            self,
            tracking_data: ShovelTrackingData,
            duration: float,
            loading_truck_id: int | None,
            loading_truck_state: TruckState | None,
            statistics: ShovelStatistics,
    ):
        # Продолжаем учитывать длительность ремонта
        statistics.totals.repairs_duration += duration


class BlastingIdleStateHandler(ShovelStateHandler):
    """Обработчик состояния ожидания взрывных работ"""

    def on_enter(
            self,
            tracking_data: ShovelTrackingData,
            duration: float,
            loading_truck_id: int | None,
            loading_truck_state: TruckState | None,
            statistics: ShovelStatistics,
    ):
        # Учитываем длительность ожидания взрывных работ
        statistics.totals.blast_waiting_duration += duration

    def on_exit(
            self,
            tracking_data: ShovelTrackingData,
            new_state: ExcState,
            loading_truck_id: int | None,
            loading_truck_state: TruckState | None,
            statistics: ShovelStatistics,
    ):
        pass

    def on_update(
            self,
            tracking_data: ShovelTrackingData,
            duration: float,
            loading_truck_id: int | None,
            loading_truck_state: TruckState | None,
            statistics: ShovelStatistics,
    ):
        # Продолжаем учитывать длительность ожидания
        statistics.totals.blast_waiting_duration += duration


class PlannedIdleStateHandler(ShovelStateHandler):
    """Обработчик состояния планового простоя"""

    def on_enter(
            self,
            tracking_data: ShovelTrackingData,
            duration: float,
            loading_truck_id: int | None,
            loading_truck_state: TruckState | None,
            statistics: ShovelStatistics,
    ):
        # Учитываем длительность планового простоя
        statistics.totals.planned_idles_duration += duration

    def on_exit(
            self,
            tracking_data: ShovelTrackingData,
            new_state: ExcState,
            loading_truck_id: int | None,
            loading_truck_state: TruckState | None,
            statistics: ShovelStatistics,
    ):
        pass

    def on_update(
            self,
            tracking_data: ShovelTrackingData,
            duration: float,
            loading_truck_id: int | None,
            loading_truck_state: TruckState | None,
            statistics: ShovelStatistics,
    ):
        # Продолжаем учитывать длительность простоя
        statistics.totals.planned_idles_duration += duration


class ShovelStatisticsManager:
    """Менеджер статистики экскаваторов"""

    def __init__(self, stats: ShovelStatistics, state_tracking: StateTrackingContainer):
        self.stats: ShovelStatistics = stats
        self.state_tracking: StateTrackingContainer = state_tracking
        self._handlers = {
            ExcState.WAITING: WaitingStateHandler(),
            ExcState.LOADING: LoadingStateHandler(),
            ExcState.REPAIR: RepairStateHandler(),
            ExcState.BLASTING_IDLE: BlastingIdleStateHandler(),
            ExcState.PLANNED_IDLE: PlannedIdleStateHandler(),
        }

    def update(
            self,
            obj_id: int,
            state: ExcState,
            duration: float,
            loading_truck_id: int | None = None,
            loading_truck_state: TruckState | None = None
    ):
        # Инициализируем данные отслеживания для нового экскаватора
        if obj_id not in self.state_tracking.shovels:
            self.state_tracking.shovels[obj_id] = ShovelTrackingData(
                cur_state=state,
                duration=duration,
                current_truck=loading_truck_id
            )

        shovel_data = self.state_tracking.shovels[obj_id]
        old_state = shovel_data.cur_state

        # Получаем обработчики для старого и нового состояний
        old_handler = self._handlers.get(old_state)
        new_handler = self._handlers.get(state)

        # Если состояние изменилось
        if old_state != state:
            # Завершаем старое состояние
            if old_handler:
                old_handler.on_exit(shovel_data, state, loading_truck_id, loading_truck_state, self.stats)

            # Начинаем новое состояние
            if new_handler:
                new_handler.on_enter(shovel_data, duration, loading_truck_id, loading_truck_state, self.stats)
        else:
            # Обновляем текущее состояние
            if new_handler:
                new_handler.on_update(shovel_data, duration, loading_truck_id, loading_truck_state, self.stats)

        # Обновляем текущее состояние в данных отслеживания
        shovel_data.cur_state = state


# endregion


# region Truck state handlers
class TruckStateHandler(ABC):
    """Абстрактный обработчик состояния самосвала."""

    @abstractmethod
    def on_enter(
            self,
            tracking_data: TruckTrackingData,
            duration: float,
            statistics: TruckStatistics,
    ):
        """Вызывается при входе в новое состояние"""
        pass

    @abstractmethod
    def on_exit(
            self,
            tracking_data: TruckTrackingData,
            new_state: TruckState,
            statistics: TruckStatistics,
    ):
        """Вызывается при выходе из текущего состояния"""
        pass

    @abstractmethod
    def on_update(
            self,
            tracking_data: TruckTrackingData,
            duration: float,
            statistics: TruckStatistics,
    ):
        """Вызывается при обновлении текущего состояния"""
        pass


class MovingEmptyStateHandler(TruckStateHandler):
    """Обработчик движения самосвала порожним"""

    def on_enter(
            self,
            tracking_data: TruckTrackingData,
            duration: float,
            statistics: TruckStatistics,
    ):
        # Начинаем накапливать длительность движения порожним
        tracking_data.duration += duration

    def on_exit(
            self,
            tracking_data: TruckTrackingData,
            new_state: TruckState,
            statistics: TruckStatistics,
    ):
        # При выходе фиксируем общую длительность движения порожним
        statistics.moving_empty_duration.append(tracking_data.duration)
        tracking_data.duration = 0

    def on_update(
            self,
            tracking_data: TruckTrackingData,
            duration: float,
            statistics: TruckStatistics,
    ):
        # Продолжаем накапливать длительность
        tracking_data.duration += duration


class MovingLoadedStateHandler(TruckStateHandler):
    """Обработчик движения самосвала гружёным"""

    def on_enter(
            self,
            tracking_data: TruckTrackingData,
            duration: float,
            statistics: TruckStatistics,
    ):
        # Начинаем накапливать длительность движения гружёным
        tracking_data.duration += duration

    def on_exit(
            self,
            tracking_data: TruckTrackingData,
            new_state: TruckState,
            statistics: TruckStatistics,
    ):
        # При выходе фиксируем общую длительность движения гружёным
        statistics.moving_loaded_duration.append(tracking_data.duration)
        tracking_data.duration = 0

    def on_update(
            self,
            tracking_data: TruckTrackingData,
            duration: float,
            statistics: TruckStatistics,
    ):
        # Продолжаем накапливать длительность
        tracking_data.duration += duration


class OtherTruckStateHandler(TruckStateHandler):
    """Обработчик для состояний самосвала, не требующих специальной логики"""

    def on_enter(
            self,
            tracking_data: TruckTrackingData,
            duration: float,
            statistics: TruckStatistics,
    ):
        # Для других состояний не требуется специальных действий
        pass

    def on_exit(
            self,
            tracking_data: TruckTrackingData,
            new_state: TruckState,
            statistics: TruckStatistics,
    ):
        pass

    def on_update(
            self,
            tracking_data: TruckTrackingData,
            duration: float,
            statistics: TruckStatistics,
    ):
        pass


class TruckStatisticsManager:
    """Менеджер статистики самосвалов"""

    def __init__(self, stats: TruckStatistics, state_tracking: StateTrackingContainer):
        self.stats: TruckStatistics = stats
        self.state_tracking: StateTrackingContainer = state_tracking
        # Регистрируем обработчики только для состояний, требующих статистики
        self._handlers = {
            TruckState.MOVING_EMPTY: MovingEmptyStateHandler(),
            TruckState.MOVING_LOADED: MovingLoadedStateHandler(),
        }

    def update(self, obj_id: int, state: TruckState, duration: float):
        # Инициализируем данные отслеживания для нового самосвала
        if obj_id not in self.state_tracking.trucks:
            self.state_tracking.trucks[obj_id] = TruckTrackingData(cur_state=state, duration=0)

        truck_data = self.state_tracking.trucks[obj_id]
        old_state = truck_data.cur_state

        # Используем обработчики по умолчанию для состояний без специальной логики
        old_handler = self._handlers.get(old_state, OtherTruckStateHandler())
        new_handler = self._handlers.get(state, OtherTruckStateHandler())

        # Если состояние изменилось
        if old_state != state:
            # Завершаем старое состояние и начинаем новое
            old_handler.on_exit(truck_data, state, self.stats)
            new_handler.on_enter(truck_data, duration, self.stats)
        else:
            # Обновляем текущее состояние
            new_handler.on_update(truck_data, duration, self.stats)

        # Обновляем текущее состояние
        truck_data.cur_state = state


# endregion


# region Unload state handlers
class UnloadStateHandler(ABC):
    """Абстрактный обработчик состояния пункта разгрузки."""

    @abstractmethod
    def on_enter(
            self,
            tracking_data: UnloadTrackingData,
            duration: float,
            unloading_truck_id: int | None,
            unloading_truck_state: TruckState | None,
            statistics: UnloadStatistics,
    ):
        """Вызывается при входе в новое состояние"""
        pass

    @abstractmethod
    def on_exit(
            self,
            tracking_data: UnloadTrackingData,
            new_state: UnloadState,
            unloading_truck_id: int | None,
            unloading_truck_state: TruckState | None,
            statistics: UnloadStatistics,
    ):
        """Вызывается при выходе из текущего состояния"""
        pass

    @abstractmethod
    def on_update(
            self,
            tracking_data: UnloadTrackingData,
            duration: float,
            unloading_truck_id: int | None,
            unloading_truck_state: TruckState | None,
            statistics: UnloadStatistics,
    ):
        """Вызывается при обновлении текущего состояния"""
        pass


class OpenUnloadStateHandler(UnloadStateHandler):
    """Обработчик открытого состояния пункта разгрузки"""

    def on_enter(
            self,
            tracking_data: UnloadTrackingData,
            duration: float,
            unloading_truck_id: int | None,
            unloading_truck_state: TruckState | None,
            statistics: UnloadStatistics,
    ):
        # Обрабатываем текущее состояние
        self._process_state(
            tracking_data,
            duration,
            unloading_truck_id,
            unloading_truck_state,
            statistics,
        )

    def on_exit(
            self,
            tracking_data: UnloadTrackingData,
            new_state: UnloadState,
            unloading_truck_id: int | None,
            unloading_truck_state: TruckState | None,
            statistics: UnloadStatistics,
    ):
        # При выходе из OPEN состояния фиксируем ожидание, если нет самосвала
        if not tracking_data.current_truck:
            statistics.truck_arrival_waiting_durations.append(tracking_data.duration)
            tracking_data.duration = 0

    def on_update(
            self,
            tracking_data: UnloadTrackingData,
            duration: float,
            unloading_truck_id: int | None,
            unloading_truck_state: TruckState | None,
            statistics: UnloadStatistics,
    ):
        # Обрабатываем обновление OPEN состояния
        self._process_state(
            tracking_data,
            duration,
            unloading_truck_id,
            unloading_truck_state,
            statistics,
        )

    def _process_state(
            self,
            tracking_data: UnloadTrackingData,
            duration: float,
            unloading_truck_id: int | None,
            unloading_truck_state: TruckState | None,
            statistics: UnloadStatistics,
    ):
        """Общая логика обработки OPEN состояния"""
        current_truck_id = tracking_data.current_truck

        # Если появился самосвал после ожидания, фиксируем время ожидания
        if not current_truck_id and unloading_truck_id:
            statistics.truck_arrival_waiting_durations.append(tracking_data.duration)
            tracking_data.duration = 0
        # Если сменился самосвал, фиксируем время разгрузки предыдущего
        elif current_truck_id and current_truck_id != unloading_truck_id:
            statistics.unload_durations.append(tracking_data.duration)
            tracking_data.duration = 0

        # Обрабатываем текущую ситуацию
        if not unloading_truck_id:
            # Ожидание самосвала - накапливаем время ожидания
            tracking_data.duration += duration
            tracking_data.current_truck = None
        elif unloading_truck_id and unloading_truck_state == TruckState.UNLOADING:
            # Разгрузка самосвала - накапливаем время разгрузки
            tracking_data.duration += duration
            tracking_data.current_truck = unloading_truck_id


class ClosedUnloadStateHandler(UnloadStateHandler):
    """Обработчик закрытого состояния пункта разгрузки"""

    def on_enter(
            self,
            tracking_data: UnloadTrackingData,
            duration: float,
            unloading_truck_id: int | None,
            unloading_truck_state: TruckState | None,
            statistics: UnloadStatistics,
    ):
        # При закрытии пункта разгрузки не требуется специальных действий
        pass

    def on_exit(
            self,
            tracking_data: UnloadTrackingData,
            new_state: UnloadState,
            unloading_truck_id: int | None,
            unloading_truck_state: TruckState | None,
            statistics: UnloadStatistics,
    ):
        pass

    def on_update(
            self,
            tracking_data: UnloadTrackingData,
            duration: float,
            unloading_truck_id: int | None,
            unloading_truck_state: TruckState | None,
            statistics: UnloadStatistics,
    ):
        pass


class UnloadStatisticsManager:
    """Менеджер статистики пунктов разгрузки"""

    def __init__(self, stats: UnloadStatistics, state_tracking: StateTrackingContainer):
        self.stats: UnloadStatistics = stats
        self.state_tracking: StateTrackingContainer = state_tracking
        # Регистрируем обработчик только для OPEN состояния
        self._handlers = {
            UnloadState.OPEN: OpenUnloadStateHandler(),
        }

    def update(
            self,
            obj_id: int,
            state: UnloadState,
            duration: float,
            unloading_truck_id: int | None = None,
            unloading_truck_state: TruckState | None = None
    ):
        # Инициализируем данные отслеживания для нового пункта разгрузки
        if obj_id not in self.state_tracking.unloads:
            self.state_tracking.unloads[obj_id] = UnloadTrackingData(
                cur_state=state,
                duration=0,
                current_truck=unloading_truck_id
            )

        unload_data = self.state_tracking.unloads[obj_id]
        old_state = unload_data.cur_state

        # Используем обработчики по умолчанию для неOPEN состояний
        old_handler = self._handlers.get(old_state, ClosedUnloadStateHandler())
        new_handler = self._handlers.get(state, ClosedUnloadStateHandler())

        # Если состояние изменилось
        if old_state != state:
            # Завершаем старое состояние и начинаем новое
            old_handler.on_exit(
                unload_data,
                state,
                unloading_truck_id,
                unloading_truck_state,
                self.stats,
            )
            new_handler.on_enter(
                unload_data,
                duration,
                unloading_truck_id,
                unloading_truck_state,
                self.stats,
            )
        else:
            # Обновляем статистики в текущем состоянии
            new_handler.on_update(
                unload_data,
                duration,
                unloading_truck_id,
                unloading_truck_state,
                self.stats,
            )

        # Обновляем текущее состояние
        unload_data.cur_state = state


# endregion


# region StatisticService
class StatisticService:
    """
    Сервис для сбора и анализа статистики производительности.

    Класс предназначен для накопления статистических данных о различных аспектах работы
    экскаваторов, самосвалов и пунктов разгрузки.
    """

    def __init__(self):
        # Инициализация структур для хранения финальной статистики
        self.shovel_stats: ShovelStatistics = ShovelStatistics()
        self.unload_stats: UnloadStatistics = UnloadStatistics()
        self.truck_stats: TruckStatistics = TruckStatistics()

        # Контейнер для временных данных отслеживания состояний
        self.state_tracking = StateTrackingContainer()

        # Инициализируем менеджеры для каждого типа сущностей
        self._shovel_manager = ShovelStatisticsManager(self.shovel_stats, self.state_tracking)
        self._truck_manager = TruckStatisticsManager(self.truck_stats, self.state_tracking)
        self._unload_manager = UnloadStatisticsManager(self.unload_stats, self.state_tracking)

    def update_truck_statistics(self, obj_id: int, state: TruckState):
        """Обновление статистики самосвала"""
        # duration=1 соответствует одному шагу симуляции
        self._truck_manager.update(obj_id, state, duration=1)

    def update_shovel_statistics(
            self,
            obj_id: int,
            state: ExcState,
            duration: int | float,
            loading_truck_id: int | None = None,
            loading_truck_state: TruckState | None = None
    ):
        """Обновление статистики экскаватора"""
        self._shovel_manager.update(obj_id, state, duration, loading_truck_id, loading_truck_state)

    def update_unload_statistics(
            self,
            obj_id: int,
            state: UnloadState,
            duration: int | float,
            unloading_truck_id: int | None = None,
            unloading_truck_state: TruckState | None = None
    ):
        """Обновление статистики пункта разгрузки"""
        self._unload_manager.update(obj_id, state, duration, unloading_truck_id, unloading_truck_state)

    @staticmethod
    def _calculate_mean(data_list: List[Union[int, float]]) -> Optional[float]:
        """
        Вспомогательный метод для расчета среднего арифметического (mean) значения списка.

        Args:
            data_list: Список числовых значений

        Returns:
            Среднее арифметическое значение или None, если список пуст
        """
        if not data_list:
            return None
        return sum(data_list) / len(data_list)

    def _calculate_variance(self, data_list: List[Union[int, float]]) -> Optional[float]:
        """
        Вспомогательный метод для расчета дисперсии списка.

        Дисперсия вычисляется по формуле для выборки (с поправкой Бесселя):
        variance = Σ(x - mean)² / (n - 1)

        Args:
            data_list: Список числовых значений

        Returns:
            Дисперсия или None, если в списке меньше 2 элементов
        """
        if len(data_list) < 2:
            return None

        mean = self._calculate_mean(data_list)
        if mean is None:
            return None

        squared_deviations = [(x - mean) ** 2 for x in data_list]
        return sum(squared_deviations) / (len(data_list) - 1)

    def calculate_trucks_needed(self, target_shovels_utilization: float = 0.9) -> float | None:
        """Производит расчёт требуемого количество самосвалов для достижения указанной целевой загрузки экскаваторов"""
        sim_data = DR.env().sim_data

        shovels_quantity = len(sim_data.shovels.keys())

        try:
            # Дособираем длительность всех обедов для статистики
            # Умножаем на количество экскаваторов, так как обед у всех одновременно
            if sim_data.lunch_times:
                lunches_duration_total = sum([(lunch[1] - lunch[0]).total_seconds() for lunch in sim_data.lunch_times])
                self.shovel_stats.totals.lunches_duration = lunches_duration_total * shovels_quantity

            arguments = dict(
                target_shovels_utilization=target_shovels_utilization,
                duration=sim_duration(),

                shovels_quantity=shovels_quantity,
                unloads_quantity=len(sim_data.unloads.keys()),

                mean_load_duration=self._calculate_mean(self.shovel_stats.load_durations),
                variance_load_duration=self._calculate_variance(self.shovel_stats.load_durations),
                mean_unload_duration=self._calculate_mean(self.unload_stats.unload_durations),
                variance_unload_duration=self._calculate_variance(self.unload_stats.unload_durations),

                mean_moving_loaded_duration=self._calculate_mean(self.truck_stats.moving_loaded_duration),
                mean_moving_empty_duration=self._calculate_mean(self.truck_stats.moving_empty_duration),

                mean_shovels_waiting_trucks_duration=self._calculate_mean(
                    self.shovel_stats.truck_arrival_waiting_durations
                ),
                variance_shovels_waiting_trucks_duration=self._calculate_variance(
                    self.shovel_stats.truck_arrival_waiting_durations
                ),
                mean_unloads_waiting_trucks_duration=self._calculate_mean(
                    self.unload_stats.truck_arrival_waiting_durations
                ),
                variance_unloads_waiting_trucks_duration=self._calculate_variance(
                    self.unload_stats.truck_arrival_waiting_durations
                ),

                shovels_repair_duration=self.shovel_stats.totals.repairs_duration,
                shovels_planned_idle_duration=self.shovel_stats.totals.planned_idles_duration,
                shovels_blast_waiting_duration=self.shovel_stats.totals.blast_waiting_duration,
                shovels_lunches_duration=self.shovel_stats.totals.lunches_duration,
            )
            logger.debug(f'StatisticService.calculate_trucks_needed arguments: {arguments}')

            # Вызываем калькулятор с собранной статистикой
            trucks_needed = TrucksNeededCalculator.calculate_trucks_needed(**arguments)

            # Если итогом подсчёта в калькуляторе станет бесконечность, сообщим о некорректности результата
            if trucks_needed == float('inf'):
                raise ValueError(f"Trucks needed is {trucks_needed}")

            return trucks_needed
        except Exception:
            # Логируем ошибку и просто вернём пустой ответ (не смогли посчитать)
            tb_str = traceback.format_exc()
            logger.error(tb_str)
            return None

# endregion