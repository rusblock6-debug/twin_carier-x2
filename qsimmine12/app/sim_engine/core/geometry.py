import math
import copy
from dataclasses import dataclass
from typing import Tuple

from roadnet.core import Edge, Vertex, RoadNetFactory

from app.sim_engine.core.props import Route as SimRoute, SimData
from app.sim_engine.enums import ObjectType


@dataclass
class Point:
    lat: float
    lon: float


class Route:
    def __init__(self, name: str, points: list[Point]):
        self.name = name
        self.points = points

    @property
    def start(self):
        return self.points[0]

    @property
    def end(self):
        return self.points[-1]


class RouteEdge:

    @staticmethod
    def _reverse(edges):
        reversed_edges = []
        for edge in reversed(edges):
            rev_edge = copy.deepcopy(edge)
            rev_edge.start, rev_edge.stop = edge.stop, edge.start
            reversed_edges.append(rev_edge)
        return reversed_edges

    def __init__(self, edges: list[Edge]):
        self.edges = edges
        self.reversed_edges = self._reverse(edges)

    @property
    def start_point(self) -> Vertex:
        return self.edges[0].start

    @property
    def end_point(self) -> Vertex:
        return self.edges[-1].stop

    def move_along_edges_gen(self) -> Edge:
        for edge in self.edges:
            yield edge

    def move_along_edges_reversed_gen(self) -> Edge:
        for edge in self.reversed_edges:
            yield edge


# region Search intersections with polygons

def cross_product(
        o: Tuple[float, float],
        a: Tuple[float, float],
        b: Tuple[float, float]
):
    """Векторное произведение координат"""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def segments_intersect(
        a: Tuple[float, float],
        b: Tuple[float, float],
        c: Tuple[float, float],
        d: Tuple[float, float]
) -> bool:
    """Проверяет, пересекаются ли отрезки AB и CD"""

    def on_segment(a, b, c):
        """Лежит ли точка C на отрезке AB"""
        return (min(a[0], b[0]) <= c[0] <= max(a[0], b[0]) and
                min(a[1], b[1]) <= c[1] <= max(a[1], b[1]))

    # Вычисляем векторные произведения
    d1 = cross_product(c, d, a)
    d2 = cross_product(c, d, b)
    d3 = cross_product(a, b, c)
    d4 = cross_product(a, b, d)

    # Основная проверка пересечения
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True

    # Особые случаи (коллинеарность)
    if d1 == 0 and on_segment(c, d, a):
        return True
    if d2 == 0 and on_segment(c, d, b):
        return True
    if d3 == 0 and on_segment(a, b, c):
        return True
    if d4 == 0 and on_segment(a, b, d):
        return True

    return False


def path_intersects_polygons(path: RouteEdge, polygons: Tuple[Tuple[Tuple[float, float]]] | list[list[list[float]]]):
    """
    Проверяет, попадает ли путь на графе хотя бы в один полигон.

    Args:
        path: объект RouteEdge, хранящий список рёбер пути на графе
        polygons: список полигонов в виде списков координат

    Returns:
        bool: True если путь пересекает или находится внутри хотя бы одного полигона
    """
    # Получаем координаты всех вершин пути
    for edge in path.move_along_edges_gen():
        # Координаты хранятся в атрибутах вершин, доступных через рёбра
        start_coord = (edge.start.x, edge.start.y)
        end_coord = (edge.stop.x, edge.stop.y)

        # проверяем координаты отрезка на отрезках полигона, чтобы понять, пересекли ли мы полигон
        for polygon in polygons:
            for segment in list(zip(polygon, polygon[1:] + polygon[:1])):
                segment_start_coord = segment[0]
                segment_end_coord = segment[1]

                if segments_intersect(start_coord, end_coord, segment_start_coord, segment_end_coord):
                    return True
    return False

#endregion


def build_route_sim(route_dc: SimRoute) -> Route:
    """
    Конвертирует наш dataclass Route (список сегментов)
    в RouteSim (список уникальных точек по порядку).
    """
    points: list = []
    seen = set()
    for seg in route_dc.segments:
        for pt in (seg.start, seg.end):
            key = (pt.lat, pt.lon)
            if key not in seen:
                seen.add(key)
                points.append(Point(pt.lat, pt.lon))  # если Point общий тип
    return Route(route_dc.id, points)


