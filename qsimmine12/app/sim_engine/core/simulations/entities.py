from dataclasses import dataclass

from app.sim_engine.core.simulations.quarry import Quarry
from app.sim_engine.core.simulations.shovel import Shovel
from app.sim_engine.core.simulations.truck import Truck
from app.sim_engine.core.simulations.unload import Unload


@dataclass
class SimContext:
    """
    Контекст(контейнер) содержащий в себе объекты симуляции
    """
    quarry: Quarry = None
    trucks: dict[int, Truck] = None
    shovels: dict[int, Shovel] = None
    unloads: dict[int, Unload] = None

    # writers: dict[str, Any]
    # random_seed: int

    def get_truck_by_id(self, truck_id: int):
        return self.trucks[truck_id]

    def get_shovel_by_id(self, shovel_id: int):
        return self.shovels[shovel_id]

    def get_unload_by_id(self, unload_id: int):
        return self.unloads[unload_id]
