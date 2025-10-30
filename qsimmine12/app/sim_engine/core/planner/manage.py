import logging
from collections import defaultdict

from app.sim_engine.core.calculations.shovel import ShovelCalc
from app.sim_engine.core.calculations.truck import TruckCalc
from app.sim_engine.core.calculations.unload import UnloadCalc
from app.sim_engine.core.geometry import build_route_edges_by_road_net_from_position, build_route_edges_by_road_net
from app.sim_engine.core.planner.entities import InputPlanningData
from app.sim_engine.core.planner.solvers.cp import CPSolver
from app.sim_engine.core.planner.solvers.milp import MILPSolver
from app.sim_engine.core.props import SimData, PlannedTrip
from app.sim_engine.enums import ObjectType

logger = logging.getLogger(__name__)


class Planner:
    SOLVERS = {
        "CBC": MILPSolver,
        "HIGHS": MILPSolver,
        "CP": CPSolver
    }

    def __init__(
            self,
            solver: str = None,
            msg: bool = False,
            workers: int = 4,
            time_limit: int = 60
    ):
        self.msg = msg
        self.workers = workers
        self.time_limit = time_limit
        self.solver = solver

    def _init_solver(self):
        if self.solver:
            solver = self.SOLVERS[self.solver]
        else:
            solver = self.SOLVERS["CP"]

        if self.solver == "HIGHS":
            solver.solver_type = "HIGHS"
        elif self.solver == "CBC":
            solver.solver_type = "CBC"

        solver.time_limit = self.time_limit
        solver.msg_out = self.msg
        solver.workers = self.workers

        return solver

    @staticmethod
    def get_planning_data(simdata: SimData) -> InputPlanningData:
        """
        Метод набивающий матрицу данных
        """
        truck_count = len(simdata.trucks)
        shovel_count = len(simdata.shovels)
        unl_count = len(simdata.unloads)
        shift_change_area = simdata.idle_areas.shift_change_areas[0]

        planning_data = InputPlanningData(
            N=truck_count,
            M=shovel_count,
            Z=unl_count,
            D_work=int(simdata.duration / 60),

            T_haul=dict(),
            T_return=dict(),
            T_load=dict(),
            T_unload=dict(),
            T_start=dict(),
            T_end=dict(),
            m_tons=dict(),

            Kmax_by_truck=None
        )

        # Идем по самосвалам
        for truck in simdata.trucks.values():

            # Идем по экскаваторам
            for shovel in simdata.shovels.values():
                time_load, weight, _ = ShovelCalc.calculate_load_cycles(shovel.properties, truck.properties)

                planning_data.T_load[
                    truck.id,
                    shovel.id
                ] = int(time_load / 60)

                if truck.initial_edge_id and truck.initial_lat and truck.initial_lon:
                    start_route = build_route_edges_by_road_net_from_position(
                        lon=truck.initial_lon,
                        lat=truck.initial_lat,
                        edge_idx=truck.initial_edge_id,
                        height=None,
                        to_object_id=shovel.id,
                        to_object_type=ObjectType.SHOVEL,
                        road_net=simdata.road_net,
                    )

                else:
                    start_route = build_route_edges_by_road_net(
                        from_object_id=shift_change_area.id,
                        from_object_type=ObjectType.IDLE_AREA,
                        to_object_id=shovel.id,
                        to_object_type=ObjectType.SHOVEL,
                        road_net=simdata.road_net
                    )

                planning_data.T_start[
                    truck.id,
                    shovel.id
                ] = int(TruckCalc.calculate_time_motion_by_edges(
                    start_route,
                    truck.properties,
                    forward=True
                ) / 60)

                planning_data.m_tons[
                    truck.id,
                    shovel.id
                ] = int(weight)

                # Идем по пунктам разгрузки
                for unload in simdata.unloads.values():
                    route = build_route_edges_by_road_net(
                        from_object_id=shovel.id,
                        from_object_type=ObjectType.SHOVEL,
                        to_object_id=unload.id,
                        to_object_type=ObjectType.UNLOAD,
                        road_net=simdata.road_net
                    )
                    planning_data.T_haul[
                        truck.id,
                        shovel.id,
                        unload.id
                    ] = int(TruckCalc.calculate_time_motion_by_edges(
                        route,
                        truck.properties,
                        forward=True
                    ) / 60)

                    planning_data.T_return[
                        truck.id,
                        unload.id,
                        shovel.id
                    ] = int(TruckCalc.calculate_time_motion_by_edges(
                        route,
                        truck.properties,
                        forward=False
                    ) / 60)

            # Идем по пунктам разгрузки
            for unload in simdata.unloads.values():
                planning_data.T_unload[
                    truck.id,
                    unload.id
                ] = int(UnloadCalc.unload_calculation_by_norm(unload.properties, truck.properties)["t_total"] / 60)

                end_route = build_route_edges_by_road_net(
                    from_object_id=unload.id,
                    from_object_type=ObjectType.UNLOAD,
                    to_object_id=shift_change_area.id,
                    to_object_type=ObjectType.IDLE_AREA,
                    road_net=simdata.road_net
                )

                planning_data.T_end[
                    truck.id,
                    unload.id
                ] = int(TruckCalc.calculate_time_motion_by_edges(
                    end_route,
                    truck.properties,
                    forward=True
                ) / 60)

        return planning_data

    def run_with_exclude(
            self,
            sim_data: SimData,
            exclude_objects: dict[str, list[int]],
    ) -> dict:

        if self.msg:
            logger.info(f"Planner run_with_exclude!")

        sim_data.duration = int((sim_data.end_time - sim_data.start_time).total_seconds())

        exclude_trucks = exclude_objects["trucks"]
        exclude_shovels = exclude_objects["shovels"]
        exclude_unloads = exclude_objects["unloads"]

        for truck_id in exclude_trucks:
            sim_data.trucks.pop(truck_id, None)

        for shovel_id in exclude_shovels:
            sim_data.shovels.pop(shovel_id, None)

        for unload_id in exclude_unloads:
            sim_data.unloads.pop(unload_id, None)

        if not sim_data.shovels or not sim_data.unloads or not sim_data.trucks:
            return {}

        result = self.run(simdata=sim_data)
        planned_trips = defaultdict(list)

        for trip in result["trips"]:
            planned_trip = PlannedTrip(
                truck_id=trip["truck_id"],
                shovel_id=trip["shovel_id"],
                unload_id=trip["unload_id"],
                order=trip["order"]
            )
            planned_trips[planned_trip.truck_id].append(planned_trip)
        return planned_trips

    def run(self, simdata: SimData):
        if self.msg:
            logger.info(f"Planner run!")

        planning_data = self.get_planning_data(simdata)

        if self.msg:
            logger.info(f"Planning data: {planning_data}")

        solver = self._init_solver()
        result = solver.run(planning_data)

        if self.msg:
            for trip in result["trips"]:
                if trip["order"] == 1:
                    logger.info("-------------------------")
                logger.info(
                    f"Самосвал: {trip["truck_id"]}; Экскаватор: {trip["shovel_id"]}; ПР: {trip["unload_id"]}; Рейс № {trip["order"]}"
                )
        return result
