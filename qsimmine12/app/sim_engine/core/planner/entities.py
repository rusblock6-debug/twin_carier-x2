from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List


@dataclass
class InputPlanningData:
    N: int  # количество самосвалов
    M: int  # количество экскаваторов
    Z: int  # количество площадок разгрузки
    D_work: int  # длительность смены (мин)

    # Матрицы/словари времени:
    T_haul: Dict[Tuple[int, int, int], int]  # ключ (i,j,z)
    T_return: Dict[Tuple[int, int, int], int]  # ключ (i,j,z)
    T_load: Dict[Tuple[int, int], int]  # ключ (i,j)
    T_unload: Dict[Tuple[int, int], int]  # ключ (i,z)
    T_start: Dict[Tuple[int, int], int]  # ключ (i,j)
    T_end: Dict[Tuple[int, int], int]  # ключ (i,z)

    # тоннаж на рейс
    m_tons: Dict[Tuple[int, int], float]  # ключ (i,j)

    # верхняя граница числа рейсов для каждого самосвала
    Kmax_by_truck: Optional[Dict[int, int]] = None

    # Удобные множества ID
    @property
    def truck_ids(self) -> List[int]:
        return sorted({i for (i, _) in self.T_load.keys()})

    @property
    def shovel_ids(self) -> List[int]:
        return sorted({j for (_, j) in self.T_load.keys()})

    @property
    def unload_ids(self) -> List[int]:
        return sorted({z for (_, z) in self.T_unload.keys()})