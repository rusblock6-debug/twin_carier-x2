import functools
import logging
import multiprocessing
from abc import ABC, abstractmethod
from typing import Callable

from app.sim_engine.core.environment import QSimEnvironment
from app.sim_engine.core.geometry import Point, Route, RouteEdge, build_route_by_road_net, build_route_edges_by_road_net
from app.sim_engine.core.props import SimData, PlannedTrip, IdleArea
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


class AbstractSimulation(ABC):
    def __init__(self, sim_data: SimData, writer: IWriter, sim_conf: dict) -> None:
        self._sim_data = sim_data
        self._writer = writer
        self._sim_conf = sim_conf

        self._sim_shovels_map: dict[int, Shovel] = {}
        self._sim_unloads_map: dict[int, Unload] = {}
        self._sim_fuel_stations: list[FuelStation] = []

        self._shift_change_area: IdleArea | None = None
        self._env: QSimEnvironment | None = None
        self._quarry: Quarry | None = None

    def run(self) -> dict:
        self._env = QSimEnvironment(
            sim_data=self._sim_data,
            writer=self._writer,
            sim_conf=self._sim_conf,
        )

        self._quarry = Quarry()
        self._quarry.sim_data = self._sim_data
        self._quarry.prepare_seeded_random()

        self._writer.update_data("meta", seed=self._quarry.sim_data.seed)

        self._handle_simulation_setup()

        self._env.run(until=self._sim_data.duration)

        logger.info("[done] Симуляция завершена")
        result = self._writer.finalize()
        result["summary"] = self._quarry.get_summary(self._sim_data.end_time)

        return result

    @abstractmethod
    def _handle_simulation_setup(self) -> None:
        raise NotImplementedError

    def _init_sim_shovels_map(self) -> None:
        # --- Экскаваторы ---
        self._sim_shovels_map: dict[int, Shovel] = {}

        for shovel in self._sim_data.shovels.values():
            shovel_sim = Shovel(
                unit_id=shovel.id,
                name=shovel.name,
                position=Point(shovel.initial_lat, shovel.initial_lon),
                properties=shovel.properties,
                quarry=self._quarry,
            )
            self._sim_shovels_map[shovel.id] = shovel_sim

        self._quarry.shovel_map = self._sim_shovels_map
        self._env.sim_context.shovels = self._sim_shovels_map

    def _init_sim_unloads_map(self) -> None:
        # --- Пункты разгрузки ---
        self._sim_unloads_map: dict[int, Unload] = {}

        for unload in self._sim_data.unloads.values():
            unl_sim = Unload(
                properties=unload.properties,
                unit_id=unload.id,
                name=unload.name,
                quarry=self._quarry,
            )
            self._sim_unloads_map[unload.id] = unl_sim

        self._quarry.unload_map = self._sim_unloads_map
        self._env.sim_context.unloads = self._sim_unloads_map

    def _init_sim_fuel_stations(self) -> None:
        # --- Заправочные станции ---
        self._sim_fuel_stations: list[FuelStation] = []
        for fs in self._sim_data.fuel_stations.values():
            fs_sim = FuelStation(
                properties=fs.properties,
                unit_id=fs.id,
                name=fs.name,
                initial_position=Point(fs.initial_lat, fs.initial_lon),
            )
            self._sim_fuel_stations.append(fs_sim)

    def _init_shift_change_area(self) -> None:
        # --- Зона пересменки ---
        shift_change_area = self._sim_data.idle_areas.shift_change_areas[0]
        self._quarry.shift_change_area = shift_change_area
        self._shift_change_area = shift_change_area


