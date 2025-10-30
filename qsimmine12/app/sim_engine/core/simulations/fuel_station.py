import copy
from datetime import timedelta

import simpy

from app.sim_engine.core.props import FuelStationProperties
from app.sim_engine.core.simulations.behaviors.base import BaseTickBehavior
from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver as DR
from app.sim_engine.enums import ObjectType
from app.sim_engine.events import FuelStationEvent, EventType
from app.sim_engine.states import FuelStationState, TruckState


class FuelStation:
    def __init__(self, properties: FuelStationProperties, unit_id, name, initial_position, tick=1):
        env = DR.env()

        self.env = env
        self.resource = simpy.Resource(env, capacity=properties.num_pumps)
        self.state = FuelStationState.WAITING
        self.properties = properties
        self.id = unit_id
        self.name = name
        self.position = initial_position
        self.writer = DR.writer()
        self.start_time = env.sim_data.start_time
        self.tick = tick
        self.trucks_queue = []

        # Базовый логика процессов каждого тика.
        self.tick_proc = BaseTickBehavior(self)

    @property
    def current_time(self):
        current_time = self.start_time + timedelta(seconds=self.env.now)
        timestamp = current_time.timestamp()
        return timestamp

    def refuelling(self, truck):
        with self.resource.request() as req:
            self.trucks_queue.append(truck.name)
            yield req
            self.push_event(event_type=EventType.REFUELING_BEGIN, truck=truck)
            fuel_needed = truck.properties.fuel_capacity - truck.fuel
            refuel_time = fuel_needed / self.properties.flow_rate
            old_state = copy.copy(truck.state)
            for _ in range(int(refuel_time)):
                truck.state = TruckState.REFUELING
                truck.fuel += self.properties.flow_rate
                yield self.env.timeout(1)
            self.push_event(event_type=EventType.REFUELING_END, truck=truck)
            truck.fuel_empty = False
            truck.fuel = truck.properties.fuel_capacity
            truck.state = old_state
            self.trucks_queue.remove(truck.name)

    def main_tic_process(self):
        if self.trucks_queue:
            self.state = FuelStationState.REFUELING
        else:
            self.state = FuelStationState.WAITING

    def push_event(self, event_type: EventType, truck):
        event = FuelStationEvent(
            event_code=event_type.code(),
            event_name=event_type.ru(),
            time=self.current_time,
            object_id=f"{self.id}_fuel_station",
            object_type=ObjectType.FUEL_STATION,
            object_name=self.name,
            truck_id=truck.id,
            truck_name=truck.name,
        )
        self.writer.push_event(event)

    def telemetry_process(self):
        frame_data = {
            "object_id": f"{self.id}_fuel_station",
            "object_type": ObjectType.FUEL_STATION.key(),
            "timestamp": self.current_time,
            "refuelling_trucks": self.trucks_queue[:self.properties.num_pumps],
            "trucks_queue": self.trucks_queue[self.properties.num_pumps:],
            "state": self.state.ru()
        }
        self.writer.writerow(frame_data)
