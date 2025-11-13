import json
from datetime import datetime, timedelta

from app.sim_engine.core.props import TruckProperties, ShovelProperties, UnlProperties, FuelStationProperties, Truck, \
    Shovel, Unload, FuelStation, SimData, Route, Segment, Point, ShiftChangeArea, Blasting, PlannedIdle, \
    IdleAreaStorage, IdleArea
from app.utils import utc_to_enterprise, TZ


# считаем, что все твои датаклассы уже импортированы:
# ShovelProperties, Shovel, UnlProperties, Unload,
# FuelStationProperties, FuelStation, TruckProperties, Truck
# + ваша утилита времени:
# from your_time_utils import utc_to_enterprise


def calculate_lunch_breaks(
        start_time: datetime,
        end_time: datetime,
        shift_config: list[dict],
        lunch_break_offset: int,
        lunch_break_duration: int
):
    """
    Расчитывает обеденные перерывы в заданном временном интервале
    """
    lunch_breaks = []

    # Начинаем анализ за день до start_time, чтобы захватить ночные смены
    analysis_start_day = (start_time - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    analysis_end_day = end_time.replace(hour=0, minute=0, second=0, microsecond=0)

    current_day = analysis_start_day
    while current_day <= analysis_end_day:
        # Для каждой смены в конфигурации
        for shift in shift_config:
            # Определяем начало и конец смены для текущего дня
            shift_start = current_day + timedelta(minutes=shift["begin_offset"])

            # Вычисляем обед для этой смены
            lunch_start = shift_start + timedelta(minutes=lunch_break_offset)
            lunch_end = lunch_start + timedelta(minutes=lunch_break_duration)

            # Проверяем, пересекается ли обед с нашим временным интервалом
            if lunch_end > start_time and lunch_start < end_time:
                # Обрезаем по границам интервала
                actual_lunch_start = max(lunch_start, start_time)
                actual_lunch_end = min(lunch_end, end_time)

                if actual_lunch_start < actual_lunch_end:
                    # Проверяем, что обед не дублируется
                    if not any(abs((lb[0] - actual_lunch_start).total_seconds()) < 60 for lb in lunch_breaks):
                        lunch_breaks.append(
                            (actual_lunch_start, actual_lunch_end)
                        )

        # Переходим к следующему дню
        current_day += timedelta(days=1)

    # Сортируем по времени начала
    lunch_breaks.sort(key=lambda x: x[0])

    return lunch_breaks


def collect_planned_idles(idles_data: list[dict]):
    """
        Организует список плановых простоев в словарь,
        сгруппированный по vehicle_type и vehicle_id,
        с сортировкой по start_time.

        Args:
            idles_data (list): Список словарей с информацией о простоях

        Returns:
            dict: Словарь вида {(vehicle_type, vehicle_id): [sorted_downtimes]}}
        """
    result = {}

    for idle in idles_data:
        vehicle_key = (idle["vehicle_type"], idle["vehicle_id"])

        if vehicle_key not in result:
            result[vehicle_key] = []

        start_time = idle["start_time"].isoformat() if isinstance(idle["start_time"], datetime) else idle["start_time"]
        end_time = idle["end_time"].isoformat() if isinstance(idle["end_time"], datetime) else idle["end_time"]

        # Добавляем текущий простой в список
        result[vehicle_key].append(
            PlannedIdle(
                id=idle["id"],
                vehicle_type=idle["vehicle_type"],
                start_time=utc_to_enterprise(start_time),
                end_time=utc_to_enterprise(end_time),
                quarry_id=idle["quarry_id"],
                vehicle_id=idle["vehicle_id"],
            )
        )

    # Сортируем списки по start_time
    for idles in result.values():
        idles.sort(key=lambda x: x.start_time)

    return result


def create_blasting_list(data: dict, timezone: str = TZ) -> list[Blasting]:
    """
    Создает список объектов Blasting из данных взрывных работ.

    Args:
        data: Словарь с данными взрывных работ
        timezone: Часовой пояс

    Returns:
        List[Blasting]: Отсортированный по start_time список объектов Blasting
    """
    blasting_list = []

    for item in data:
        zones = []
        for feature in item["geojson_data"]["features"]:
            if feature["geometry"]["type"] == "Polygon":
                coordinates = feature["geometry"]["coordinates"][0]
                zones.append(coordinates)

        start_time = item["start_time"].isoformat() if isinstance(item["start_time"], datetime) else item["start_time"]
        end_time = item["end_time"].isoformat() if isinstance(item["end_time"], datetime) else item["end_time"]

        blasting = Blasting(
            id=item["id"],
            zones=zones,
            start_time=utc_to_enterprise(start_time, timezone),
            end_time=utc_to_enterprise(end_time, timezone),
        )
        blasting_list.append(blasting)

    # Сортировка по start_time
    blasting_list.sort(key=lambda x: x.start_time)

    return blasting_list


def transform_road_net_3d_to_2d(road_net: dict):
    for feature in road_net["features"]:
        geometry = feature['geometry']

        if geometry['type'] == 'LineString':
            coords = []
            for coord in feature["geometry"]["coordinates"]:
                coords.append([coord[0], coord[1], 0.0])
            geometry["coordinates"] = coords
        if geometry['type'] == 'Point':
            coords = geometry["coordinates"]
            geometry["coordinates"] = [coords[0], coords[1], 0.0]
    return road_net


class SimDataSerializer:
    """Преобразует входной dict (как в run_simulation) в набор датаклассов."""

    @classmethod
    def serialize(cls, data: dict) -> SimData:
        # --- время ---
        timezone = data["quarry"]["timezone"]
        start_time = utc_to_enterprise(data["start_time"], timezone)
        end_time = utc_to_enterprise(data["end_time"], timezone)
        seconds = int((end_time - start_time).total_seconds())

        # --- зерно рандома ---
        if data.get('seed') is None:
            # будет сгенерировано в начале симуляции
            seed = None
        else:
            # предопределено
            seed = int(data['seed'])

        # --- экскаваторы ---
        shovels: dict[int, Shovel] = {}
        for raw in data["quarry"].get("shovel_list", []):
            shovel_props = ShovelProperties(
                obem_kovsha_m3=raw["bucket_volume"],
                skorost_podem_m_s=raw["bucket_lift_speed"],
                skorost_povorot_rad_s=raw["arm_turn_speed"],
                skorost_vrezki_m_s=raw["bucket_dig_speed"],
                skorost_napolneniya_m_s=raw["bucket_fill_speed"],
                koef_zapolneniya=raw.get("bucket_fill_coef", 0.8),
                tip_porody=raw.get("payload_type", "sand"),
                koef_vozvrata=raw.get("return_move_coef", 0.85),
                initial_operating_time=raw.get("initial_operating_time", 12),
                average_repair_duration=raw.get("average_repair_duration", 8),
                initial_failure_count=raw.get("initial_failure_count", 100),
                # оставшиеся коэфы — со своими датакласс-дефолтами
            )
            shovels[raw["id"]] = Shovel(
                id=raw["id"],
                name=raw["name"],
                initial_lat=raw["initial_lat"],
                initial_lon=raw["initial_lon"],
                properties=shovel_props,
            )

        # --- пункты разгрузки ---
        unloads: dict[int, Unload] = {}
        for raw in data["quarry"].get("unload_list", []):
            unl_props = UnlProperties(
                angle=raw["angle"],
                material_type=raw.get("payload_type", "unknown"),
                type_unloading=raw["unload_type"],
                trucks_at_once=raw.get("trucks_at_once", 100),
                initial_operating_time=raw.get("initial_operating_time", 24),
                average_repair_duration=raw.get("average_repair_duration", 24),
                initial_failure_count=raw.get("initial_failure_count", 50),
            )
            unloads[raw["id"]] = Unload(
                    id=raw["id"],
                    name=raw["name"],
                    properties=unl_props,
                )

        # --- заправки ---
        fuel_stations: dict[int, FuelStation] = {}
        for raw in data["quarry"].get("fuel_station_list", []):
            fs_props = FuelStationProperties(
                num_pumps=raw["num_pumps"],
                flow_rate=raw["flow_rate"],
            )
            fuel_stations[raw["id"]] = FuelStation(
                id=raw["id"],
                name=raw["name"],
                initial_lat=raw["initial_lat"],
                initial_lon=raw["initial_lon"],
                properties=fs_props,
            )

        # --- Зоны пересменки ---
        idle_areas: list[IdleArea] = []
        for raw in data["quarry"].get("idle_area_list", []):
            area = IdleArea(
                id=raw["id"],
                name=raw["name"],
                initial_lat=raw["initial_lat"],
                initial_lon=raw["initial_lon"],
                is_shift_change_area=raw["is_shift_change_area"],
                is_lunch_area=raw["is_lunch_area"],
                is_blast_waiting_area=raw["is_blast_waiting_area"],
                is_planned_idle_area=raw["is_repair_area"]
            )
            idle_areas.append(area)
        idle_areas_storage = IdleAreaStorage(areas=idle_areas)

        # --- самосвалы ---
        trucks: dict[int, Truck] = {}
        for raw in data["quarry"].get("truck_list", []):
            truck_props = TruckProperties(
                body_capacity=raw["body_capacity"],
                speed_empty_kmh=raw["speed_empty"],
                speed_loaded_kmh=raw["speed_loaded"],
                initial_operating_time=raw.get("initial_operating_time", 12),
                average_repair_duration=raw.get("average_repair_duration", 4),
                initial_failure_count=raw.get("initial_failure_count", 50),
                # топливо
                fuel_capacity=raw["fuel_capacity"],
                fuel_threshold_critical=raw["fuel_threshold_critical"],
                fuel_threshold_planned=raw["fuel_threshold_planned"],
                fuel_level=raw["fuel_level"],
                fuel_idle_lph=raw["fuel_idle_lph"],
                fuel_specific_consumption=raw["fuel_specific_consumption"],
                fuel_density=raw["fuel_density"],
                engine_power_kw=raw["engine_power_kw"],
                # acceleration/skill — остаются дефолтами датакласса, либо можно raw.get(...)
            )
            trucks[raw["id"]] = Truck(
                id=raw["id"],
                name=raw["name"],
                initial_lat=raw["initial_lat"],
                initial_lon=raw["initial_lon"],
                properties=truck_props,
                initial_edge_id=None
            )

        # --- маршруты ---
        routes: list[Route] = []
        for raw in data["quarry"].get("trail_list", []):
            segments = [
                Segment(
                    start=Point(lat=s["start"][0], lon=s["start"][1]),
                    end=Point(lat=s["end"][0], lon=s["end"][1]),
                )
                for s in raw["segments"]
            ]
            routes.append(
                Route(
                    id=raw["id"],
                    segments=segments,
                    shovel_id=raw["shovel_id"],
                    unload_id=raw["unload_id"],
                    truck_ids=raw.get("trucks", []),
                )
            )

        # --- обеды ---
        lunch_times = []
        if data["quarry"].get("lunch_break_offset") and data["quarry"].get("lunch_break_duration"):
            lunch_times = calculate_lunch_breaks(
                start_time=start_time,
                end_time=end_time,
                shift_config=data["quarry"].get("shift_config", []),
                lunch_break_offset=data["quarry"].get("lunch_break_offset"),
                lunch_break_duration=data["quarry"].get("lunch_break_duration"),
            )

        # --- плановые простои ---
        planned_idles = {}
        idles_data = data["quarry"].get("schedules", {}).get('planned_idle')
        if idles_data:
            planned_idles = collect_planned_idles(idles_data)

        # --- взрывные работы ---
        blasting_list = []
        blasting_data = data["quarry"].get("schedules", {}).get('blasting')
        if blasting_data:
            blasting_list = create_blasting_list(data=blasting_data, timezone=timezone)

        # принудительно приведём граф дорог в 2D координаты, т.к. наша симуляция пока что умеет работать только в 2D
        # TODO: убрать, когда научим симуляцию работать с 3D координатами
        road_net = transform_road_net_3d_to_2d(data["quarry"]["road_net"])

        # Примечание: trail_list/маршруты здесь намеренно не собираем —
        # твои «чистые» датаклассы их не содержат. Если нужно — добавим
        # отдельные dataclass'ы и поля в SimData.
        return SimData(
            start_time=start_time,
            end_time=end_time,
            duration=seconds,
            seed=seed,
            trucks=trucks,
            shovels=shovels,
            unloads=unloads,
            fuel_stations=fuel_stations,
            routes=routes,
            road_net=road_net,
            idle_areas=idle_areas_storage,
            lunch_times=lunch_times,
            planned_idles=planned_idles,
            blasting_list=blasting_list,

            target_shovel_load=data["quarry"].get("target_shovel_load", 0.9),
        )