class Simulation(AbstractSimulation):
    def __init__(self, sim_data: SimData, writer: IWriter, sim_conf: dict) -> None:
        super().__init__(sim_data, writer, sim_conf)
        self._truck_route_map: dict[int, tuple[Route, RouteEdge, RouteEdge, Shovel, Unload]] = {}

    def _handle_simulation_setup(self) -> None:
        """
        Run simulation with manual truck routes

        This func needs to be **picklable** for `run_reliability` (multiprocessing limitations)
        """
        self._quarry.planned_trips = {}

        self._init_sim_shovels_map()
        self._init_sim_unloads_map()
        self._init_sim_fuel_stations()
        self._init_shift_change_area()

        self.__init_truck_route_map()
        self.__init_trucks()

    def __init_truck_route_map(self) -> None:
        # --- Маршруты и привязки грузовиков ---
        self._truck_route_map: dict[int, tuple[Route, RouteEdge, RouteEdge, Shovel, Unload]] = {}

        for route in getattr(self._sim_data, "routes", []) or []:
            route_sim = build_route_by_road_net(route.shovel_id, route.unload_id, self._sim_data.road_net)
            route_edge = build_route_edges_by_road_net(
                from_object_id=route.shovel_id,
                from_object_type=ObjectType.SHOVEL,
                to_object_id=route.unload_id,
                to_object_type=ObjectType.UNLOAD,
                road_net=self._sim_data.road_net
            )
            # route_sim = build_route_sim(route)

            shift_start_route = build_route_edges_by_road_net(
                from_object_id=self._shift_change_area.id,
                from_object_type=ObjectType.IDLE_AREA,
                to_object_id=route.shovel_id,
                to_object_type=ObjectType.SHOVEL,
                road_net=self._sim_data.road_net
            )

            shovel_sim = self._sim_shovels_map[route.shovel_id]
            unl_sim = self._sim_unloads_map[route.unload_id]
            for truck_id in route.truck_ids:
                self._truck_route_map[truck_id] = (route_sim, route_edge, shift_start_route, shovel_sim, unl_sim)

    def __init_trucks(self) -> None:
        # --- Самосвалы ---
        for truck in self._sim_data.trucks.values():
            props = truck.properties
            if truck.id not in self._truck_route_map:
                continue
            route, route_edge, shift_start_route, shovel_sim, unl_sim = self._truck_route_map[truck.id]
            Truck(
                unit_id=truck.id,
                name=truck.name,
                initial_position=Point(truck.initial_lat, truck.initial_lon),
                route=route,
                route_edge=route_edge,
                start_route=shift_start_route,
                planned_trips=[PlannedTrip(truck_id=truck.id, shovel_id=shovel_sim.id, unload_id=unl_sim.id, order=1)],
                quarry=self._quarry,
                shovel=shovel_sim,
                unload=unl_sim,
                properties=props,
                fuel_stations=self._sim_fuel_stations
            )


class PlannedTripsSimulation(AbstractSimulation):
    def __init__(
            self,
            sim_data: SimData,
            writer: IWriter,
            sim_conf: dict,
            planned_trips: dict[int, list[PlannedTrip]],
    ) -> None:
        super().__init__(sim_data, writer, sim_conf)
        self._planned_trips = planned_trips
        self._sim_truck_map: dict[int, Truck] = {}

    def _handle_simulation_setup(self) -> None:
        """
        Run simulation with auto truck routes

        This func needs to be **picklable** for `run_reliability` (multiprocessing limitations)
        """
        self._quarry.planned_trips = self._planned_trips

        self._init_sim_shovels_map()
        self._init_sim_unloads_map()
        self._init_sim_fuel_stations()
        self._init_shift_change_area()

        self.__init_trucks()

    def __init_trucks(self) -> None:
        # --- Самосвалы ---
        self._sim_truck_map: dict[int, Truck] = {}

        for truck in self._sim_data.trucks.values():
            props = truck.properties

            sim_truck = Truck(
                unit_id=truck.id,
                name=truck.name,
                initial_position=Point(truck.initial_lat, truck.initial_lon),
                route=None,
                route_edge=None,
                start_route=None,
                planned_trips=self._planned_trips.get(truck.id, []),
                quarry=self._quarry,
                shovel=None,
                unload=None,
                properties=props,
                fuel_stations=self._sim_fuel_stations,
            )
            self._sim_truck_map[truck.id] = sim_truck

        self._quarry.truck_map = self._sim_truck_map
        self._env.sim_context.trucks = self._sim_truck_map


