from enum import Enum


class TruckState(Enum):
    MOVING_EMPTY = ("moving_empty", "Движение порожним")
    LOADING = ("loading", "Погрузка")
    MOVING_LOADED = ("moving_loaded", "Движение груженым")
    UNLOADING = ("unloading", "Разгрузка")
    IDLE = ("idle", "Простой")
    REPAIR = ('repair', "Ремонт")
    WAITING = ("waiting", "Ожидание")
    REFUELING = ('refueling', "Заправка")
    LUNCH = ('lunch', 'Обед')
    PLANNED_IDLE = ('planned_idle', 'Плановый простой (Ремонт, ТО и т.д.)')
    BLASTING_IDLE = ('blasting_idle', 'Ожидание проведения взрывных работ')

    @property
    def is_work(self):
        return self in [self.MOVING_LOADED, self.MOVING_EMPTY, self.UNLOADING]

    @property
    def is_moving(self):
        return self in [self.MOVING_LOADED, self.MOVING_EMPTY]

    def __str__(self):
        return self.value[0]  # По умолчанию — английский

    def ru(self):
        return self.value[1]

    def en(self):
        return self.value[0]


class ExcState(Enum):
    LOADING = ("loading", "Погрузка")
    WAITING = ("waiting", "Ожидание")
    REPAIR = ("repair", "Ремонт")
    PLANNED_IDLE = ("planned_idle", "Плановый простой (Ремонт, ТО и т.д.)")
    BLASTING_IDLE = ('blasting_idle', 'Ожидание проведения взрывных работ')

    @property
    def is_work(self):
        return self == self.LOADING

    def __str__(self):
        return self.value[0]  # По умолчанию — английский

    def ru(self):
        return self.value[1]

    def en(self):
        return self.value[0]


class UnloadState(Enum):
    OPEN = ("open", "Открыт")
    CLOSED = ("closed", "Закрыт")
    REPAIR = ('repair', "Ремонт")
    BLASTING_IDLE = ('blasting_idle', 'Ожидание проведения взрывных работ')

    @property
    def is_work(self):
        return self == self.OPEN

    def __str__(self):
        return self.value[0]  # По умолчанию — английский

    def ru(self):
        return self.value[1]

    def en(self):
        return self.value[0]


class FuelStationState(Enum):
    REFUELING = ("refueling", "Заправка")
    WAITING = ("waiting", "Ожидание")

    def __str__(self):
        return self.value[0]  # По умолчанию — английский

    def ru(self):
        return self.value[1]

    def en(self):
        return self.value[0]