# region Routes building

def build_route_by_road_net(
        shovel_id: int,
        unload_id: int,
        road_net: dict,
) -> Route:
    graph_logic = RoadNetFactory().create_from_geojson(
        geojson_data=road_net,
        is_trustful=True,
    )

    source = (shovel_id, ObjectType.SHOVEL.key())
    target = (unload_id, ObjectType.UNLOAD.key())

    result = graph_logic.search_path_dijkstra(
        source=source,
        target=target,
        # source_edge_idx=0,
    )
    points: list = []
    seen = set()
    for edge in result.edges:
        key = (edge.start.lat, edge.start.lon)
        if key not in seen:
            seen.add(key)
            points.append(Point(*key))

        key = (edge.stop.lat, edge.stop.lon)
        if key not in seen:
            seen.add(key)
            points.append(Point(*key))

    return Route(f"shov_{source[0]} - unl_{target[0]}", points)


def build_route_edges_by_road_net(
        from_object_id: int,
        from_object_type: ObjectType,
        to_object_id: int,
        to_object_type: ObjectType,
        road_net: dict,
) -> RouteEdge:
    graph_logic = RoadNetFactory().create_from_geojson(
        geojson_data=road_net,
        is_trustful=True,
    )

    source = (from_object_id, from_object_type.key())
    target = (to_object_id, to_object_type.key())

    result = graph_logic.search_path_dijkstra(
        source=source,
        target=target,
        # source_edge_idx=0,
    )
    return RouteEdge(result.edges)


def build_route_edges_by_road_net_from_position(
        lon: int | float,
        lat: int | float,
        height: int | None,
        edge_idx: int,
        to_object_id: int,
        to_object_type: ObjectType,
        road_net: dict,
) -> RouteEdge:
    graph_logic = RoadNetFactory().create_from_geojson(
        geojson_data=road_net,
        is_trustful=True,
    )

    source = (lon, lat, height)
    target = (to_object_id, to_object_type.key())

    result = graph_logic.search_path_dijkstra(
        source=source,
        target=target,
        source_edge_idx=edge_idx,
    )
    return RouteEdge(result.edges)


def build_route_edges_by_road_net_from_position_to_position(
        lon: float,
        lat: float,
        height: float | None,
        edge_idx: int,

        end_lon: float,
        end_lat: float,
        end_height: float | None,
        end_edge_idx: int | None,
        road_net: dict
) -> RouteEdge:
    """Строит кратчайший путь на графе от позиции до позиции"""
    graph_logic = RoadNetFactory().create_from_geojson(
        geojson_data=road_net,
        is_trustful=True,
    )

    source = (lon, lat, height)
    target = (end_lon, end_lat, end_height)

    result = graph_logic.search_path_dijkstra(
        source=source,
        target=target,
        source_edge_idx=edge_idx,
        target_edge_idx=end_edge_idx,
    )
    return RouteEdge(result.edges)


def find_all_route_edges_by_road_net_from_position_to_position(
        lon: float,
        lat: float,
        height: float | None,
        edge_idx: int | None,

        end_lon: float,
        end_lat: float,
        end_height: float | None,
        end_edge_idx: int | None,
        road_net: dict
):
    """Ищет все пути на графе от указанной позиции до указанной позиции"""
    graph_logic = RoadNetFactory().create_from_geojson(
        geojson_data=road_net,
        is_trustful=True,
    )

    source = (lon, lat, height)
    target = (end_lon, end_lat, end_height)

    paths = graph_logic.search_all_paths(
        source=source,
        target=target,
        source_edge_idx=edge_idx,
        target_edge_idx=end_edge_idx,
    )

    result = [RouteEdge(path.edges) for path in paths]
    result.sort(key=lambda route: sum([edge.length for edge in route.edges]))
    return result


