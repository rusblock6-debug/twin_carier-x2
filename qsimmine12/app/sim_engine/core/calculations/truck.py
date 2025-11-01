from typing import Generator

import numpy as np

from app.sim_engine.core.dummy_roadnet import *
from app.sim_engine.core.geometry import Point, interpolate_position, haversine_km, RouteEdge


class TruckCalc:
    @classmethod
    def calculate_segment_motion(
            cls,
            p1: Point,
            p2: Point,
            initial_speed: float,
            speed_limit: float,
            acceleration: float,
            time_step_sec: int = 1
    ) -> Generator[tuple[float, Point], None, None]:
        """
        Расчет движения между двумя точками в маршруте
        """
        distance_km = haversine_km(p1, p2)
        travelled_km = 0.0
        speed = initial_speed

        while travelled_km < distance_km:
            speed = min(speed + acceleration, speed_limit)
            delta_km = speed * time_step_sec / 3600.0  # перевод в км
            travelled_km = min(travelled_km + delta_km, distance_km)
            ratio = travelled_km / distance_km
            new_position = interpolate_position(p1, p2, ratio)
            yield speed, new_position

    @classmethod
    def calculate_motion(cls, route, props, forward):
        """
        Расчет движения по маршруту состоящего из списка точек
        """

        points = route.points if forward else list(reversed(route.points))
        speed_limit = props.speed_empty_kmh if not forward else props.speed_loaded_kmh
        acceleration = props.acceleration_empty if not forward else props.acceleration_loaded

        current_speed = 0.0  # начальная скорость

        for i in range(len(points) - 1):
            for speed, position in cls.calculate_segment_motion(points[i], points[i + 1], current_speed, speed_limit,
                                                                 acceleration):
                yield speed, position
                current_speed = speed  # <--- обновляем накопленную скорость

    @classmethod
    def calculate_edge_motion(
            cls,
            edge: Edge,
            initial_speed: float,
            speed_limit: float,
            acceleration: float,
            time_step_sec: int = 1
    ) -> Generator[tuple[float, Point], None, None]:
        """
        Расчет движения по ребру графа
        """
        distance_km = edge.length / 1000
        # distance_km = haversine_km(edge.start, edge.stop)

        travelled_km = 0.0
        speed = initial_speed

        while travelled_km < distance_km:
            speed = min(speed + acceleration, speed_limit)
            delta_km = speed * time_step_sec / 3600.0  # перевод в км
            travelled_km = min(travelled_km + delta_km, distance_km)
            ratio = travelled_km / distance_km
            new_position = interpolate_position(edge.start, edge.stop, ratio)
            yield speed, new_position

    @classmethod
    def calculate_motion_by_edges(cls, route: RouteEdge, props, forward, is_loaded):
        """
        Расчет движения по списку ребер графа
        """

        speed_limit = props.speed_empty_kmh if not is_loaded else props.speed_loaded_kmh
        acceleration = props.acceleration_empty if not is_loaded else props.acceleration_loaded

        current_speed = 0.0  # начальная скорость

        if forward:
            generator_path = route.move_along_edges_gen
        else:
            generator_path = route.move_along_edges_reversed_gen

        for edge in generator_path():
            for speed, position in cls.calculate_edge_motion(
                    edge,
                    current_speed,
                    speed_limit,
                    acceleration
            ):
                yield speed, position, edge
                current_speed = speed  # <--- обновляем накопленную скорость

    @classmethod
    def calculate_time_motion_by_edges(cls, route: RouteEdge, props, forward):
        is_loaded = forward
        return sum([1 for _ in cls.calculate_motion_by_edges(route, props, forward, is_loaded)])

    # ---- Новые методы расчета из core_sim, пока нигде не работают----
    def time_empty(self) -> int:
        """
        Время движения порожним к экскаватору (сек)
        Формула: t = S / v * 3600 / driver_skill,
        где S — длина пути (км), v — скорость порожним (км/ч)
        """
        t = self.distance_km / self.speed_empty_kmh * 3600
        return int(np.ceil(t / self.driver_skill))

    def time_loaded(self) -> int:
        """
        Время движения гружённым к разгрузке (сек)
        Формула: t = S / v * 3600 / driver_skill,
        где S — длина пути (км), v — скорость гружённым (км/ч)
        """
        t = self.distance_km / self.speed_loaded_kmh * 3600
        return int(np.ceil(t / self.driver_skill))

