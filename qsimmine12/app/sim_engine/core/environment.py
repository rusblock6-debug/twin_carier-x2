import simpy

from app.sim_engine.core.planner.solvers.greedy import GreedySolver
from app.sim_engine.core.props import SimData
from app.sim_engine.core.simulations.entities import SimContext
from app.sim_engine.core.simulations.utils.idle_area_service import IdleAreaService
from app.sim_engine.core.simulations.utils.statistic_service import StatisticService
from app.sim_engine.core.simulations.utils.service_locator import ServiceLocator
from app.sim_engine.core.simulations.utils.trip_service import TripService
from app.sim_engine.writer import IWriter


class QSimEnvironment(simpy.Environment):
    def __init__(self, sim_data: SimData, writer: IWriter, sim_conf: dict):
        super().__init__()

        self.sim_data = sim_data
        self.sim_context: SimContext = SimContext()

        ServiceLocator.unbind_all()

        ServiceLocator.bind('sim_env', self)
        ServiceLocator.bind('writer', writer)
        ServiceLocator.bind('sim_conf', sim_conf)
        ServiceLocator.bind('solver', GreedySolver())
        ServiceLocator.bind('trip_service', TripService())
        ServiceLocator.bind('idle_area_service', IdleAreaService(self.sim_data.idle_areas))
        ServiceLocator.bind(
            'statistic_service',
            StatisticService()
        )
