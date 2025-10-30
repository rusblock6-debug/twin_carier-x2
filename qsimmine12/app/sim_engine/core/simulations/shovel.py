from datetime import timedelta

import simpy

from app.sim_engine.core.calculations.shovel import ShovelCalc
from app.sim_engine.core.constants import density_by_material
from app.sim_engine.core.geometry import Point
from app.sim_engine.core.props import ShovelProperties
from app.sim_engine.core.simulations.behaviors.base import BreakdownBehavior, BaseTickBehavior, PlannedIdleBehavior
from app.sim_engine.core.simulations.behaviors.blasting import ShovelBlastingWatcher
from app.sim_engine.core.simulations.quarry import Quarry
from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver as DR
from app.sim_engine.enums import ObjectType
from app.sim_engine.events import Event, EventType
from app.sim_engine.states import ExcState, TruckState


class Shovel:
    def __init__(
            self,
            unit_id,
            name,
            position:
            Point,
            quarry: Quarry,
            properties: ShovelProperties,
            tick=1
    ):
        env = DR.env()

        self.env = env
        self.id = unit_id
        self.name = name
        self.position = position
        self.state = ExcState.WAITING
        self.writer = DR.writer()
        self.solver = DR.solver()
        self.sim_conf = DR.sim_conf()
        self.quarry = quarry
        self.resource = simpy.Resource(env, capacity=1)
        self.properties = properties
        self.cycles = 0
        self.start_time = env.sim_data.start_time
        self.trucks_queue = []
        self.tick = tick

        # механизм Поломок/Восстановлений
        self.broken = False
        self.breakdown = BreakdownBehavior(self, properties) if self.sim_conf["breakdown"] else None

        # механизм отслеживания плановых простоев
        self.at_planned_idle = False
        self.planned_idle_proc = PlannedIdleBehavior(
            target=self,
            object_type=ObjectType.SHOVEL,
        ) if self.sim_conf["planned_idle"] and self.quarry.sim_data.planned_idles.get(('shovel', self.id)) else None

        # механизм учёта взрывных работ
        self.in_blasting_idle = False
        self.blasting_proc = ShovelBlastingWatcher(
            target=self,
        ) if self.sim_conf["blasting"] else None

        # Базовый логика процессов каждого тика.
        self.tick_proc = BaseTickBehavior(self)

    @property
    def current_time(self):
        return self.start_time + timedelta(seconds=self.env.now)

    @property
    def current_timestamp(self):
        return self.current_time.timestamp()

    # TODO: старый метод, использовался до планировщика, кандидат на удаление
    def _load_truck(self, truck):
        with self.resource.request() as req:
            self.trucks_queue.append(truck.name)
            yield req
            volume = 0
            weight = 0
            while True:
                data = ShovelCalc.calculate_cycle(props=self.properties)
                load_time = data["vsego_s"]

                for _ in range(int(load_time)):  # Округление снижает точность расчетов!!!

                    while self.broken or truck.broken:
                        truck.state = TruckState.REPAIR if truck.broken else TruckState.IDLE
                        yield self.env.timeout(1)
                    truck.state = TruckState.LOADING

                    yield self.env.timeout(1)

                density = density_by_material[self.properties.tip_porody]
                cycle_volume = self.properties.obem_kovsha_m3 * self.properties.koef_zapolneniya
                cycle_weight = cycle_volume * density

                volume += cycle_volume
                weight += cycle_weight

                truck.weight = weight
                truck.volume = volume

                next_cycle_weight = weight + cycle_weight
                over_norm_weight = next_cycle_weight > truck.properties.body_capacity

                if over_norm_weight:
                    break

            self.trucks_queue.remove(truck.name)

    def load_truck(self, truck):
        truck.req = self.resource.request()
        self.trucks_queue.append(truck.name)
        yield truck.req

        for time, weight, volume in ShovelCalc.calculate_load_cycles_cumulative_generator(
            self.properties,
            truck.properties
        ):
            while self.broken or truck.broken:
                truck.state = TruckState.REPAIR if truck.broken else TruckState.IDLE
                yield self.env.timeout(1)
            truck.state = TruckState.LOADING
            yield self.env.timeout(time)
            truck.weight = weight
            truck.volume = volume

        self.resource.release(truck.req)
        self.trucks_queue.remove(truck.name)

    def main_tic_process(self):
        if self.broken:
            self.state = ExcState.REPAIR
        elif self.in_blasting_idle:
            self.state = ExcState.BLASTING_IDLE
        elif not self.broken and self.trucks_queue:
            self.state = ExcState.LOADING
        elif not self.broken and self.at_planned_idle:
            self.state = ExcState.PLANNED_IDLE
        elif not self.broken and not self.trucks_queue:
            self.state = ExcState.WAITING

    def push_event(self, event_type: EventType, write_event: bool = True):
        event = Event(
            event_code=event_type.code(),
            event_name=event_type.ru(),
            time=self.current_timestamp,
            object_id=f"{self.id}_shovel",
            object_type=ObjectType.SHOVEL,
            object_name=self.name,
        )

        if self.sim_conf["mode"] == "auto":
            if event_type in [EventType.BREAKDOWN_BEGIN, EventType.PLANNED_IDLE_BEGIN]:
                if self.sim_conf["solver"] == "GREEDY":
                    self.solver.rebuild_planning_data(
                        start_time=self.current_time,
                        excluded_object=(self.id, ObjectType.SHOVEL)
                    )
                else:
                    # TODO: Перевести ребилд MILP и CP солверов на env
                    self.quarry.rebuild_plan_by_add_exclude(
                        start_time=self.current_time,
                        exclude_object_id=self.id,
                        exclude_object_type=ObjectType.SHOVEL
                    )

            elif event_type in [EventType.BREAKDOWN_END, EventType.PLANNED_IDLE_END]:
                if self.sim_conf["solver"] == "GREEDY":
                    self.solver.rebuild_planning_data(
                        start_time=self.current_time,
                        included_object=(self.id, ObjectType.SHOVEL)
                    )
                else:
                    # TODO: Перевести ребилд MILP и CP солверов на env
                    self.quarry.rebuild_plan_by_del_exclude(
                        start_time=self.current_time,
                        exclude_object_id=self.id,
                        exclude_object_type=ObjectType.SHOVEL
                    )

        if write_event:
            self.writer.push_event(event)

    def telemetry_process(self):
        frame_data = {
            "object_id": f"{self.id}_shovel",
            "object_name": self.name,
            "object_type": ObjectType.SHOVEL.key(),
            "lat": round(self.position.lat, 6),
            "lon": round(self.position.lon, 6),
            "state": self.state.ru(),
            "timestamp": self.current_timestamp,
            "loading_truck": self.trucks_queue[0] if self.trucks_queue else "-",
            "trucks_queue": self.trucks_queue[1:]
        }
        self.writer.writerow(frame_data)
