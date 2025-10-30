from typing import Tuple

from app.sim_engine.core.geometry import RouteEdge, find_route_edges_around_restricted_zones_from_position_to_object
from app.sim_engine.core.props import IdleAreaStorage, IdleArea
from app.sim_engine.enums import ObjectType, IdleAreaType


class IdleAreaService:
    """Сервис, предоставляющий операции для работы с площадками простоев"""

    def __init__(self, idle_area_storage: IdleAreaStorage):
        self.storage = idle_area_storage

    def get_areas(
            self,
            area_type: IdleAreaType | None = None
    ) -> list[IdleArea]:
        """Сбор площадок соответствующего типа"""
        if area_type is None:
            return self.storage.all
        elif area_type == IdleAreaType.LUNCH:
            return self.storage.lunch_areas
        elif area_type == IdleAreaType.BLAST_WAITING:
            return self.storage.blast_waiting_areas
        elif area_type == IdleAreaType.PLANNED_IDLE:
            return self.storage.planned_idle_areas
        elif area_type == IdleAreaType.SHIFT_CHANGE:
            return self.storage.shift_change_areas
        return []

    def find_nearest(
            self,
            area_type: IdleAreaType,
            lon: float,
            lat: float,
            edge_idx: int | None,
            restricted_zones: Tuple[Tuple[Tuple[float, float]]] | list[list[list[float]]] | None,
            road_net: dict,
    ) -> Tuple[IdleArea, RouteEdge] | Tuple[None, None]:
        """
            Поиск ближайшей площадки, соответствующей указанному типу.
            Поиск происходит по графу относительно переданной позиции.
            При наличии запрещённых зон для проезда поиск будет вестись с учётом этих зон.

            При отсутствии проезда к площадке из-за запретных зон будет выбрана другая ближайшая площадка при наличии
            к ней проезда.

            Возвращает кортеж: площадка, маршрут на графе к площадке
        """
        areas = self.get_areas(area_type=area_type)

        best_area = None
        best_route = None
        if areas:
            best_length = None

            # Определяем ближайшую площадку по длине пути на графе
            for area in areas:
                # ищем кратчайший маршрут в объезд запретных зон
                route = find_route_edges_around_restricted_zones_from_position_to_object(
                    lon=lon,
                    lat=lat,
                    edge_idx=edge_idx,
                    to_object_id=area.id,
                    to_object_type=ObjectType.IDLE_AREA,
                    restricted_zones=restricted_zones or [],
                    road_net=road_net,
                )
                if route:
                    length = sum([edge.length for edge in route.edges])

                    if best_length is None or length < best_length:
                        best_area = area
                        best_route = route
                        best_length = length

        return best_area, best_route