class Reliability:
    def __init__(
            self,
            simulation_closure: Callable,
            sim_data: SimData,
            writer: IWriter,
            sim_conf: dict,
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
            planned_trips: dict | None = None,
    ) -> None:
        self.simulation_closure = simulation_closure
        self.sim_data = sim_data
        self.writer = writer
        self.sim_conf = sim_conf
        self.metric = metric
        self.processes_number = processes_number
        self.init_runs_number = init_runs_number
        self.step_runs_number = step_runs_number
        self.max_runs_number = max_runs_number
        self.alpha = alpha
        self.r_target = r_target
        self.delta_target = delta_target
        self.consecutive = consecutive
        self.boot_b = boot_b
        self.planned_trips = planned_trips

        if processes_number is None:
            self.processes = int(multiprocessing.cpu_count() / 2)
        else:
            self.processes = processes_number

    def run(self) -> dict:
        """
        Run given simulation engaging reliability calculation

        `run_func` needs to be **picklable** (multiprocessing limitations)
        """
        logger.info('run_reliability', {
            'simulation_closure': f"{self.simulation_closure.__name__}",
            'metric': f"{self.metric}",
            'proc': f"{self.processes}",
            'init': f"{self.init_runs_number}",
            'step': f"{self.step_runs_number}",
            'max': f"{self.max_runs_number}",
            'alpha': f"{self.alpha}",
            'r_target': f"{self.r_target}",
            'd_target': f"{self.delta_target}",
            'consec': f"{self.consecutive}",
            'boot_b': f"{self.boot_b}",
        })

        next_runs_number = self.init_runs_number
        prev_metric_median = None
        cur_stable_streak = 0

        go_for_more = True
        all_results = []

        ctx = multiprocessing.get_context("spawn")
        with ctx.Pool(processes=self.processes) as pool:
            while go_for_more:
                starmap_args_list = [self._make_closure_args() for _ in range(next_runs_number)]
                logger.info(f"Run {next_runs_number} simulations on {self.processes} processes")

                attempt_results = pool.starmap(self.simulation_closure, starmap_args_list)
                logger.info("Finished executing simulations")
                all_results.extend(attempt_results)

                is_stable, metric_array, metric_median, stable_streak = assess_stability(
                    all_results,
                    metric=self.metric,
                    prev_metric_median=prev_metric_median,
                    cur_stable_streak=cur_stable_streak,
                    alpha=self.alpha,
                    r_target=self.r_target,
                    delta_target=self.delta_target,
                    consecutive=self.consecutive,
                )

                if is_stable or len(all_results) >= self.max_runs_number:
                    logger.info("Achieved stability or exceeded max results number")
                    go_for_more = False
                else:
                    logger.info("Going to next attempt to achieve stability")
                    next_runs_number = self.step_runs_number
                    prev_metric_median = metric_median
                    cur_stable_streak = stable_streak

        logger.info("Calc reliable metric")
        metric_reliable, metric_best_min, metric_best_max = calc_reliability(
            metric_array, alpha=self.alpha, boot_b=self.boot_b
        )

        logger.info("Find result closest to reliable metric")
        closest_result = find_closest_result(all_results, metric_reliable, metric_best_max, self.metric)

        self.sim_data.seed = closest_result["meta"]["seed"]

        logger.info(f"Reproduce closest result by seed: {self.sim_data.seed}")

        args = self._make_closure_args(writer=self.writer)
        final_result = self.simulation_closure(*args)
        final_result["summary"][f"{self.metric}_reliable"] = round(metric_reliable)
        final_result["summary"][f"{self.metric}_best_min"] = round(metric_best_min)
        final_result["summary"][f"{self.metric}_best_max"] = round(metric_best_max)
        final_result["summary"]["is_stable"] = is_stable
        final_result["summary"]["confidence_interval"] = (1 - self.alpha) * 100
        fsum = final_result["summary"]

        logger.info('final summary', {
            'result': f"{self.metric} {fsum[self.metric]}",
            'reliable': f"{fsum[f"{self.metric}_reliable"]}",
            'best_min': f"{fsum[f"{self.metric}_best_min"]}",
            'best_max': f"{fsum[f"{self.metric}_best_max"]}",
            'is_stable': f"{fsum["is_stable"]}",
            'confidence_interval': f"{fsum["confidence_interval"]}",
        })

        return final_result

    def _make_closure_args(self, writer: IWriter = DictReliabilityWriter()) -> tuple:
        if self.planned_trips is not None:
            return self.sim_data, writer, self.sim_conf, self.planned_trips
        return self.sim_data, writer, self.sim_conf


@sim_data_validate
def run_simulation(
        sim_data: SimData,
        writer: IWriter,
        sim_conf: dict,
) -> dict:
    simulation = Simulation(sim_data, writer, sim_conf)
    return simulation.run()


@sim_data_validate
def run_simulation_for_planned_trips(
        sim_data: SimData,
        writer: IWriter,
        sim_conf: dict,
        planned_trips: dict[int, list[PlannedTrip]],
) -> dict:
    simulation = PlannedTripsSimulation(sim_data, writer, sim_conf, planned_trips)
    return simulation.run()