def find_all_route_edges_by_road_net_from_position(
        lon: float,
        lat: float,
        height: float | None,
        edge_idx: int | None,

        to_object_id: int,
        to_object_type: ObjectType,
        road_net: dict,
):
    """Ищет все пути на графе от указанной позиции до указанного объекта"""
    graph_logic = RoadNetFactory().create_from_geojson(
        geojson_data=road_net,
        is_trustful=True,
    )

    source = (lon, lat, height)
    target = (to_object_id, to_object_type.key())

    paths = graph_logic.search_all_paths(
        source=source,
        target=target,
        source_edge_idx=edge_idx,
    )

    result = [RouteEdge(path.edges) for path in paths]
    result.sort(key=lambda route: sum([edge.length for edge in route.edges]))
    return result


def find_all_route_edges_by_road_net_from_object_to_object(
        from_object_id: int,
        from_object_type: ObjectType,

        to_object_id: int,
        to_object_type: ObjectType,
        road_net: dict,
):
    """Ищет все пути на графе от указанной позиции до указанного объекта"""
    graph_logic = RoadNetFactory().create_from_geojson(
        geojson_data=road_net,
        is_trustful=True,
    )

    source = (from_object_id, from_object_type.key())
    target = (to_object_id, to_object_type.key())

    paths = graph_logic.search_all_paths(
        source=source,
        target=target,
    )

    result = [RouteEdge(path.edges) for path in paths]
    result.sort(key=lambda route: sum([edge.length for edge in route.edges]))
    return result

#endregion


def interpolate_position(p1: Point, p2: Point, ratio: float) -> Point:
    lat = p1.lat + (p2.lat - p1.lat) * ratio
    lon = p1.lon + (p2.lon - p1.lon) * ratio
    return Point(lat, lon)


def haversine_km(p1: Point, p2: Point) -> float:
    R = 6371
    lat1, lon1 = math.radians(p1.lat), math.radians(p1.lon)
    lat2, lon2 = math.radians(p2.lat), math.radians(p2.lon)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def find_nearest_point(point: Point, point_list: list[Point]):
    nearest_point = min(point_list, key=lambda p: haversine_km(point, p))
    return nearest_point



# region Build routes edges around blasting

def find_route_edges_around_restricted_zones_from_position_to_object(
        lon: float,
        lat: float,
        edge_idx: int | None,
        to_object_id: int,
        to_object_type: ObjectType,
        restricted_zones: Tuple[Tuple[Tuple[float, float]]] | list[list[list[float]]],
        road_net: dict
) -> RouteEdge | None:
    """
        Поиск маршрута в объезд запрещённых зон (полигонов) от позиции до объекта
    """
    # Строим маршрут к зоне ожидания
    all_routes = find_all_route_edges_by_road_net_from_position(
        lon=lon,
        lat=lat,
        height=None,
        edge_idx=edge_idx,
        to_object_id=to_object_id,
        to_object_type=to_object_type,
        road_net=road_net,
    )

    # Маршруты отсортированы по длине, выберем первый, не попадающий в запрещённые зоны
    chosen_route = None
    for route in all_routes:
        if not path_intersects_polygons(route, restricted_zones):
            chosen_route = route
            break

    return chosen_route


def find_route_edges_around_restricted_zones_from_position_to_position(
        lon: float,
        lat: float,
        edge_idx: int | None,
        end_lon: float,
        end_lat: float,
        end_edge_idx: int | None,
        restricted_zones: Tuple[Tuple[Tuple[float, float]]] | list[list[list[float]]],
        road_net: dict
) -> RouteEdge | None:
    """
        Поиск маршрута в объезд запрещённых зон (полигонов) от позиции до объекта
    """
    # Строим маршрут к зоне ожидания
    all_routes = find_all_route_edges_by_road_net_from_position_to_position(
        lon=lon,
        lat=lat,
        height=None,
        edge_idx=edge_idx,
        end_lon=end_lon,
        end_lat=end_lat,
        end_height=None,
        end_edge_idx=end_edge_idx,
        road_net=road_net,
    )

    # Маршруты отсортированы по длине, выберем первый, не попадающий в запрещённые зоны
    chosen_route = None
    for route in all_routes:
        if not path_intersects_polygons(route, restricted_zones):
            chosen_route = route
            break

    return chosen_route

# endregion
