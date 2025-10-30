import enum
from dataclasses import dataclass, fields, is_dataclass, asdict
from enum import Enum
from typing import Any

from app.sim_engine.core.simulations.utils.mixins import DataclassEnumSerializerMixin
from app.sim_engine.enums import ObjectType


class EventType(Enum):
    BREAKDOWN_BEGIN = (1, "breakdown_begin", "Начало ремонта")
    BREAKDOWN_END = (2, "breakdown_end", "Завершение ремонта")

    REFUELING_BEGIN = (3, "refueling_begin", "Начало Заправки")
    REFUELING_END = (4, "refueling_end", "Конец Заправки")

    LUNCH_BEGIN = (5, "lunch_begin", "Начало обеда")
    LUNCH_END = (6, "lunch_end", "Конец обеда")

    BLASTING_BEGIN = (7, "blasting_begin", "Начало взрывных работ")
    BLASTING_END = (8, "blasting_end", "Завершение взрывных работ")

    BLASTING_IDLE_BEGIN = (9, "blasting_idle_begin", "Начало ожидания проведения взрывных работ")
    BLASTING_IDLE_END = (10, "blasting_idle_end", "Конец ожидания проведения взрывных работ")

    PLANNED_IDLE_BEGIN = (11, "planned_idle_begin", "Начало планового простоя (Ремонт, ТО и т.д.)")
    PLANNED_IDLE_END = (12, "planned_idle_end", "Конец планового простоя (Ремонт, ТО и т.д.)")

    def __str__(self):
        return self.value[1]  # По умолчанию — английский

    def code(self):
        return self.value[0]

    def ru(self):
        return self.value[2]

    def en(self):
        return self.value[1]


@dataclass
class Event(DataclassEnumSerializerMixin):
    event_code: int
    event_name: str
    time: float
    object_id: int | str
    object_type: ObjectType
    object_name: str


@dataclass
class FuelStationEvent(Event):
    truck_id: int
    truck_name: str
