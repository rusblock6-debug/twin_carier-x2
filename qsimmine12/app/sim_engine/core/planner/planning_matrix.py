from app.sim_engine.core.calculations.shovel import ShovelCalc
from app.sim_engine.core.calculations.truck import TruckCalc
from app.sim_engine.core.calculations.unload import UnloadCalc
from app.sim_engine.core.geometry import build_route_edges_by_road_net_from_position, build_route_edges_by_road_net
from app.sim_engine.core.planner.entities import InputPlanningData
from app.sim_engine.core.props import SimData
from app.sim_engine.enums import ObjectType


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