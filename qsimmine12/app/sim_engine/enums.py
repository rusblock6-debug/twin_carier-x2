import enum


class ObjectType(enum.Enum):
    TRUCK = (1, 'truck', 'Самосвал')
    SHOVEL = (2, 'shovel', 'Экскаватор')
    UNLOAD = (3, 'unload', 'Зона разгрузки')
    QUARRY = (4, 'quarry', 'Карьер')
    IDLE_AREA = (5, 'idle_area', 'Площадка пересменки')
    FUEL_STATION = (6, 'fuel_station', 'Заправка')
    BLASTING = (7, 'blasting', 'Взрывные работы')

    def __str__(self):
        return self.key()  # По умолчанию — английский

    def ru(self) -> str:
        return self.value[2]

    def key(self) -> str:
        return self.value[1]

    def code(self) -> int:
        return self.value[0]


class IdleAreaType(enum.Enum):
    SHIFT_CHANGE = (1, 'shift_change', 'Площадка пересменки')
    PLANNED_IDLE = (2, 'planned_idle', 'Площадка ремонта')
    LUNCH = (3, 'lunch', 'Площадка обеда')
    BLAST_WAITING = (4, 'blast_waiting', 'Площадка ожидания взрывных работ')

    def __str__(self):
        return self.key()  # По умолчанию — английский

    def ru(self) -> str:
        return self.value[2]

    def key(self) -> str:
        return self.value[1]

    def code(self) -> int:
        return self.value[0]


class SolverType(enum.Enum):
    GREEDY = (1, 'GREEDY')
    CBC = (2, 'CBC')
    HIGHS = (3, 'HIGHS')
    CP = (4, 'CP')

    def __str__(self):
        return self.key()

    def key(self) -> str:
        return self.value[1]

    def code(self) -> int:
        return self.value[0]

    @classmethod
    def from_code(cls, code: int) -> 'SolverType':
        for member in cls:
            if member.code() == code:
                return member
        raise KeyError(f"Unknown solver code {code}")
