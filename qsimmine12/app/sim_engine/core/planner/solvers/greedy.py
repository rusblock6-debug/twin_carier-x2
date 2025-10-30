import logging
from copy import deepcopy
from datetime import datetime
from typing import List

from app.sim_engine.core.planner.entities import InputPlanningData
from app.sim_engine.core.planner.planning_matrix import get_planning_data
from app.sim_engine.core.props import PlannedTrip
from app.sim_engine.core.simulations.truck import Truck
from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver as DR
from app.sim_engine.enums import ObjectType
from app.sim_engine.states import TruckState

logger = logging.getLogger(__name__)


class GreedySolver:

    def __init__(self, planning_data: InputPlanningData = None):
        env = DR.env()

        self.sim_context = env.sim_context
        self.sim_data = deepcopy(env.sim_data)
        self._planning_data = planning_data

        self.exclude_objects: dict[ObjectType, list] = {
            ObjectType.TRUCK: [],
            ObjectType.SHOVEL: [],
            ObjectType.UNLOAD: []
        }

    @property
    def planning_data(self):
        if not self._planning_data:
            self._planning_data = get_planning_data(self.sim_data)
        return self._planning_data

    def _included_object(self, object_type: ObjectType, object_id: int):
        self.exclude_objects[object_type].remove(object_id)

    def _excluded_object(self, object_type: ObjectType, object_id: int):
        self.exclude_objects[object_type].append(object_id)

    def _included_objects(self, objects: list[tuple[int, ObjectType]]):
        for obj in objects:
            self._included_object(object_type=obj[1], object_id=obj[0])

    def _excluded_objects(self, objects: list[tuple[int, ObjectType]]):
        for obj in objects:
            self._excluded_object(object_type=obj[1], object_id=obj[0])

    def _update_trucks_position(self, truck_id, sim_truck):
        truck = self.sim_data.trucks[truck_id]
        truck.initial_lat = sim_truck.position.lat
        truck.initial_lon = sim_truck.position.lon
        truck.initial_edge_id = sim_truck.edge.index if sim_truck.edge else None

    @staticmethod
    def _reset_cycle(sim_truck):
        if sim_truck.state in [
            TruckState.MOVING_EMPTY,
            TruckState.WAITING,
        ]:
            sim_truck.process.interrupt()

    def rebuild_planning_data(
            self,
            start_time=None,
            end_time=None,
            excluded_object: tuple[int, ObjectType] = None,
            included_object: tuple[int, ObjectType] = None
    ):
        self._planning_data = None

        if start_time:
            self.sim_data.start_time = start_time
        if end_time:
            self.sim_data.end_time = end_time

        if excluded_object:
            self._excluded_object(object_type=excluded_object[1], object_id=excluded_object[0])

        elif included_object:
            self._included_object(object_type=included_object[1], object_id=included_object[0])

        for truck_id, sim_truck in self.sim_context.trucks.items():
            logger.debug(f"rebuild truck: {sim_truck.name}")
            self._update_trucks_position(truck_id, sim_truck)
            self._reset_cycle(sim_truck)

    def rebuild_planning_data_cascade(
            self,
            start_time: datetime | None = None,
            end_time: datetime | None = None,
            excluded_objects: List[tuple[int, ObjectType]] | None = None,
            included_objects: List[tuple[int, ObjectType]] | None = None
    ):
        self._planning_data = None

        if start_time:
            self.sim_data.start_time = start_time
        if end_time:
            self.sim_data.end_time = end_time

        if excluded_objects:
            self._excluded_objects(excluded_objects)
        elif included_objects:
            self._included_objects(included_objects)

        for truck_id, sim_truck in self.sim_context.trucks.items():
            logger.debug(f"rebuild truck: {sim_truck.name}")
            self._update_trucks_position(truck_id, sim_truck)
            self._reset_cycle(sim_truck)

    @staticmethod
    def find_trucks_to_shovel(shovel):
        trucks = []
        for truck in shovel.quarry.truck_map.values():
            if truck.shovel and truck.shovel.id == shovel.id and truck.state == TruckState.MOVING_EMPTY:
                trucks.append(truck)
        return trucks

    def choose_next_trip(self, truck, now: int):
        """Выбирает лучшую связку (shovel, unload) для данного самосвала"""
        best_score, best_choice = -1, None

        choices = []

        for shovel in truck.quarry.shovel_map.values():

            if shovel.broken:
                continue

            moving_trucks = self.find_trucks_to_shovel(shovel)
            trucks_count = len(shovel.trucks_queue) + len(moving_trucks)
            wait_shovel = trucks_count * self.planning_data.T_load[(truck.id, shovel.id)]

            for unld in truck.quarry.unload_map.values():

                if unld.broken:
                    continue

                wait_unl = len(unld.trucks_queue) * self.planning_data.T_unload[(truck.id, unld.id)]

                cycle_time = (
                        self.planning_data.T_start[(truck.id, shovel.id)] +
                        wait_shovel +
                        self.planning_data.T_load[(truck.id, shovel.id)] +
                        self.planning_data.T_haul[(truck.id, shovel.id, unld.id)] +
                        wait_unl +
                        self.planning_data.T_unload[(truck.id, unld.id)] +
                        self.planning_data.T_return[(truck.id, unld.id, shovel.id)]
                )
                tons = self.planning_data.m_tons[(truck.id, shovel.id)]
                score = tons / cycle_time

                choices.append((shovel.name, unld.name, cycle_time, score))
                if score > best_score:
                    best_score = score
                    best_choice = (shovel, unld, cycle_time, score)

        logger.debug(f"Choose trip for Track:{truck.name}; time: {truck.current_time}")
        logger.debug(f"Choices:{choices}")
        return best_choice

    def assign_trip(self, truck: Truck, now: int) -> PlannedTrip | None:
        """Формирует новый PlannedTrip и обновляет маршруты для самосвала"""
        choice = self.choose_next_trip(truck, now)
        if not choice:
            return None

        shovel, unld, cycle_time, score = choice

        trip = PlannedTrip(
            truck_id=truck.id,
            shovel_id=shovel.id,
            unload_id=unld.id,
            order=1
        )
        return trip
