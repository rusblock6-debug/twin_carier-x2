import json
import logging
import os

from app.sim_engine.enums import ObjectType
from app.sim_engine.simulation_manager import SimulationManager

# Путь к файлам
current_dir = os.path.dirname(__file__)
input_file = os.path.join(current_dir, "run_sim_data.json")
output_telemetry_file = os.path.join(current_dir, "telemetry.json")
output_events_file = os.path.join(current_dir, "events.json")
output_schedule_file = os.path.join(current_dir, "schedule.csv")

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Чтение и парсинг JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    scenario = data.get("scenario", {})
    mode = "auto" if scenario and scenario["is_auto_truck_distribution"] else "manual"

    # Подготавливаем и вызываем работу симуляции
    manager = SimulationManager(raw_data=data, options={
        'mode': mode,
        # 'reliability_calc_enabled': True,
    })

    result = manager.run()

    summary = result["summary"]
    events = result["events"]
    logger.info(f"Рейсов: {summary["trips"]}")
    logger.info(f"Объем: {summary["volume"]}")
    logger.info(f"Масса: {summary["weight"]}")
    hourly_volume = " | ".join([f"{i["time"]}: {i["value"]}" for i in summary["chart_volume_data"]])
    hourly_trip = " | ".join([f"{i["time"]}: {i["value"]}" for i in summary["chart_trip_data"]])
    logger.info(f"Почасовой объем: {hourly_volume}")
    logger.info(f"Почасовые рейсы: {hourly_trip}")
    logger.info("Таблица рейсов:")
    # for trip in summary["trips_table"]:
    #     logger.info(trip)

    #  Если нужно сохранить телеметрию или события
    truck_telemetry = [
        i for i in result["telemetry"] if i["object_type"] == ObjectType.TRUCK.key() and i["object_id"] == "1_truck"
    ]
    #
    # fuel_station_telemetry = [
    #     i for i in result["telemetry"] if i["object_type"] == ObjectType.FUEL_STATION.key() and i["object_id"] == "1_fuel_station"
    # ]

    # with open(output_telemetry_file, "w", encoding="utf-8") as f:
    #     json.dump(truck_telemetry, f, ensure_ascii=False, indent=2)
    # #
    # with open(output_events_file, "w", encoding="utf-8") as f:
    #     json.dump(events, f, ensure_ascii=False, indent=2)
