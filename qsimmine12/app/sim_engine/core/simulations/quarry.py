import logging
import random
from copy import deepcopy
from datetime import timedelta, datetime
from typing import Tuple

# TODO: Решить проблему циклических ссылок
# from app.sim_engine.core.simulations.shovel import Shovel
# from app.sim_engine.core.simulations.truck import Truck
# from app.sim_engine.core.simulations.unload import Unload
from app.sim_engine.core.planner.manage import Planner
from app.sim_engine.core.props import SimData, Blasting, IdleArea
from app.sim_engine.core.simulations.behaviors.blasting import QuarryBlastingWatcher
from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver as DR
from app.sim_engine.core.simulations.utils.helpers import safe_int
from app.sim_engine.enums import ObjectType, SolverType
from app.sim_engine.events import Event, EventType
from app.sim_engine.states import TruckState

logger = logging.getLogger(__name__)


class TripStartTimeNotDefinedException(Exception):
    pass


class Quarry:
    def __init__(self):
        env = DR.env()
        self.writer = DR.writer()
        self.trip_service = DR.trip_service()
        self.statistic_service = DR.statistic_service()
        self.solver = DR.solver()
        self.sim_conf = DR.sim_conf()

        self.env = env
        self.start_time = env.sim_data.start_time

        self.trips_table = []

        self.truck_map: dict = {}
        self.shovel_map: dict = {}
        self.unload_map: dict = {}
        self.shift_change_area: IdleArea = None

        # Данные для ребилда плановых рейсов во время симуляции
        self.sim_data: SimData = None
        self.planned_trips: dict = None
        self.exclude_objects: dict = {
            "trucks": [],
            "shovels": [],
            "unloads": []
        }

        self.seeded_random: random.Random = random._inst

        # механизм учёта взрывных работ
        self.active_blasting: list[Blasting] = []
        self.active_blasting_polygons: Tuple[Tuple[Tuple[float, float]]] | list[list[list[float]]] = []
        self.blasting_proc = QuarryBlastingWatcher(
            target=self,
        ) if self.sim_conf["blasting"] else None

    @property
    def current_time(self) -> datetime:
        return self.start_time + timedelta(seconds=self.env.now)

    @property
    def current_timestamp(self):
        return self.current_time.timestamp()

    @property
    def restricted_zones(self):
        return self.active_blasting_polygons

    def prepare_seeded_random(self) -> None:
        """
        Generate seed if it doesn't exist in `self.sim_data.seed` and init `random.Random` instance with it

        Needs to be called when we already have `self.sim_data`
        """
        if self.sim_data.seed is None:
            self.sim_data.seed = random.getrandbits(128)
        self.seeded_random = random.Random(self.sim_data.seed)

    def update_planned_trips(self):
        for truck_id, sim_truck in self.truck_map.items():
            sim_truck.planned_trips = self.planned_trips.get(truck_id, sim_truck.planned_trips)
            if sim_truck.state in [
                TruckState.MOVING_EMPTY,
                TruckState.WAITING,
            ]:
                sim_truck.process.interrupt()

    def update_trucks_position(self, sim_data):
        for truck_id, sim_truck in self.truck_map.items():
            truck = sim_data.trucks[truck_id]
            truck.initial_lat = sim_truck.position.lat
            truck.initial_lon = sim_truck.position.lon
            truck.initial_edge_id = sim_truck.edge.index if sim_truck.edge else None

    def rebuild_plan_by_add_exclude(
            self,
            start_time: datetime = None,
            end_time: datetime = None,
            exclude_object_id: int = None,
            exclude_object_type: ObjectType = None
    ) -> None:

        sim_data_copy = deepcopy(self.sim_data)
        if start_time:
            sim_data_copy.start_time = start_time
        if end_time:
            sim_data_copy.end_time = end_time

        self.update_trucks_position(sim_data_copy)

        if exclude_object_type == ObjectType.TRUCK:
            self.exclude_objects["trucks"].append(exclude_object_id)
        elif exclude_object_type == ObjectType.SHOVEL:
            self.exclude_objects["shovels"].append(exclude_object_id)
        elif exclude_object_type == ObjectType.UNLOAD:
            self.exclude_objects["unloads"].append(exclude_object_id)

        planner = Planner(
            solver=self.sim_conf["solver"],
            msg=self.sim_conf["msg"],
            workers=self.sim_conf["workers"],
            time_limit=self.sim_conf["time_limit"]
        )

        self.planned_trips = planner.run_with_exclude(sim_data_copy, self.exclude_objects)

        if self.planned_trips:
            self.update_planned_trips()

    def rebuild_plan_by_del_exclude(
            self,
            start_time: datetime = None,
            end_time: datetime = None,
            exclude_object_id: int = None,
            exclude_object_type: ObjectType = None
    ) -> None:

        sim_data_copy = deepcopy(self.sim_data)
        if start_time:
            sim_data_copy.start_time = start_time
        if end_time:
            sim_data_copy.end_time = end_time

        self.update_trucks_position(sim_data_copy)

        if exclude_object_type == ObjectType.TRUCK:
            self.exclude_objects["trucks"].remove(exclude_object_id)
        elif exclude_object_type == ObjectType.SHOVEL:
            self.exclude_objects["shovels"].remove(exclude_object_id)
        elif exclude_object_type == ObjectType.UNLOAD:
            self.exclude_objects["unloads"].remove(exclude_object_id)

        planner = Planner(
            solver=self.sim_conf["solver"],
            msg=self.sim_conf["msg"],
            workers=self.sim_conf["workers"],
            time_limit=self.sim_conf["time_limit"]
        )
        self.planned_trips = planner.run_with_exclude(sim_data_copy, self.exclude_objects)

        if self.planned_trips:
            self.update_planned_trips()

    def get_summary(self, end_time: datetime) -> dict:
        summary =  self.trip_service.get_summary(end_time)

        trucks_needed = self.statistic_service.calculate_trucks_needed(
            target_shovels_utilization=self.sim_data.target_shovel_load
        )
        summary['trucks_needed'] = safe_int(trucks_needed)
        logger.debug(f"SUMMARY -> trucks_needed: {summary['trucks_needed']}")

        return summary

    def push_event(self, event_type: EventType, *args, **kwargs):
        event = Event(
            event_code=event_type.code(),
            event_name=event_type.ru(),
            time=self.current_timestamp,
            object_id=ObjectType.QUARRY.key(),
            object_type=ObjectType.QUARRY,
            object_name='',
        )

        if event_type in [EventType.BLASTING_BEGIN, EventType.BLASTING_END]:
            blasting_id: int = kwargs.get("blasting_id")
            blasting_start: datetime = kwargs.get("blasting_start")
            blasting_end: datetime = kwargs.get("blasting_end")

            event = Event(
                event_code=event_type.code(),
                event_name=event_type.ru(),
                time=self.current_timestamp,
                object_id=f"{blasting_id}_blasting",
                object_type=ObjectType.BLASTING,
                object_name=f'{blasting_start.strftime("%d-%m-%Y %H:%M:%S")} - {blasting_end.strftime("%d-%m-%Y %H:%M:%S")}',
            )

            if self.sim_conf["mode"] == "auto" and self.sim_conf["solver"] == SolverType.GREEDY:
                # Собираем самосвалы для добавления в планирование и исключения из него
                trucks_to_exclude, trucks_to_include = self.blasting_proc.check_trucks_state()
                if trucks_to_exclude or trucks_to_include:
                    self.solver.rebuild_planning_data_cascade(
                        start_time=self.current_time,
                        excluded_objects=[(truck_id, ObjectType.TRUCK) for truck_id in trucks_to_exclude],
                        included_objects=[(truck_id, ObjectType.TRUCK) for truck_id in trucks_to_exclude]
                    )

        self.writer.push_event(event)
