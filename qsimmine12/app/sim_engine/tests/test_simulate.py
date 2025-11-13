"""
PYTEST_DONT_REWRITE
"""

import json
import math
import os

import pytest

from app.sim_engine.enums import ObjectType
from app.sim_engine.simulation_manager import SimulationManager
from app.sim_engine.writer import DictSimpleWriter

USE_MULTIPROCESSING = True

@pytest.fixture
def input_data():
    # Пусть run_sim_data_base.json лежит рядом с этим тестом
    current_dir = os.path.dirname(__file__)
    input_file = os.path.join(current_dir, "run_sim_data_base.json")
    with open(input_file, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_result(result: dict):
    # Проверяем наличие ключей
    assert "summary" in result
    assert "summary" in result
    assert "telemetry" in result

    summary = result["summary"]
    assert isinstance(summary["trips"], int)
    assert isinstance(summary["volume"], (int, float))
    assert isinstance(summary["weight"], (int, float))

    assert "chart_volume_data" in summary
    assert "chart_trip_data" in summary
    assert "trucks_count" in summary
    assert "shovels_count" in summary

    assert isinstance(summary["chart_volume_data"], list)
    assert isinstance(summary["chart_trip_data"], list)

    # Проверим структуру первой записи графика
    if summary["chart_volume_data"]:
        v = summary["chart_volume_data"][0]
        assert "time" in v and "value" in v

    total_trips_count = summary["trips"]
    total_weight = summary["weight"]
    total_volume = summary["volume"]

    real_chart_trips_count = 0
    real_trips_count = 0
    real_weight = 0
    real_volume = 0
    real_chart_volume = 0

    for trip in summary["chart_trip_data"]:
        real_chart_trips_count += trip["value"]

    for trip in summary["chart_volume_data"]:
        real_chart_volume += trip["value"]

    for trip in summary["trips_table"]:
        real_trips_count += 1
        real_weight += trip["weight"]
        real_volume += trip["volume"]

    assert real_chart_trips_count == total_trips_count

    # пока что в поле volume на самом деле вес
    assert math.floor(real_chart_volume) == total_weight, f"{math.floor(real_chart_volume)} != {total_weight}"

    assert total_trips_count == real_trips_count
    assert math.floor(real_weight) == total_weight
    assert math.floor(real_volume) == total_volume


def test_simulation_result(input_data):
    result = SimulationManager(use_multiprocessing=USE_MULTIPROCESSING, raw_data=input_data, writer=DictSimpleWriter, options={'mode': 'auto'}).run()
    validate_result(result)
    shovel_telemetry = [i for i in result["telemetry"] if i["object_type"] == ObjectType.SHOVEL.key()]

    assert isinstance(shovel_telemetry, list)
    for row in shovel_telemetry[::1000]:

        assert isinstance(row, dict)
        assert len(row.keys()) == 9
        assert isinstance(row["object_id"], str)
        assert isinstance(row["object_name"], str)
        assert isinstance(row["object_type"], str)
        assert isinstance(row["lat"], float)
        assert isinstance(row["lon"], float)
        assert isinstance(row["state"], str)
        assert isinstance(row["timestamp"], float)
        assert isinstance(row["loading_truck"], str)
        if row["loading_truck"]:
            assert isinstance(row["loading_truck"][0], str)
        assert isinstance(row["trucks_queue"], list)
        if row["trucks_queue"]:
            assert isinstance(row["trucks_queue"][0], str)


def test_shovel_telemetry(input_data):
    result = SimulationManager(use_multiprocessing=USE_MULTIPROCESSING, raw_data=input_data, writer=DictSimpleWriter, options={'mode': 'auto'}).run()
    validate_result(result)
    shovel_telemetry = [i for i in result["telemetry"] if i["object_type"] == ObjectType.SHOVEL.key()]

    assert isinstance(shovel_telemetry, list)
    for row in shovel_telemetry[::1000]:

        assert isinstance(row, dict)
        assert len(row.keys()) == 9
        assert isinstance(row["object_id"], str)
        assert isinstance(row["object_name"], str)
        assert isinstance(row["object_type"], str)
        assert isinstance(row["lat"], float)
        assert isinstance(row["lon"], float)
        assert isinstance(row["state"], str)
        assert isinstance(row["timestamp"], float)
        assert isinstance(row["loading_truck"], str)
        if row["loading_truck"]:
            assert isinstance(row["loading_truck"][0], str)
        assert isinstance(row["trucks_queue"], list)
        if row["trucks_queue"]:
            assert isinstance(row["trucks_queue"][0], str)


def test_truck_telemetry(input_data):
    result = SimulationManager(use_multiprocessing=USE_MULTIPROCESSING, raw_data=input_data, writer=DictSimpleWriter, options={'mode': 'auto'}).run()
    validate_result(result)
    shovel_telemetry = [i for i in result["telemetry"] if i["object_type"] == ObjectType.TRUCK.key()]

    assert isinstance(shovel_telemetry, list)
    for row in shovel_telemetry[::1000]:
        assert isinstance(row, dict)
        assert len(row.keys()) == 10
        assert isinstance(row["object_id"], str)
        assert isinstance(row["object_name"], str)
        assert isinstance(row["object_type"], str)
        assert isinstance(row["lat"], float) or row["lat"] == 0
        assert isinstance(row["lon"], float) or row["lon"] == 0
        assert isinstance(row["speed"], int) or isinstance(row["speed"], float)
        assert isinstance(row["weight"], int) or isinstance(row["weight"], float)
        assert isinstance(row["fuel"], int) or isinstance(row["fuel"], float)
        assert isinstance(row["state"], str)
        assert isinstance(row["timestamp"], float)


def test_unload_telemetry(input_data):
    result = SimulationManager(use_multiprocessing=USE_MULTIPROCESSING, raw_data=input_data, writer=DictSimpleWriter, options={'mode': 'auto'}).run()
    validate_result(result)
    shovel_telemetry = [i for i in result["telemetry"] if i["object_type"] == ObjectType.UNLOAD.key()]

    assert isinstance(shovel_telemetry, list)
    for row in shovel_telemetry[::1000]:

        assert isinstance(row, dict)
        assert len(row.keys()) == 6
        assert isinstance(row["object_id"], str)
        assert isinstance(row["object_type"], str)
        assert isinstance(row["timestamp"], float)
        assert isinstance(row["state"], str)
        assert isinstance(row["unloading_trucks"], list)
        if row["unloading_trucks"]:
            assert isinstance(row["unloading_trucks"][0], str)
        assert isinstance(row["trucks_queue"], list)
        if row["trucks_queue"]:
            assert isinstance(row["trucks_queue"][0], str)


def test_fuel_station_telemetry(input_data):
    result = SimulationManager(use_multiprocessing=USE_MULTIPROCESSING, raw_data=input_data, writer=DictSimpleWriter, options={'mode': 'auto'}).run()
    validate_result(result)
    shovel_telemetry = [i for i in result["telemetry"] if i["object_type"] == ObjectType.FUEL_STATION.key()]

    assert isinstance(shovel_telemetry, list)
    for row in shovel_telemetry[::1000]:

        assert isinstance(row, dict)
        assert len(row.keys()) == 6
        assert isinstance(row["object_id"], str)
        assert isinstance(row["object_type"], str)
        assert isinstance(row["timestamp"], float)
        assert isinstance(row["state"], str)
        assert isinstance(row["refuelling_trucks"], list)
        if row["refuelling_trucks"]:
            assert isinstance(row["refuelling_trucks"][0], str)
        assert isinstance(row["trucks_queue"], list)
        if row["trucks_queue"]:
            assert isinstance(row["trucks_queue"][0], str)


def test_summary_result(input_data):
    config = {"breakdown": False, "refuel": False, 'lunch': False, 'planned_idle': False, 'blasting': False,
              'mode': 'auto'}
    result = SimulationManager(use_multiprocessing=USE_MULTIPROCESSING, raw_data=input_data, writer=DictSimpleWriter, options=config).run()
    validate_result(result)
    summary = result["summary"]
    del summary['trips_table']
    del summary['trucks_needed']

    result = {
        'trips': 19,
        'volume': 2150,
        'weight': 3221,
        'chart_volume_data': [
            {'time': '11:00', 'value': 1921},
            {'time': '12:00', 'value': 1300}
        ],
        'chart_trip_data': [
            {'time': '11:00', 'value': 11},
            {'time': '12:00', 'value': 8}
        ],
        'trucks_count': 5,
        'shovels_count': 2
    }

    assert summary == result


def test_events(input_data):
    config = {"breakdown": True, "refuel": True, 'lunch': True, 'planned_idle': False, 'blasting': False,
              'mode': 'auto'}
    result = SimulationManager(use_multiprocessing=USE_MULTIPROCESSING, raw_data=input_data, writer=DictSimpleWriter, options=config).run()
    validate_result(result)

    events = result["events"]
    assert len(events) > 0

    assert isinstance(events, list)
    for event in events[::100]:
        assert isinstance(event, dict)
        assert isinstance(event["event_code"], int)
        assert isinstance(event["event_name"], str)
        assert isinstance(event["time"], float)
        assert isinstance(event["object_id"], str)
        assert isinstance(event["object_type"], str)
        assert isinstance(event["object_name"], str)

        match (event["event_code"]):
            case 3 | 4:
                assert len(event.keys()) == 8
            case _:
                assert len(event.keys()) == 6


def test_summary_result_with_breakdown(input_data):
    config = {"breakdown": True, "refuel": False, 'lunch': False, 'planned_idle': False, 'blasting': False,
              'mode': 'auto'}
    result = SimulationManager(use_multiprocessing=USE_MULTIPROCESSING, raw_data=input_data, writer=DictSimpleWriter, options=config).run()
    validate_result(result)
    summary = result["summary"]
    del summary['trips_table']
    del summary['trucks_needed']

    result = result = {
        'trips': 19,
        'volume': 2150,
        'weight': 3221,
        'chart_volume_data': [
            {'time': '11:00', 'value': 1921},
            {'time': '12:00', 'value': 1300}
        ],
        'chart_trip_data': [
            {'time': '11:00', 'value': 11},
            {'time': '12:00', 'value': 8}
        ],
        'trucks_count': 5,
        'shovels_count': 2
    }
    assert summary != result
    assert 0 < summary["trips"] < result["trips"]
    assert 0 < summary["volume"] < result["volume"]
    assert 0 < summary["weight"] < result["weight"]


def test_breakdown_events_count(input_data):
    config = {"breakdown": True, "refuel": False, 'lunch': False, 'planned_idle': False, 'blasting': False,
              'mode': 'auto'}
    result = SimulationManager(use_multiprocessing=USE_MULTIPROCESSING, raw_data=input_data, writer=DictSimpleWriter, options=config).run()
    validate_result(result)
    assert len(result["events"]) > 0


def test_summary_result_with_refuel(input_data):
    config = {"breakdown": False, "refuel": True, 'lunch': False, 'planned_idle': False, 'blasting': False,
              'mode': 'auto'}
    result = SimulationManager(use_multiprocessing=USE_MULTIPROCESSING, raw_data=input_data, writer=DictSimpleWriter, options=config).run()
    validate_result(result)
    summary = result["summary"]
    del summary['trips_table']
    del summary['trucks_needed']

    result = result = {
        'trips': 19,
        'volume': 2150,
        'weight': 3221,
        'chart_volume_data': [
            {'time': '11:00', 'value': 1921},
            {'time': '12:00', 'value': 1300}
        ],
        'chart_trip_data': [
            {'time': '11:00', 'value': 11},
            {'time': '12:00', 'value': 8}
        ],
        'trucks_count': 5,
        'shovels_count': 2
    }
    assert summary != result
    assert 0 < summary["trips"] < result["trips"]
    assert 0 < summary["volume"] < result["volume"]
    assert 0 < summary["weight"] < result["weight"]


def test_refuel_events_count(input_data):
    config = {"breakdown": False, "refuel": True, "lunch": False, 'planned_idle': False, 'blasting': False,
              'mode': 'auto'}
    result = SimulationManager(use_multiprocessing=USE_MULTIPROCESSING, raw_data=input_data, writer=DictSimpleWriter, options=config).run()
    validate_result(result)
    assert len(result["events"]) == 10


def test_summary_result_with_lunch(input_data):
    config = {"breakdown": False, "refuel": False, 'lunch': True, 'planned_idle': False, 'blasting': False,
              'mode': 'auto'}
    result = SimulationManager(use_multiprocessing=USE_MULTIPROCESSING, raw_data=input_data, writer=DictSimpleWriter, options=config).run()
    validate_result(result)
    summary = result["summary"]
    del summary['trips_table']
    del summary['trucks_needed']

    result = result = {
        'trips': 19,
        'volume': 2150,
        'weight': 3221,
        'chart_volume_data': [
            {'time': '11:00', 'value': 1921},
            {'time': '12:00', 'value': 1300}
        ],
        'chart_trip_data': [
            {'time': '11:00', 'value': 11},
            {'time': '12:00', 'value': 8}
        ],
        'trucks_count': 5,
        'shovels_count': 2
    }
    assert summary != result
    assert 0 < summary["trips"] < result["trips"]
    assert 0 < summary["volume"] < result["volume"]
    assert 0 < summary["weight"] < result["weight"]


def test_lunch_events_count(input_data):
    config = {"breakdown": False, "refuel": False, 'lunch': True, 'planned_idle': False, 'blasting': False,
              'mode': 'auto'}
    result = SimulationManager(use_multiprocessing=USE_MULTIPROCESSING, raw_data=input_data, writer=DictSimpleWriter, options=config).run()
    validate_result(result)
    assert len(result["events"]) == 5


def test_summary_result_with_planned_idle(input_data):
    config = {"breakdown": False, "refuel": False, 'lunch': False, 'planned_idle': True, 'blasting': False,
              'mode': 'auto'}
    result = SimulationManager(use_multiprocessing=USE_MULTIPROCESSING, raw_data=input_data, writer=DictSimpleWriter, options=config).run()
    validate_result(result)
    summary = result["summary"]
    del summary['trips_table']
    del summary['trucks_needed']

    result = {
        'trips': 19,
        'volume': 2150,
        'weight': 3221,
        'chart_volume_data': [
            {'time': '11:00', 'value': 1921},
            {'time': '12:00', 'value': 1300}
        ],
        'chart_trip_data': [
            {'time': '11:00', 'value': 11},
            {'time': '12:00', 'value': 8}
        ],
        'trucks_count': 5,
        'shovels_count': 2
    }
    assert summary != result
    assert 0 < summary["trips"] < result["trips"]
    assert 0 < summary["volume"] < result["volume"]
    assert 0 < summary["weight"] < result["weight"]


def test_planned_idle_events_count(input_data):
    config = {"breakdown": False, "refuel": False, 'lunch': False, 'planned_idle': True, 'blasting': False,
              'mode': 'auto'}
    result = SimulationManager(use_multiprocessing=USE_MULTIPROCESSING, raw_data=input_data, writer=DictSimpleWriter, options=config).run()
    validate_result(result)
    assert len(result["events"]) == 4


def test_blasting_events_count(input_data):
    config = {"breakdown": False, "refuel": False, 'lunch': False, 'planned_idle': False, 'blasting': True,
              'mode': 'auto'}
    result = SimulationManager(use_multiprocessing=USE_MULTIPROCESSING, raw_data=input_data, writer=DictSimpleWriter, options=config).run()
    validate_result(result)
    assert len(result["events"]) == 4


def test_auto_mode_summary_result(input_data):
    config = {"breakdown": False, "refuel": True, 'lunch': True, 'planned_idle': True, 'blasting': False,
              'mode': 'auto'}
    result = SimulationManager(use_multiprocessing=USE_MULTIPROCESSING, raw_data=input_data, writer=DictSimpleWriter, options=config).run()
    validate_result(result)
    summary = result["summary"]
    del summary['trips_table']
    del summary['trucks_needed']

    result = {
        'trips': 19,
        'volume': 2150,
        'weight': 3221,
        'chart_volume_data': [
            {'time': '11:00', 'value': 1921},
            {'time': '12:00', 'value': 1300}
        ],
        'chart_trip_data': [
            {'time': '11:00', 'value': 11},
            {'time': '12:00', 'value': 8}
        ],
        'trucks_count': 5,
        'shovels_count': 2
    }

    assert 0 < summary['trips'] <= result['trips']
    assert 0 < summary['volume'] <= result['volume']
    assert 0 < summary['weight'] <= result['weight']
