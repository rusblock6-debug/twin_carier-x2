from datetime import timedelta

import simpy

from app.sim_engine.core.calculations.unload import UnloadCalc
from app.sim_engine.core.simulations.behaviors.base import BaseTickBehavior, BreakdownBehavior
from app.sim_engine.core.simulations.behaviors.blasting import UnloadBlastingWatcher
from app.sim_engine.core.simulations.quarry import Quarry
from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver as DR
from app.sim_engine.enums import ObjectType, SolverType
from app.sim_engine.events import Event, EventType
from app.sim_engine.states import UnloadState, TruckState


class Unload:
    def __init__(
            self,
            properties,
            unit_id,
            name,
            quarry: Quarry,
            tick=1
    ):
        env = DR.env()
        self.writer = DR.writer()
        self.statistic_service = DR.statistic_service()
        self.solver = DR.solver()
        self.sim_conf = DR.sim_conf()

        self.env = env
        self.resource = simpy.Resource(env, capacity=properties.trucks_at_once)
        self.state = UnloadState.OPEN
        self.properties = properties
        self.id = unit_id
        self.name = name
        self.quarry = quarry
        self.start_time = env.sim_data.start_time
        self.tick = tick
        self.trucks_queue = []

        # механизм Поломок/Восстановлений
        self.broken = False
        self.breakdown_proc = BreakdownBehavior(self, properties) if self.sim_conf["breakdown"] else None

        # механизм учёта взрывных работ
        self.in_blasting_idle = False
        self.blasting_proc = UnloadBlastingWatcher(
            self,
        ) if self.sim_conf["blasting"] else None

        # Базовый логика процессов каждого тика.
        self.tick_proc = BaseTickBehavior(self)

    @property
    def current_time(self):
        return self.start_time + timedelta(seconds=self.env.now)

    @property
    def current_timestamp(self):
        return self.current_time.timestamp()

    @property
    def unloading_truck(self):
        """Возвращает разгружающийся самосвал (первый в очереди)"""
        return self.trucks_queue[0] if self.trucks_queue else None

    @property
    def trucks_in_queue(self):
        """Возвращает список самосвалов, стоящих в очереди на разгрузку"""
        return self.trucks_queue[self.properties.trucks_at_once:] if len(self.trucks_queue) > self.properties.trucks_at_once else None

    def unload_truck(self, truck):
        with self.resource.request() as req:
            self.trucks_queue.append(truck)
            yield req
            data = UnloadCalc.unload_calculation(props=self.properties, truck_volume=truck.volume)
            time_unload = data["t_total"]
            weight_in_second = truck.weight / time_unload
            volume_in_second = truck.volume / time_unload
            for _ in range(int(time_unload)):

                while self.broken or truck.broken:
                    truck.state = TruckState.REPAIR if truck.broken else TruckState.IDLE
                    yield self.env.timeout(1)
                truck.state = TruckState.UNLOADING

                truck.weight = max(0, truck.weight - weight_in_second)
                truck.volume = max(0, truck.volume - volume_in_second)

                yield self.env.timeout(1)
            self.trucks_queue.remove(truck)

    def main_tic_process(self):
        if self.broken:
            self.state = UnloadState.REPAIR
        elif self.in_blasting_idle:
            self.state = UnloadState.BLASTING_IDLE
        else:
            self.state = UnloadState.OPEN

        # Учёт статистик
        unloading_truck = self.unloading_truck
        self.statistic_service.update_unload_statistics(
            obj_id=self.id,
            state=self.state,
            duration=self.tick,
            unloading_truck_id=unloading_truck.id if unloading_truck else None,
            unloading_truck_state=unloading_truck.state if unloading_truck else None,
        )

    def push_event(self, event_type: EventType, write_event: bool = True):
        event = Event(
            event_code=event_type.code(),
            event_name=event_type.ru(),
            time=self.current_timestamp,
            object_id=f"{self.id}_unload",
            object_type=ObjectType.UNLOAD,
            object_name=self.name,
        )
        if self.sim_conf["mode"] == "auto":
            if event_type in (EventType.BREAKDOWN_BEGIN, EventType.REFUELING_BEGIN, EventType.BLASTING_IDLE_BEGIN):
                if self.sim_conf["solver"] == SolverType.GREEDY:
                    self.solver.rebuild_planning_data(
                        start_time=self.current_time,
                        excluded_object=(self.id, ObjectType.UNLOAD)
                    )
                else:
                    # TODO: Перевести ребилд MILP и CP солверов на env
                    self.quarry.rebuild_plan_by_add_exclude(
                        start_time=self.current_time,
                        exclude_object_id=self.id,
                        exclude_object_type=ObjectType.UNLOAD
                    )
            elif event_type in (EventType.BREAKDOWN_END, EventType.REFUELING_END, EventType.BLASTING_IDLE_END):
                if self.sim_conf["solver"] == SolverType.GREEDY:
                    self.solver.rebuild_planning_data(
                        start_time=self.current_time,
                        included_object=(self.id, ObjectType.UNLOAD)
                    )
                else:
                    # TODO: Перевести ребилд MILP и CP солверов на env
                    self.quarry.rebuild_plan_by_del_exclude(
                        start_time=self.current_time,
                        exclude_object_id=self.id,
                        exclude_object_type=ObjectType.UNLOAD
                    )

        if write_event:
            self.writer.push_event(event)

    def telemetry_process(self):
        frame_data = {
            "object_id": f"{self.id}_unload",
            "object_type": ObjectType.UNLOAD.key(),
            "timestamp": self.current_timestamp,
            "unloading_trucks": [truck.name for truck in self.trucks_queue[:self.properties.trucks_at_once]],
            "trucks_queue": [truck.name for truck in self.trucks_queue[self.properties.trucks_at_once:]],
            "state": self.state.ru()
        }
        self.writer.writerow(frame_data)