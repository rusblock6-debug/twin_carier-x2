from typing import TYPE_CHECKING, Any

from app.sim_engine.core.simulations.utils.service_locator import ServiceLocator

if TYPE_CHECKING:
    from app.sim_engine.writer import IWriter
    from app.sim_engine.core.environment import QSimEnvironment
    from app.sim_engine.core.planner.solvers.greedy import GreedySolver
    from app.sim_engine.core.simulations.utils.trip_service import TripService
    from app.sim_engine.core.simulations.utils.idle_area_service import IdleAreaService
    from app.sim_engine.core.simulations.utils.statistic_service import StatisticService


class DependencyResolver:
    @classmethod
    def sim_conf(cls) -> dict:
        return cls.__resolve('sim_conf')

    @classmethod
    def writer(cls) -> 'IWriter':
        return cls.__resolve('writer')

    @classmethod
    def solver(cls) -> 'GreedySolver':
        return cls.__resolve('solver')

    @classmethod
    def trip_service(cls) -> 'TripService':
        return cls.__resolve('trip_service')

    @classmethod
    def idle_area_service(cls) -> 'IdleAreaService':
        return cls.__resolve('idle_area_service')

    @classmethod
    def statistic_service(cls) -> 'StatisticService':
        return cls.__resolve('statistic_service')

    @classmethod
    def env(cls) -> 'QSimEnvironment':
        return cls.__resolve('sim_env')

    @staticmethod
    def __resolve(alias: str) -> Any:
        return ServiceLocator.get_or_fail(alias)
