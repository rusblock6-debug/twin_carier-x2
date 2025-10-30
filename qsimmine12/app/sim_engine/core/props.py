from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from app.sim_engine.enums import ObjectType


@dataclass
class Point:
    lat: float
    lon: float


@dataclass
class Segment:
    start: Point
    end: Point


@dataclass
class Route:
    id: int
    segments: list[Segment]
    shovel_id: int
    unload_id: int
    truck_ids: list[int]


@dataclass
class ShovelProperties:
    obem_kovsha_m3: float
    skorost_podem_m_s: float
    skorost_povorot_rad_s: float
    skorost_vrezki_m_s: float
    skorost_napolneniya_m_s: float
    initial_operating_time: int
    average_repair_duration: int
    initial_failure_count: int
    koef_zapolneniya: float = 0.8
    koef_gidravliki: float = 1.1
    koef_inertsii: float = 1.2
    koef_vozvrata: float = 0.85
    tip_porody: str = 'sand'
    vlazhnost_percent: float = 10.0


@dataclass
class Shovel:
    id: int
    name: str
    initial_lat: float
    initial_lon: float
    properties: ShovelProperties


@dataclass
class UnlProperties:
    angle: float
    material_type: str
    type_unloading: str
    initial_operating_time: int
    average_repair_duration: int
    initial_failure_count: int
    trucks_at_once: int = 100


@dataclass
class Unload:
    id: int
    name: str
    properties: UnlProperties


@dataclass
class FuelStationProperties:
    num_pumps: int
    flow_rate: float


@dataclass
class FuelStation:
    id: int
    name: str
    initial_lat: float
    initial_lon: float
    properties: FuelStationProperties


@dataclass
class ShiftChangeArea:
    id: int
    name: str
    initial_lat: float
    initial_lon: float


@dataclass
class IdleArea:
    id: int
    name: str
    initial_lon: float
    initial_lat: float

    is_shift_change_area: bool = False
    is_planned_idle_area: bool = False
    is_lunch_area: bool = False
    is_blast_waiting_area: bool = False


@dataclass
class IdleAreaStorage:
    areas: list[IdleArea] = field(default_factory=list)

    @property
    def all(self):
        return self.areas

    @property
    def lunch_areas(self):
        return [area for area in self.areas if area.is_lunch_area]

    @property
    def shift_change_areas(self):
        return [area for area in self.areas if area.is_shift_change_area]

    @property
    def planned_idle_areas(self):
        return [area for area in self.areas if area.is_planned_idle_area]

    @property
    def blast_waiting_areas(self):
        return [area for area in self.areas if area.is_blast_waiting_area]


@dataclass
class TruckProperties:
    body_capacity: float
    speed_empty_kmh: float
    speed_loaded_kmh: float
    initial_operating_time: int
    average_repair_duration: int
    initial_failure_count: int

    # топливо
    fuel_capacity: float
    fuel_threshold_critical: float
    fuel_threshold_planned: float
    fuel_level: float
    fuel_idle_lph: float
    fuel_specific_consumption: float
    fuel_density: float
    engine_power_kw: float

    # default
    acceleration_empty: float = 2.8
    acceleration_loaded: float = 1.4
    driver_skill: float = 1.0


@dataclass
class Truck:
    id: int
    name: str
    initial_lat: float
    initial_lon: float
    initial_edge_id: int
    properties: TruckProperties


@dataclass
class PlannedIdle:
    id: int
    vehicle_type: Literal["shovel", "truck"]
    start_time: datetime
    end_time: datetime
    quarry_id: int
    vehicle_id: int


@dataclass
class Blasting:
    id: int
    zones: list[list[list[float]]]
    start_time: datetime
    end_time: datetime


@dataclass
class SimData:
    start_time: datetime
    end_time: datetime
    duration: int

    seed: int | None

    trucks: dict[int, Truck]
    shovels: dict[int, Shovel]
    unloads: dict[int, Unload]
    idle_areas: IdleAreaStorage
    fuel_stations: dict[int, FuelStation]

    routes: list[Route]
    road_net: dict

    lunch_times: list[tuple[datetime, datetime]] = field(default_factory=list)
    planned_idles: dict[tuple[str, int], PlannedIdle] = field(default_factory=dict)
    blasting_list: list[Blasting] = field(default_factory=list)


@dataclass
class TripData:
    truck_id: int
    truck_weight: int | float
    truck_volume: int | float
    shovel_id: int | None
    unload_id: int | None


@dataclass
class PlannedTrip:
    truck_id: int
    shovel_id: int
    unload_id: int
    order: int


@dataclass
class QuarryObject:
    id: int
    type: ObjectType


@dataclass
class ActualTrip:
    start_trip_data: TripData
    start_object: QuarryObject
    start_time: datetime
    end_trip_data: TripData | None = None
    end_object: QuarryObject | None = None
    end_time: datetime | None = None

    def is_finished(self) -> bool:
        return (
                self.end_object is not None and
                self.end_time is not None and
                self.end_trip_data is not None
        )

    def to_telemetry(self) -> dict:
        if not self.is_finished():
            raise RuntimeError('Trip is not finished')

        return {
            'truck_id': self.end_trip_data.truck_id,
            'shovel_id': self.end_trip_data.shovel_id,
            'unload_id': self.end_trip_data.unload_id,
            'volume': int(self.end_trip_data.truck_volume),  # m3
            'weight': int(self.end_trip_data.truck_weight),
            'time': self.end_time.isoformat(),  # TODO: убрать позже, оставил для обратной совместимости
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'start_object': {
                'id': self.start_object.id,
                'type': self.start_object.type.key(),
            },
            'end_object': {
                'id': self.end_object.id,
                'type': self.end_object.type.key(),
            },
        }
