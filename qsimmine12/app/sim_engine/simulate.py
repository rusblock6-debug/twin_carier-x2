import functools
import logging
import multiprocessing
from typing import Callable

from app.sim_engine.core.environment import QSimEnvironment
from app.sim_engine.core.geometry import Point, Route, RouteEdge, build_route_by_road_net, build_route_edges_by_road_net
from app.sim_engine.core.props import SimData, PlannedTrip
from app.sim_engine.core.simulations.fuel_station import FuelStation
from app.sim_engine.core.simulations.quarry import Quarry
from app.sim_engine.core.simulations.shovel import Shovel
from app.sim_engine.core.simulations.truck import Truck
from app.sim_engine.core.simulations.unload import Unload
from app.sim_engine.enums import ObjectType
from app.sim_engine.reliability import assess_stability, calc_reliability, find_closest_result
from app.sim_engine.writer import IWriter, DictReliabilityWriter

logger = logging.getLogger(__name__)


class DataValidateError(Exception):
    pass


def sim_data_validate(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except KeyError as e:
            missing_field = e.args[0]
            error = f"ERROR! missing required argument in data: {missing_field}"
            raise DataValidateError(error)

    return wrapper


@sim_data_validate
def run_simulation(
        sim_data: SimData,
        writer: IWriter,
        sim_conf: dict,
) -> dict:
    """
    Run simulation with manual truck routes

    This func needs to be **picklable** for `run_reliability` (multiprocessing limitations)
    """

    env = QSimEnvironment(
        sim_data=sim_data,
        writer=writer,
        sim_conf=sim_conf,
    )

    quarry = Quarry()
    quarry.sim_data = sim_data
    quarry.planned_trips = {}

    quarry.prepare_seeded_random()
    writer.update_data("meta", seed=quarry.sim_data.seed)

    # --- Экскаваторы ---
    sim_shovels_map: dict[int, Shovel] = {}
    for shovel in sim_data.shovels.values():
        shovel_sim = Shovel(
            unit_id=shovel.id,
            name=shovel.name,
            position=Point(shovel.initial_lat, shovel.initial_lon),
            properties=shovel.properties,
            quarry=quarry
        )
        sim_shovels_map[shovel.id] = shovel_sim

    quarry.shovel_map = sim_shovels_map

    # --- Пункты разгрузки ---
    sim_unloads_map: dict[int, Unload] = {}
    for unload in sim_data.unloads.values():
        unl_sim = Unload(
            properties=unload.properties,
            unit_id=unload.id,
            name=unload.name,
            quarry=quarry,
        )
        sim_unloads_map[unload.id] = unl_sim

    quarry.unload_map = sim_unloads_map

    # --- Заправочные станции ---
    sim_fuel_stations: list[FuelStation] = []
    for fs in sim_data.fuel_stations.values():
        fs_sim = FuelStation(
            properties=fs.properties,
            unit_id=fs.id,
            name=fs.name,
            initial_position=Point(fs.initial_lat, fs.initial_lon),
        )
        sim_fuel_stations.append(fs_sim)

    # --- Зона пересменки ---
    shift_change_area = sim_data.idle_areas.shift_change_areas[0]
    quarry.shift_change_area = shift_change_area

    # --- Маршруты и привязки грузовиков ---
    truck_route_map: dict[int, tuple[Route, RouteEdge, RouteEdge, Shovel, Unload]] = {}
    for route in getattr(sim_data, "routes", []) or []:

        route_sim = build_route_by_road_net(route.shovel_id, route.unload_id, sim_data.road_net)
        route_edge = build_route_edges_by_road_net(
            from_object_id=route.shovel_id,
            from_object_type=ObjectType.SHOVEL,
            to_object_id=route.unload_id,
            to_object_type=ObjectType.UNLOAD,
            road_net=sim_data.road_net
        )
        # route_sim = build_route_sim(route)

        shift_start_route = build_route_edges_by_road_net(
            from_object_id=shift_change_area.id,
            from_object_type=ObjectType.IDLE_AREA,
            to_object_id=route.shovel_id,
            to_object_type=ObjectType.SHOVEL,
            road_net=sim_data.road_net
        )

        shovel_sim = sim_shovels_map[route.shovel_id]
        unl_sim = sim_unloads_map[route.unload_id]
        for truck_id in route.truck_ids:
            truck_route_map[truck_id] = (route_sim, route_edge, shift_start_route, shovel_sim, unl_sim)

    # --- Самосвалы ---
    for truck in sim_data.trucks.values():
        props = truck.properties
        if truck.id not in truck_route_map:
            continue
        route, route_edge, shift_start_route, shovel_sim, unl_sim = truck_route_map[truck.id]
        Truck(
            unit_id=truck.id,
            name=truck.name,
            initial_position=Point(truck.initial_lat, truck.initial_lon),
            route=route,
            route_edge=route_edge,
            start_route=shift_start_route,
            planned_trips=[PlannedTrip(truck_id=truck.id, shovel_id=shovel_sim.id, unload_id=unl_sim.id, order=1)],
            quarry=quarry,
            shovel=shovel_sim,
            unload=unl_sim,
            properties=props,
            fuel_stations=sim_fuel_stations
        )

    env.run(until=sim_data.duration)
    logger.info("[done] Симуляция завершена")
    result = writer.finalize()
    result["summary"] = quarry.get_summary(sim_data.end_time)

    return result


def run_simulation_for_planned_trips(
        sim_data: SimData,
        writer: IWriter,
        planned_trips: dict[int, list[PlannedTrip]],
        sim_conf: dict,
) -> dict:
    """
    Run simulation with auto truck routes

    This func needs to be **picklable** for `run_reliability` (multiprocessing limitations)
    """

    env = QSimEnvironment(
        sim_data=sim_data,
        writer=writer,
        sim_conf=sim_conf,
    )

    quarry = Quarry()
    quarry.sim_data = sim_data
    quarry.planned_trips = planned_trips

    quarry.prepare_seeded_random()
    writer.update_data("meta", seed=quarry.sim_data.seed)

    # --- Экскаваторы ---
    sim_shovels_map: dict[int, Shovel] = {}
    for shovel in sim_data.shovels.values():
        shovel_sim = Shovel(
            unit_id=shovel.id,
            name=shovel.name,
            position=Point(shovel.initial_lat, shovel.initial_lon),
            properties=shovel.properties,
            quarry=quarry
        )
        sim_shovels_map[shovel.id] = shovel_sim

    quarry.shovel_map = sim_shovels_map
    env.sim_context.shovels = sim_shovels_map

    # --- Пункты разгрузки ---
    sim_unloads_map: dict[int, Unload] = {}
    for unload in sim_data.unloads.values():
        unl_sim = Unload(
            properties=unload.properties,
            unit_id=unload.id,
            name=unload.name,
            quarry=quarry
        )
        sim_unloads_map[unload.id] = unl_sim

    quarry.unload_map = sim_unloads_map
    env.sim_context.unloads = sim_unloads_map

    # --- Заправочные станции ---
    sim_fuel_stations: list[FuelStation] = []
    for fs in sim_data.fuel_stations.values():
        fs_sim = FuelStation(
            properties=fs.properties,
            unit_id=fs.id,
            name=fs.name,
            initial_position=Point(fs.initial_lat, fs.initial_lon),
        )
        sim_fuel_stations.append(fs_sim)

    # --- Зона пересменки ---
    quarry.shift_change_area = sim_data.idle_areas.shift_change_areas[0]

    # --- Самосвалы ---
    sim_truck_map: dict[int, Truck] = {}
    for truck in sim_data.trucks.values():
        props = truck.properties

        sim_truck = Truck(
            unit_id=truck.id,
            name=truck.name,
            initial_position=Point(truck.initial_lat, truck.initial_lon),
            route=None,
            route_edge=None,
            start_route=None,
            planned_trips=planned_trips.get(truck.id, []),
            quarry=quarry,
            shovel=None,
            unload=None,
            properties=props,
            fuel_stations=sim_fuel_stations,
        )
        sim_truck_map[truck.id] = sim_truck
    quarry.truck_map = sim_truck_map
    env.sim_context.trucks = sim_truck_map

    env.run(until=sim_data.duration)
    logger.info("[done] Симуляция завершена")
    result = writer.finalize()
    result["summary"] = quarry.get_summary(sim_data.end_time)

    return result


def run_reliability(
        run_func: Callable,
        sim_data: SimData,
        writer: IWriter,
        sim_conf: dict,
        *extra_run_func_args: tuple,
        metric: str = "weight",
        processes_number: int | None = None,
        init_runs_number: int = 15,
        step_runs_number: int = 15,
        max_runs_number: int = 105,
        alpha: float = 0.05,
        r_target: float = 0.05,
        delta_target: float = 0.01,
        consecutive: int = 2,
        boot_b: int = 5000,
) -> dict:
    """
    Run given simulation engaging reliablility calculation

    `run_func` needs to be **picklable** (multiprocessing limitations)
    """
    if processes_number is None:
        processes = int(multiprocessing.cpu_count() / 2)
    else:
        processes = processes_number

    logger.info('run_reliability', {
        'func': f"{run_func.__name__}",
        'metric': f"{metric}",
        'proc': f"{processes}",
        'init': f"{init_runs_number}",
        'step': f"{step_runs_number}",
        'max': f"{max_runs_number}",
        'alpha': f"{alpha}",
        'r_target': f"{r_target}",
        'd_target': f"{delta_target}",
        'consec': f"{consecutive}",
        'boot_b': f"{boot_b}",
    })

    next_runs_number = init_runs_number
    prev_metric_median = None
    cur_stable_streak = 0

    go_for_more = True
    all_results = []

    ctx = multiprocessing.get_context("spawn")
    with ctx.Pool(processes=processes) as pool:
        while go_for_more:
            starmap_args_list = [
                (sim_data, DictReliabilityWriter(), sim_conf, *extra_run_func_args)
                for i in range(next_runs_number)
            ]
            logger.info(f"Run {next_runs_number} simulations on {processes} processes")
            attempt_results = pool.starmap(run_func, starmap_args_list)
            logger.info("Finished executing simulations")
            all_results.extend(attempt_results)

            is_stable, metric_array, metric_median, stable_streak = assess_stability(
                all_results,
                metric=metric,
                prev_metric_median=prev_metric_median,
                cur_stable_streak=cur_stable_streak,
                alpha=alpha,
                r_target=r_target,
                delta_target=delta_target,
                consecutive=consecutive,
            )

            if is_stable or len(all_results) >= max_runs_number:
                logger.info("Achieved stability or exceeded max results number")
                go_for_more = False
            else:
                logger.info("Going to next attempt to achieve stability")
                next_runs_number = step_runs_number
                prev_metric_median = metric_median
                cur_stable_streak = stable_streak

    logger.info("Calc reliable metric")
    metric_reliable, metric_best_min, metric_best_max = calc_reliability(
        metric_array, alpha=alpha, boot_b=boot_b
    )

    logger.info("Find result closest to reliable metric")
    closest_result = find_closest_result(all_results, metric_reliable, metric_best_max, metric)

    sim_data.seed = closest_result["meta"]["seed"]

    logger.info(f"Reproduce closest result by seed: {sim_data.seed}")

    final_result = run_func(sim_data, writer, sim_conf, *extra_run_func_args)
    final_result["summary"][f"{metric}_reliable"] = round(metric_reliable)
    final_result["summary"][f"{metric}_best_min"] = round(metric_best_min)
    final_result["summary"][f"{metric}_best_max"] = round(metric_best_max)
    final_result["summary"]["is_stable"] = is_stable
    final_result["summary"]["confidence_interval"] = (1 - alpha) * 100
    fsum = final_result["summary"]

    logger.info('final summary', {
        'result': f"{metric} {fsum[metric]}",
        'reliable': f"{fsum[f"{metric}_reliable"]}",
        'best_min': f"{fsum[f"{metric}_best_min"]}",
        'best_max': f"{fsum[f"{metric}_best_max"]}",
        'is_stable': f"{fsum["is_stable"]}",
        'confidence_interval': f"{fsum["confidence_interval"]}",
    })

    return final_result
