from datetime import timedelta
from typing import List, Callable, Optional, Set

import simpy

from app.sim_engine.core.calculations.truck import TruckCalc
from app.sim_engine.core.geometry import (
    Point,
    Route,
    haversine_km,
    RouteEdge,
    build_route_edges_by_road_net,
    build_route_edges_by_road_net_from_position,
    build_route_edges_by_road_net_from_position_to_position,
    path_intersects_polygons,
    find_route_edges_around_restricted_zones_from_base_route
)
from app.sim_engine.core.props import TruckProperties, PlannedTrip, TripData
from app.sim_engine.core.simulations.behaviors.base import BaseTickBehavior, BreakdownBehavior, FuelBehavior, \
    LunchBehavior, PlannedIdleBehavior
from app.sim_engine.core.simulations.behaviors.blasting import TruckBlastingWatcher
from app.sim_engine.core.simulations.fuel_station import FuelStation
from app.sim_engine.core.simulations.quarry import Quarry
from app.sim_engine.core.simulations.shovel import Shovel
from app.sim_engine.core.simulations.unload import Unload
from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver as DR
from app.sim_engine.enums import ObjectType, IdleAreaType
from app.sim_engine.events import EventType, Event
from app.sim_engine.states import TruckState


class Truck:
    def __init__(
            self,
            unit_id,
            name,
            initial_position: Point,
            route: Route | None,
            route_edge: RouteEdge | None,
            start_route: RouteEdge | None,
            planned_trips: list[PlannedTrip],
            quarry: Quarry,
            shovel: Shovel | None,
            unload: Unload | None,
            properties: TruckProperties,
            fuel_stations: list[FuelStation],
            tick=1
    ):

        env = DR.env()
        self.writer = DR.writer()
        self.trip_service = DR.trip_service()
        self.idle_area_service = DR.idle_area_service()
        self.solver = DR.solver()
        self.sim_conf = DR.sim_conf()

        self.env = env
        self.id = unit_id
        self.name = name
        self.route = route
        self.route_edge = route_edge
        self.start_route = start_route

        # Текущий актуальный маршрут
        self.active_route_edge = None

        self.planned_trips = planned_trips
        self.quarry = quarry
        self.shovel = shovel
        self.unload = unload

        self.position = initial_position
        self.speed = 0
        self.edge = None

        self.weight = 0
        self.volume = 0
        self.fuel = properties.fuel_level
        self.fuel_stations = fuel_stations

        self.state = TruckState.IDLE
        self.target_speed = 30
        self.cycles_done = 0
        self.max_cycles = 3
        self.properties = properties
        self.start_time = env.sim_data.start_time
        self.process = env.process(self.run())
        self.calculator = TruckCalc
        self.tick = tick

        # Переменная для управления очередью на погрузке, разгрузке
        self.req = None

        # механизм Поломок/Восстановлений
        self.broken = False
        self.breakdown_proc = BreakdownBehavior(self, properties) if self.sim_conf["breakdown"] else None

        # механизм отслеживания топлива
        self.fuel_empty = False
        self.fuel_proc = FuelBehavior(self, properties) if self.sim_conf["refuel"] and self.fuel_stations else None

        # механизм отслеживания Обеденных перерывов
        self.at_lunch = False
        self.lunch_proc = LunchBehavior(
            target=self
        ) if self.sim_conf["lunch"] and self.quarry.sim_data.lunch_times else None

        # механизм отслеживания плановых простоев
        self.at_planned_idle = False
        self.planned_idle_proc = PlannedIdleBehavior(
            target=self,
            object_type=ObjectType.TRUCK,
        ) if self.sim_conf["planned_idle"] and self.quarry.sim_data.planned_idles.get(
            (ObjectType.TRUCK.key(), self.id)
        ) else None

        self.blasting_proc = TruckBlastingWatcher(
            target=self
        ) if self.sim_conf["blasting"] else None

        # Базовый логика процессов каждого тика.
        self.tick_proc = BaseTickBehavior(self)

    @property
    def nearest_fuel_station(self) -> FuelStation:
        if len(self.fuel_stations) > 2:
            nearest_fs = min(self.fuel_stations, key=lambda fs: haversine_km(self.position, fs.position))
        else:
            nearest_fs = self.fuel_stations[0]
        return nearest_fs

    @property
    def current_time(self):
        return self.start_time + timedelta(seconds=self.env.now)

    @property
    def current_timestamp(self):
        return self.current_time.timestamp()

    def travel_segment(self, p1: Point, p2: Point, speed_limit, acceleration):
        for speed, position in self.calculator.calculate_segment_motion(p1, p2, self.speed, speed_limit, acceleration):
            yield self.env.timeout(1)
            self.speed = speed
            self.position = position

    def broken_action(self):
        # логика поломок
        while self.broken:
            self.state = TruckState.REPAIR
            yield self.env.timeout(1)

    def refuel_action(self):
        """Логика заправок"""
        while self.fuel_empty:
            route_to_refuel = build_route_edges_by_road_net_from_position(
                lon=self.position.lon,
                lat=self.position.lat,
                height=None,
                edge_idx=self.edge.index,
                to_object_id=self.nearest_fuel_station.id,
                to_object_type=ObjectType.FUEL_STATION,
                road_net=self.quarry.sim_data.road_net
            )
            yield from self.moving(route_to_refuel, forward=True, actions=[self.broken_action, self.blasting_action])
            yield self.env.process(self.nearest_fuel_station.refuelling(self))

    def lunch_action(self):
        """ Логика обеденных перерывов """
        if self.at_lunch:
            self.state = TruckState.LUNCH

            for _ in self.move_to_area(IdleAreaType.LUNCH, actions=[self.broken_action]):
                yield _

                if not self.at_lunch:
                    # если обед кончился, а мы до него так и не доехали, больше не едем на обед
                    break

            # пережидаем обед
            while self.at_lunch:
                self.state = TruckState.LUNCH
                yield self.env.timeout(1)

    def planned_idle_action(self):
        """Логика плановых простоев"""
        if self.at_planned_idle:
            old_state = self.state

            self.state = TruckState.PLANNED_IDLE

            for _ in self.move_to_area(IdleAreaType.PLANNED_IDLE, actions=[self.broken_action]):
                yield _

                if not self.at_planned_idle:
                    # если простой кончился, а мы до него так и не доехали, больше не едем туда
                    break

            # пережидаем плановый простой
            while self.at_planned_idle:
                self.state = TruckState.PLANNED_IDLE
                yield self.env.timeout(1)

            self.state = old_state

    def wait_blasting(self, current_zones: Set[int]):
        """Логика ожидания изменений во взрывных работах"""
        while self.quarry.active_blasting and current_zones == {blasting.id for blasting in self.quarry.active_blasting}:
            self.state = TruckState.BLASTING_IDLE
            yield self.env.timeout(1)

    def blasting_action(self):
        """Логика поведения при активных взрывных работах"""
        if self.quarry.active_blasting:
            # Проверка на попадание маршрута в области взрывных работ
            if path_intersects_polygons(self.active_route_edge, self.quarry.active_blasting_polygons):
                # Сборка всех возможных маршрутов между пунктом отправления и пункт назнчения
                chosen_path = find_route_edges_around_restricted_zones_from_base_route(
                    base_route=self.active_route_edge,
                    restricted_zones=self.quarry.active_blasting_polygons,
                    road_net=self.quarry.sim_data.road_net,
                )

                # Если смогли найти маршрут в объезд зоны
                if chosen_path:
                    # TODO: Надо проложить путь до ближайшей точки на пути, и потом уже двигаться от неё
                    #  Пока что едем до точки начала маршрута, а потом уже едем по маршруту

                    # Если наше текущее положение не совпадает с началом построенного маршрута
                    if (self.position.lon, self.position.lat) != (chosen_path.start_point.lon,
                                                                  chosen_path.start_point.lat):
                        route_moving_to = build_route_edges_by_road_net_from_position_to_position(
                            lon=self.position.lon,
                            lat=self.position.lat,
                            height=0,
                            edge_idx=self.edge.index,
                            end_lon=chosen_path.start_point.x,
                            end_lat=chosen_path.start_point.y,
                            end_height=0,
                            end_edge_idx=chosen_path.edges[0].index,
                            road_net=self.quarry.sim_data.road_net
                        )
                        # проследуем к началу этого маршрута
                        yield from self.moving(route_moving_to, forward=True, actions=[self.broken_action])
                    # проедем основной маршрут
                    yield from self.moving(chosen_path, forward=True, actions=[self.broken_action])
                else:
                    old_state = self.state
                    self.state = TruckState.BLASTING_IDLE

                    # запоминаем активные зоны
                    remember_zones = {blasting.id for blasting in self.quarry.active_blasting}

                    # Едем в зону ожидания
                    for _ in self.move_to_area(IdleAreaType.BLAST_WAITING, actions=[self.broken_action]):
                        yield _
                        if remember_zones != {blasting.id for blasting in self.quarry.active_blasting}:
                            break

                    # Если за время движения в зону ожидания список взрывных работ не изменился, то стоим и ждём
                    yield from self.wait_blasting(remember_zones)
                    self.state = old_state

    def move_to_area(
            self,
            area_type: IdleAreaType,
            actions: Optional[List[Callable]] = None
    ):
        """Логика поиска ближайшей площадки выбранного типа и следование на эту площадку"""
        if not self.idle_area_service.get_areas(area_type=area_type):
            # зон указанного типа не существует, никуда не двигаемся
            return

        while True:
            # 1. Ищем ближайшую зону подходящего типа
            area, route = self.idle_area_service.find_nearest(
                area_type=area_type,
                lon=self.position.lon,
                lat=self.position.lat,
                edge_idx=self.edge.index,
                restricted_zones=self.quarry.active_blasting_polygons,
                road_net=self.quarry.sim_data.road_net,
            )

            # 2. Если нашли зону подходящего типа, отправляем двигаться по маршруту
            if area and route:
                for _ in self.moving(route, forward=True, actions=actions):
                    # даём возможность прекратить этот метод там, где он вызывался
                    yield _

                    if path_intersects_polygons(route, self.quarry.active_blasting_polygons):
                        break

            # 3. Если подходящая зона не нашлась
            elif not area or not route:
                # Ищем зону ожидания взрыва и едем туда ждать
                blast_waiting_area, route = self.idle_area_service.find_nearest(
                    area_type=IdleAreaType.BLAST_WAITING,
                    lon=self.position.lon,
                    lat=self.position.lat,
                    edge_idx=self.edge.index,
                    restricted_zones=self.quarry.active_blasting_polygons,
                    road_net=self.quarry.sim_data.road_net,
                )

                # запоминаем активные зоны взрывов
                remember_blasting_zones = {blasting.id for blasting in self.quarry.active_blasting}

                if blast_waiting_area and route:
                    for _ in self.moving(route, forward=True, actions=[self.broken_action]):
                        # даём возможность прервать метод там, где он вызывался
                        yield _

                        area, route = self.idle_area_service.find_nearest(
                            area_type=area_type,
                            lon=self.position.lon,
                            lat=self.position.lat,
                            edge_idx=self.edge.index,
                            restricted_zones=self.quarry.active_blasting_polygons,
                            road_net=self.quarry.sim_data.road_net,
                        )
                        if area and route:
                            break

                # Доехали, ждём взрывы
                for _ in self.wait_blasting(remember_blasting_zones):
                    yield _

            # 4. если доехали до нужной зоны
            if area and (area.initial_lon, area.initial_lat) == (self.position.lon, self.position.lat):
                return

    def moving(self, route: RouteEdge, forward: bool, actions: Optional[List[Callable]] = None):
        """
            Метод, производящий перемещение самосвала по заданному маршруту с возможностью отклонения от маршрута при необходимости
        """
        if actions is None:
            actions = []

        # Определяем текущий маршрут движения
        self.active_route_edge = route

        # запоминаем, куда изначально хотели двигаться
        destination_point = route.end_point if forward else route.start_point
        # Определяем гружёность самосвала
        is_loaded = self.state == TruckState.MOVING_LOADED

        # Выполняем, пока не достигнем задуманного пункта назначения
        destination_reached = False
        while not destination_reached:
            position_changed = False

            # Ведём самосвал по текущему маршруту
            for speed, position, edge in self.calculator.calculate_motion_by_edges(
                    self.active_route_edge,
                    self.properties,
                    forward=forward,
                    is_loaded=is_loaded):

                # Action'ы могут влиять на местоположение самосвала, поэтому запоминаем позицию
                position_before = (self.position.lon, self.position.lat)
                for action in actions:
                    yield from action()
                if position_before != (self.position.lon, self.position.lat):
                    # если по итогам отработки action'ов позиция самосвала изменилась,
                    # то нет смысла больше отслеживать текущее перемещение
                    position_changed = True
                    break

                yield self.env.timeout(1)
                self.speed = speed
                self.position = position
                self.edge = edge

            if position_changed:
                # Позиция поменялась, поэтому нужно построить новый маршрут от текущей позиции,
                # если текущая позиция не совпадает с изначальным пунктом назначения
                if (self.position.lon, self.position.lat) != (destination_point.x, destination_point.y):
                    self.active_route_edge = build_route_edges_by_road_net_from_position_to_position(
                        lon=self.position.lon,
                        lat=self.position.lat,
                        height=0,
                        edge_idx=self.edge.index,
                        end_lon=destination_point.lon,
                        end_lat=destination_point.lat,
                        end_height=0,
                        end_edge_idx=None,
                        road_net=self.quarry.sim_data.road_net
                    )
                    forward = True
                else:
                    # Мы достигли задуманного пункта назначения
                    destination_reached = True
            else:
                # если ничего не заставило изменить наш маршрут в процессе движения, значит мы достигли пункта назначения
                destination_reached = True

    def set_route(self) -> None:
        plan_trip = self.planned_trips.pop(0)
        self.shovel = self.quarry.shovel_map[plan_trip.shovel_id]
        self.unload = self.quarry.unload_map[plan_trip.unload_id]
        self.route_edge = build_route_edges_by_road_net(
            from_object_id=plan_trip.shovel_id,
            from_object_type=ObjectType.SHOVEL,
            to_object_id=plan_trip.unload_id,
            to_object_type=ObjectType.UNLOAD,
            road_net=self.quarry.sim_data.road_net
        )

    def set_start_route(self) -> None:
        if self.edge:
            self.start_route = build_route_edges_by_road_net_from_position(
                lon=self.position.lon,
                lat=self.position.lat,
                height=None,
                edge_idx=self.edge.index,
                to_object_id=self.shovel.id,
                to_object_type=ObjectType.SHOVEL,
                road_net=self.quarry.sim_data.road_net
            )
        else:
            self.start_route = build_route_edges_by_road_net(
                from_object_id=self.quarry.shift_change_area.id,
                from_object_type=ObjectType.IDLE_AREA,
                to_object_id=self.shovel.id,
                to_object_type=ObjectType.SHOVEL,
                road_net=self.quarry.sim_data.road_net
            )
            self.edge = self.start_route.edges[0]

    def run(self):
        default_actions = [
            self.broken_action,
            self.refuel_action,
            self.planned_idle_action,
            self.lunch_action,
            self.blasting_action,
        ]

        self.trip_service.set_shift_change_area(self.quarry.shift_change_area)

        while True:
            try:
                if not self.planned_trips and self.sim_conf["solver"] == "GREEDY" and self.sim_conf["mode"] == "auto":
                    trip = self.solver.assign_trip(self, self.env.now)
                    if trip:
                        self.planned_trips.append(trip)

                self.state = TruckState.MOVING_EMPTY
                self.trip_service.begin(self.current_trip_data())

                if self.planned_trips:
                    # Успешно произошло распределение и есть в плане рейс, строим новый маршрут
                    self.set_route()
                    self.set_start_route()
                    yield from self.moving(self.start_route, forward=True, actions=default_actions)

                elif not self.start_route:
                    # Распределение не произошло, но цикл прервался, нужно вывести на предыдущий маршрут
                    self.set_start_route()
                    yield from self.moving(self.start_route, forward=True, actions=default_actions)

                else:
                    # Просто продолжаем двигатся по предыдущему маршруту, без изменений
                    yield from self.moving(self.route_edge, forward=False, actions=default_actions)

                self.state = TruckState.WAITING
                self.speed = 0
                self.weight = 0
                self.volume = 0
                yield self.env.process(self.shovel.load_truck(self))

                self.state = TruckState.MOVING_LOADED
                self.speed = 0
                yield from self.moving(self.route_edge, forward=True, actions=default_actions)

                self.state = TruckState.UNLOADING
                self.speed = 0
                yield self.env.process(self.unload.unload_truck(self))

                self.trip_service.finish(self.current_trip_data())

                if self.planned_trips:
                    self.set_route()

                self.weight = 0
                self.volume = 0
                self.speed = 0
                self.state = TruckState.IDLE
                self.cycles_done += 1

                yield self.env.timeout(5)

            except simpy.Interrupt as e:

                # Сбрасываем начало маршрута, так как его потребуется перестроить
                self.start_route = None

                if self.req and self.req in self.shovel.resource.queue:
                    self.req.cancel()
                    self.shovel.trucks_queue.remove(self.name)
                if len(self.planned_trips) > 0:
                    self.set_route()
                    self.set_start_route()

    def push_event(self, event_type: EventType, write_event: bool = True) -> None:
        if write_event:
            event = Event(
                event_code=event_type.code(),
                event_name=event_type.ru(),
                time=self.current_timestamp,
                object_id=f"{self.id}_truck",
                object_type=ObjectType.TRUCK,
                object_name=self.name,
            )
            self.writer.push_event(event)

        if self.sim_conf["mode"] == "auto":
            if event_type in [EventType.BREAKDOWN_BEGIN, EventType.REFUELING_BEGIN, EventType.LUNCH_BEGIN,
                              EventType.PLANNED_IDLE_BEGIN]:
                if self.sim_conf["solver"] == "GREEDY":
                    self.solver.rebuild_planning_data(
                        start_time=self.current_time,
                        excluded_object=(self.id, ObjectType.TRUCK)
                    )
                else:
                    # TODO: Перевести ребилд MILP и CP солверов на env
                    self.quarry.rebuild_plan_by_add_exclude(
                        start_time=self.current_time,
                        exclude_object_id=self.id,
                        exclude_object_type=ObjectType.TRUCK
                    )

            elif event_type in [EventType.BREAKDOWN_END, EventType.REFUELING_END, EventType.LUNCH_END,
                                EventType.PLANNED_IDLE_END]:
                if self.sim_conf["solver"] == "GREEDY":
                    self.solver.rebuild_planning_data(
                        start_time=self.current_time,
                        included_object=(self.id, ObjectType.TRUCK)
                    )
                else:
                    # TODO: Перевести ребилд MILP и CP солверов на env
                    self.quarry.rebuild_plan_by_del_exclude(
                        start_time=self.current_time,
                        exclude_object_id=self.id,
                        exclude_object_type=ObjectType.TRUCK
                    )

    def telemetry_process(self):
        frame_data = {
            "object_id": f"{self.id}_truck",
            "object_name": self.name,
            "object_type": ObjectType.TRUCK.key(),
            "lat": round(self.position.lat, 6),
            "lon": round(self.position.lon, 6),
            "speed": round(self.speed, 1),
            "weight": round(self.weight, 1),
            "fuel": self.fuel,
            "state": self.state.ru(),
            "timestamp": self.current_timestamp
        }

        self.writer.writerow(frame_data)

    def current_trip_data(self) -> TripData:
        shovel_id = self.shovel.id if self.shovel else None
        unload_id = self.unload.id if self.unload else None

        return TripData(
            truck_id=self.id,
            shovel_id=shovel_id,
            unload_id=unload_id,
            truck_weight=self.weight,
            truck_volume=self.volume,
        )
