import json
import pathlib
from datetime import datetime
from typing import Any, List, Optional

from fastapi import HTTPException
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text, text
from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, scoped_session, mapped_column, relationship, DeclarativeBase, Session
from sqlalchemy.sql import func, delete, or_
from sqlalchemy.sql.schema import CheckConstraint, Index

from app.consts import COMMON_SHIFT_CONFIG
from app.enums import PayloadType, TrailType, UnloadType
from app.sim_engine.enums import SolverType
from app.utils import TZ, utc_now

__all__ = (
    'BaseObject',
    'Blasting',
    'DefaultValuesMixin',
    'FuelStation',
    'FuelStationTemplate',
    'LocationMixin',
    'Scenario',
    'ShovelTemplate',
    'Shovel',
    'TruckTemplate',
    'Truck',
    'UnloadTemplate',
    'Unload',
    'Trail',
    'TrailTruckAssociation',
    'Quarry',
    'RoadNet',
    'UploadedFile',
    'MapOverlay',
    'TYPE_MODEL_MAP',
    'IdleArea',
    'PlannedIdle',
)


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })


# region Model mixins

class DefaultValuesMixin:
    """Миксин для сбора значений по умолчанию"""

    @classmethod
    def collect_default_values(cls) -> dict[str, Any]:
        # cls: db.Model
        result = {}
        # field: Column
        for field in cls.__table__.columns.values():
            if getattr(field.default, 'is_scalar', False):
                result[field.name] = field.default.arg
        return result

    @classmethod
    def collect_default_values_of_all_models(cls):
        # cls: db.Model

        result = {}
        # mapper: Mapper

        for mapper in Base.registry.mappers:
            if issubclass(mapper.class_, cls):
                dv_dict = mapper.class_.collect_default_values()
                if dv_dict:
                    result[mapper.class_.__tablename__] = dv_dict
        return result


class LocationMixin:
    """Миксин для локации"""

    initial_lat: Mapped[float] = mapped_column(default=0.0)
    """Исходная широта, °"""
    initial_lon: Mapped[float] = mapped_column(default=0.0)
    """Исходная долгота, °"""
    initial_height: Mapped[float] = mapped_column(default=0.0)
    """Исходная высота, м"""

    @property
    def initial_location(self) -> List[float]:
        return [self.initial_lat, self.initial_lon, self.initial_height]

    location = initial_location

    def set_location(self, location: List[float]) -> None:
        if len(location) == 2:
            lat, lon = location
            self.initial_lat = lat
            self.initial_lon = lon
        elif len(location) == 3:
            lat, lon, height = location
            self.initial_lat = lat
            self.initial_lon = lon
            self.initial_height = height


# endregion


# region Common abstract base models

class BaseObject(Base):
    """Абстрактная базовая модель для объектов"""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    """ID"""
    name: Mapped[str] = mapped_column(String(100))
    """Название"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, server_default=func.now()
    )
    """Таймштамп создания"""
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, server_default=func.now(), onupdate=utc_now
    )
    """Таймштамп изменения"""

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}: {self.name}>'


class BaseVehicle(BaseObject):
    """Абстрактная базовая модель для транспортных средств"""

    __abstract__ = True

    is_calc_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    """Включён ли расчёт по физическим параметрам и справочным характеристикам"""


# endregion


# region Blasting

class Blasting(BaseObject):
    """Расписание взрывных работ"""

    __tablename__ = "blasting"

    name = None

    geojson_data: Mapped[dict] = mapped_column(JSONB, default={}, server_default='{}')
    """Геозона проведения взрывных работ (GeoJSON)"""

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    """Начало взрывных работ"""
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    """Окончание взрывных работ"""

    quarry_id: Mapped[int] = mapped_column(ForeignKey('quarry.id', ondelete='CASCADE'))
    """ID карьера"""
    quarry: Mapped['Quarry'] = relationship(back_populates='blasting_list')
    """Карьер"""


# endregion Blasting


# region Shovel

class ShovelArgsMixin:
    """Основные параметры экскаватора для обсчёта симуляции"""

    bucket_volume: Mapped[float] = mapped_column(default=1.2)
    """Объём ковша (obem_kovsha_m3), м³"""
    bucket_lift_speed: Mapped[float] = mapped_column(default=0.6)
    """Скорость подъёма ковша (skorost_podem_m_s), м/с"""
    arm_turn_angle: Mapped[float] = mapped_column(default=90, server_default='90')
    """Количество градусов в одном обороте (arm_turn_angle)"""
    arm_turn_speed: Mapped[float] = mapped_column(default=0.8)
    """Угловая скорость поворота стрелы (skorost_povorot_rad_s), рад/с"""
    bucket_dig_speed: Mapped[float] = mapped_column(default=0.15)
    """Скорость врезки ковша в грунт (skorost_vrezki_m_s), м/с"""
    bucket_fill_speed: Mapped[float] = mapped_column(default=0.07)
    """Скорость наполнения ковша (skorost_napolneniya_m_s), м/с"""
    bucket_fill_coef: Mapped[float] = mapped_column(default=0.9)
    """Коэффициент заполнения ковша (koef_zapolneniya)"""
    arm_inertia_coef: Mapped[float] = mapped_column(default=1.2)
    """Коэффициент инерции стрелы (koef_inertsii)"""
    return_move_coef: Mapped[float] = mapped_column(default=0.85)
    """Коэффициент возвратного движения (koef_vozvrata)"""
    payload_type: Mapped[PayloadType] = mapped_column(default=PayloadType.GRAVEL)
    """Тип груза (tip_porody)"""
    initial_operating_time: Mapped[int] = mapped_column(default=12, server_default='12')
    """Продолжительность безотказной работы (на начало моделирования), час"""
    initial_failure_count: Mapped[int] = mapped_column(default=100, server_default='100')
    """Зафиксировано отказов (на начало моделирования), шт"""
    average_repair_duration: Mapped[int] = mapped_column(default=8, server_default='8')
    """Средняя продолжительность ремонта, мин"""


class ShovelTemplate(DefaultValuesMixin, ShovelArgsMixin, BaseObject):
    """Шаблон экскаватора"""

    __tablename__ = "shovel_template"

    shovels: Mapped[List['Shovel']] = relationship(back_populates='template')
    """Экскаваторы"""


class Shovel(DefaultValuesMixin, ShovelArgsMixin, LocationMixin, BaseVehicle):
    """Экскаватор"""

    __tablename__ = "shovel"

    template_id: Mapped[Optional[int]] = mapped_column(ForeignKey('shovel_template.id', ondelete='SET NULL'))
    """ID шаблона"""
    template: Mapped[Optional['ShovelTemplate']] = relationship(back_populates='shovels')
    """Шаблон"""

    quarry_id: Mapped[int] = mapped_column(ForeignKey('quarry.id', ondelete='CASCADE'))
    """ID карьера"""
    quarry: Mapped['Quarry'] = relationship(back_populates='shovels')
    """Карьер"""

    trails: Mapped[List['Trail']] = relationship(back_populates='shovel')
    """Маршруты"""


# endregion


# region Truck

class TruckArgsMixin:
    """Основные параметры самосвала для обсчёта симуляции"""

    body_capacity: Mapped[float] = mapped_column(default=10.0)
    """Грузоподъемность кузова, т"""
    speed_empty: Mapped[float] = mapped_column(default=35.0)
    """Скорость порожним (speed_empty_kmh), км/ч"""
    speed_loaded: Mapped[float] = mapped_column(default=18.0)
    """Скорость гружёным (speed_loaded_kmh), км/ч"""
    initial_operating_time: Mapped[int] = mapped_column(default=12, server_default='12')
    """Продолжительность безотказной работы (на начало моделирования), час"""
    initial_failure_count: Mapped[int] = mapped_column(default=50, server_default='50')
    """Зафиксировано отказов (на начало моделирования), шт"""
    average_repair_duration: Mapped[int] = mapped_column(default=4, server_default='4')
    """Средняя продолжительность ремонта, мин"""

    # --- топливная модель ---
    fuel_capacity: Mapped[float] = mapped_column(default=200, server_default='200')
    """Объем бака, л"""
    fuel_threshold_critical: Mapped[float] = mapped_column(default=50, server_default='50')
    """Критический уровень топлива, л (0.25 * fuel_capacity)"""
    fuel_threshold_planned: Mapped[float] = mapped_column(default=80, server_default='80')
    """Порог плановой заправки, л (0.4 * fuel_capacity)"""
    fuel_level: Mapped[float] = mapped_column(default=200, server_default='200')
    """Стартовый уровень топлива, л"""
    fuel_idle_lph: Mapped[float] = mapped_column(default=15, server_default='15')
    """Холостой расход топлива, л/ч"""
    fuel_specific_consumption: Mapped[float] = mapped_column(default=205, server_default='205')
    """Удельный расход топлива при номинальной мощности, г/кВт*ч"""
    fuel_density: Mapped[float] = mapped_column(default=0.82, server_default='0.82')
    """Плотность топлива при 15 °C, кг/л"""
    engine_power_kw: Mapped[float] = mapped_column(default=1716, server_default='1716')
    """Мощность двигателя, кВт"""


class TruckTemplate(DefaultValuesMixin, TruckArgsMixin, BaseObject):
    """Шаблон самосвала"""

    __tablename__ = "truck_template"

    trucks: Mapped[List['Truck']] = relationship(back_populates='template')
    """Самосвалы"""


class Truck(DefaultValuesMixin, TruckArgsMixin, LocationMixin, BaseVehicle):
    """Самосвал"""

    __tablename__ = "truck"

    template_id: Mapped[Optional[int]] = mapped_column(ForeignKey('truck_template.id', ondelete='SET NULL'))
    """ID шаблона"""
    template: Mapped[Optional['TruckTemplate']] = relationship(back_populates='trucks')
    """Шаблон"""

    quarry_id: Mapped[int] = mapped_column(ForeignKey('quarry.id', ondelete='CASCADE'))
    """ID карьера"""
    quarry: Mapped['Quarry'] = relationship(back_populates='trucks')
    """Карьер"""

    trail_associations: Mapped[List['TrailTruckAssociation']] = relationship(
        back_populates='truck', cascade='all, delete-orphan'
    )
    """Маршруты"""


# endregion


# region Unload

class UnloadArgsMixin:
    """Основные параметры пункта разгрузки для обсчёта симуляции"""

    unload_type: Mapped[UnloadType] = mapped_column(default=UnloadType.HYDRAULIC)
    """Тип (type_unloading)"""
    capacity: Mapped[int] = mapped_column(default=100000000)
    """Вместимость (capacity), т"""
    angle: Mapped[float] = mapped_column(default=25.0)
    """Угол наклона платформы (angle), °"""
    payload_type: Mapped[PayloadType] = mapped_column(default=PayloadType.GRAVEL)
    """Тип груза (material_type)"""
    trucks_at_once: Mapped[int] = mapped_column(default=100, server_default='100')
    """Одновременно разгружающихся АС, шт"""
    initial_operating_time: Mapped[int] = mapped_column(default=24, server_default='24')
    """Продолжительность безотказной работы (на начало моделирования), час"""
    initial_failure_count: Mapped[int] = mapped_column(default=50, server_default='50')
    """Зафиксировано отказов (на начало моделирования), шт"""
    average_repair_duration: Mapped[int] = mapped_column(default=24, server_default='24')
    """Средняя продолжительность ремонта, мин"""


class UnloadTemplate(DefaultValuesMixin, UnloadArgsMixin, BaseObject):
    """Шаблон пункта разгрузки"""

    __tablename__ = "unload_template"

    unloads: Mapped[List['Unload']] = relationship(back_populates='template')
    """Пункты разгрузки"""


class Unload(DefaultValuesMixin, UnloadArgsMixin, LocationMixin, BaseObject):
    """Пункт разгрузки"""

    __tablename__ = "unload"

    template_id: Mapped[Optional[int]] = mapped_column(ForeignKey('unload_template.id', ondelete='SET NULL'))
    """ID шаблона"""
    template: Mapped[Optional['UnloadTemplate']] = relationship(back_populates='unloads')
    """Шаблон"""

    quarry_id: Mapped[int] = mapped_column(ForeignKey('quarry.id', ondelete='CASCADE'))
    """ID карьера"""
    quarry: Mapped['Quarry'] = relationship(back_populates='unloads')
    """Карьер"""

    trails: Mapped[List['Trail']] = relationship(back_populates='unload')
    """Маршруты"""


# endregion


# region FuelStation

class FuelStationArgsMixin:
    """Основные параметры заправки для обсчёта симуляции"""

    num_pumps: Mapped[int] = mapped_column(default=2, server_default='2')
    """Количество пистолетов, шт"""
    flow_rate: Mapped[float] = mapped_column(default=2.0, server_default='2.0')
    """Скорость подачи топлива, л/сек"""


class FuelStationTemplate(DefaultValuesMixin, FuelStationArgsMixin, BaseObject):
    """Шаблон заправки"""

    __tablename__ = "fuel_station_template"

    fuel_stations: Mapped[List['FuelStation']] = relationship(back_populates='template')
    """Заправки"""


class FuelStation(DefaultValuesMixin, FuelStationArgsMixin, LocationMixin, BaseObject):
    """Заправка"""

    __tablename__ = "fuel_station"

    template_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('fuel_station_template.id', ondelete='SET NULL')
    )
    """ID шаблона"""
    template: Mapped[Optional['FuelStationTemplate']] = relationship(back_populates='fuel_stations')
    """Шаблон"""

    quarry_id: Mapped[int] = mapped_column(ForeignKey('quarry.id', ondelete='CASCADE'))
    """ID карьера"""
    quarry: Mapped['Quarry'] = relationship(back_populates='fuel_stations')
    """Карьер"""


# endregion


# region IdleArea

class IdleArea(DefaultValuesMixin, LocationMixin, BaseObject):
    """Зона ожидания (пересменки, обеда и т.д.)"""

    __tablename__ = "idle_area"

    quarry_id: Mapped[int] = mapped_column(ForeignKey('quarry.id', ondelete='CASCADE'))
    """ID карьера"""
    quarry: Mapped['Quarry'] = relationship(back_populates='idle_areas')
    """Карьер"""

    is_lunch_area: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_shift_change_area: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_blast_waiting_area: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_repair_area: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    @property
    def types(self) -> List[str]:
        types_list = []
        if self.is_lunch_area:
            types_list.append("зона обеда")
        if self.is_shift_change_area:
            types_list.append("зона пересменки")
        if self.is_blast_waiting_area:
            types_list.append("зона ожидания взрыва")
        if self.is_repair_area:
            types_list.append("зона ремонта")
        return types_list


# endregion


# region Trail

class Trail(Base):
    """Маршрут"""

    __tablename__ = "trail"

    id: Mapped[int] = mapped_column(primary_key=True)
    """ID"""
    trail_type: Mapped[TrailType] = mapped_column(default=TrailType.COMMON)
    """Тип"""
    raw_graph: Mapped[str] = mapped_column(Text, default='')
    """Сырой граф"""

    shovel_id: Mapped[int] = mapped_column(ForeignKey('shovel.id', ondelete='CASCADE'))
    """ID экскаватора"""
    shovel: Mapped['Shovel'] = relationship(back_populates='trails')
    """Экскаватор"""

    unload_id: Mapped[int] = mapped_column(ForeignKey('unload.id', ondelete='CASCADE'))
    """ID пункта разгрузки"""
    unload: Mapped['Unload'] = relationship(back_populates='trails')
    """Пункт разгрузки"""

    truck_associations: Mapped[List['TrailTruckAssociation']] = relationship(
        back_populates='trail', cascade='all, delete-orphan'
    )
    """Самосвалы"""

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}: Shovel {self.shovel_id}, Unload {self.unload_id}>'


class TrailTruckAssociation(Base):
    """Ассоциация (промежуточная m2m модель) между маршрутом и самосвалом"""

    __tablename__ = "trail_truck_association"

    scenario_id: Mapped[int] = mapped_column(ForeignKey('scenario.id', ondelete='CASCADE'), primary_key=True)
    """ID сценария"""
    scenario: Mapped['Scenario'] = relationship(back_populates='truck_associations')
    """Сценарий"""

    trail_id: Mapped[int] = mapped_column(ForeignKey('trail.id', ondelete='CASCADE'), primary_key=True)
    """ID маршрута"""
    trail: Mapped['Trail'] = relationship(back_populates='truck_associations')
    """Маршрут"""

    truck_id: Mapped[int] = mapped_column(ForeignKey('truck.id', ondelete='CASCADE'), primary_key=True)
    """ID самосвала"""
    truck: Mapped['Truck'] = relationship(back_populates='trail_associations')
    """Самосвал"""

    def __repr__(self):
        return f'<{self.__class__.__name__}: Trail {self.trail_id}, Truck {self.truck_id}>'


# endregion


# region Other general models

class Quarry(DefaultValuesMixin, BaseObject):
    """Карьер"""

    __tablename__ = "quarry"

    center_lat: Mapped[float] = mapped_column(default=0.0, server_default='0.0')
    """Широта центра карьера, °"""
    center_lon: Mapped[float] = mapped_column(default=0.0, server_default='0.0')
    """Долгота центра карьера, °"""
    center_height: Mapped[float] = mapped_column(default=0.0, server_default='0.0')
    """Высота центра карьера, м"""
    timezone: Mapped[str] = mapped_column(String(100), default=TZ, server_default=TZ)
    """Часовой пояс"""
    shift_config: Mapped[list] = mapped_column(
        JSON, default=COMMON_SHIFT_CONFIG, server_default=json.dumps(COMMON_SHIFT_CONFIG)
    )
    """Разметка смен на сдвигах"""
    work_break_duration: Mapped[int] = mapped_column(default=10, server_default='10')
    """Продолжительность перерывов, мин"""
    work_break_rate: Mapped[int] = mapped_column(default=1, server_default='1')
    """Частота возникновения перерывов, шт/час"""
    lunch_break_offset: Mapped[int] = mapped_column(default=360, server_default='360')
    """Сдвиг обеденного перерыва от начала смены, мин"""
    lunch_break_duration: Mapped[int] = mapped_column(default=60, server_default='60')
    """Продолжительность обеденного перерыва, мин"""
    shift_change_offset: Mapped[int] = mapped_column(default=690, server_default='690')
    """Сдвиг пересменки от начала смены, мин"""
    shift_change_duration: Mapped[int] = mapped_column(default=30, server_default='30')
    """Продолжительность пересменки, мин"""

    target_shovel_load: Mapped[float] = mapped_column(default=0.9, server_default='0.9')
    """Целевая загрузка экскаваторов"""

    shovels: Mapped[List['Shovel']] = relationship(back_populates='quarry')
    trucks: Mapped[List['Truck']] = relationship(back_populates='quarry')
    """Самосвалы"""
    unloads: Mapped[List['Unload']] = relationship(back_populates='quarry')
    """Пункты разгрузки"""
    fuel_stations: Mapped[List['FuelStation']] = relationship(back_populates='quarry')
    """Заправки"""
    idle_areas: Mapped[List['IdleArea']] = relationship(back_populates='quarry')
    """Площадки пересменки/обеда/ожидания взрыва"""
    scenarios: Mapped[List['Scenario']] = relationship(back_populates='quarry')
    """Сценарии карьера"""
    blasting_list: Mapped[List['Blasting']] = relationship(back_populates='quarry')
    """Расписание взрывных работ"""

    road_nets: Mapped[List['RoadNet']] = relationship(back_populates='quarry')
    """Дорожные сети"""
    map_overlays: Mapped[List['MapOverlay']] = relationship(back_populates='quarry')
    """Подложки для карты"""


class Scenario(DefaultValuesMixin, BaseObject):
    """Сценарий для моделирования"""

    __tablename__ = "scenario"

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    """Начало сценария"""
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    """Конец сценария"""
    is_auto_truck_distribution: Mapped[bool] = mapped_column(Boolean, default=True)
    """Режим распределения автосамосвалов: True - автоматический, False - ручной"""

    is_calc_reliability_enabled: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false')
    """Активирован ли расчёт достоверного результата"""
    process_num: Mapped[int | None] = mapped_column()
    """Размер пула процессов для параллельного запуска симуляций (None/null - авто), шт"""

    init_runs_num: Mapped[int] = mapped_column(default=15, server_default='15')
    """Начальное количество результатов для этапной оценки стабильности, шт"""
    step_runs_num: Mapped[int] = mapped_column(default=15, server_default='15')
    """Шаг прироста количества результатов, шт"""
    max_runs_num: Mapped[int] = mapped_column(default=105, server_default='105')
    """Предельное количество результатов, шт"""

    alpha: Mapped[float] = mapped_column(default=0.05, server_default='0.05')
    """Уровень α (0.05 → 95% предиктивный интервал)"""
    r_target: Mapped[float] = mapped_column(default=0.05, server_default='0.05')
    """Порог относительной половины ширины t-интервала"""
    delta_target: Mapped[float] = mapped_column(default=0.01, server_default='0.01')
    """Порог относительного сдвига медианы между этапами"""
    consecutive: Mapped[int] = mapped_column(default=2, server_default='2')
    """Сколько раз подряд должны быть соблюдены оба порога, шт"""
    boot_b: Mapped[int] = mapped_column(default=5000, server_default='5000')
    """Число пересэмплирований для бутстрэпа, шт"""

    solver_type: Mapped[int] = mapped_column(default=SolverType.GREEDY.code(), server_default="1")
    """Тип солвера(алгоритма)"""

    quarry_id: Mapped[int] = mapped_column(ForeignKey('quarry.id', ondelete='CASCADE'))
    """ID карьера"""
    quarry: Mapped['Quarry'] = relationship(back_populates='scenarios')
    """Карьер"""

    truck_associations: Mapped[List['TrailTruckAssociation']] = relationship(back_populates='scenario')
    """Маршруты сценария"""


class RoadNet(BaseObject):
    """Дорожная сеть"""

    __tablename__ = "road_net"

    name = None

    geojson_data: Mapped[dict] = mapped_column(JSONB, default={}, server_default=text("'{}'::jsonb"))
    """Граф дорог и связи с объектами (GeoJSON)"""

    quarry_id: Mapped[int] = mapped_column(ForeignKey('quarry.id', ondelete='CASCADE'))
    """ID карьера"""
    quarry: Mapped['Quarry'] = relationship(back_populates='road_nets')
    """Карьер"""

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'


class UploadedFile(Base):
    """Загруженный файл"""

    __tablename__ = "uploaded_file"

    id: Mapped[int] = mapped_column(primary_key=True)
    """ID"""
    name: Mapped[str] = mapped_column(String(255), unique=True)
    """Имя"""
    path: Mapped[str] = mapped_column(String(4096))
    """Путь"""
    size: Mapped[int] = mapped_column()
    """Размер"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, server_default=func.now()
    )
    """Таймштамп создания"""

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name}>'

    @classmethod
    def delete_with_file(
            cls, session: scoped_session[Session], id_: int | None = None, name: str | None = None
    ) -> bool:
        if not id_ and not name:
            return False
        if id_:
            where_expr = cls.id == id_
        else:
            where_expr = cls.name == name

        deleted_path = session.execute(
            delete(cls).where(where_expr).returning(cls.path)
        ).scalar()
        if deleted_path is None:
            return False

        pathlib.Path(deleted_path).resolve().unlink(missing_ok=True)
        return True


class MapOverlay(DefaultValuesMixin, BaseObject):
    """Подложка карты"""

    __tablename__ = "map_overlay"

    is_active: Mapped[bool] = mapped_column(default=True, server_default='true')
    """Доступна для отображения?"""

    geojson_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    """Данные подложки (GeoJSON)"""
    anchor_lat: Mapped[Optional[float]] = mapped_column()
    """Широта привязки, °"""
    anchor_lon: Mapped[Optional[float]] = mapped_column()
    """Долгота привязки, °"""
    anchor_height: Mapped[Optional[float]] = mapped_column()
    """Высота привязки, м"""
    color: Mapped[str] = mapped_column(String(9), default='#212121FF', server_default='#212121FF')
    """Цвет отрисовки (RGBA hex)"""
    color_regex = r'^#[A-F0-9]{8}$'

    source_file_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('uploaded_file.id', ondelete='SET NULL'), unique=True
    )
    """ID исходного файла"""
    source_file: Mapped[Optional['UploadedFile']] = relationship()
    """Исходный файл"""

    quarry_id: Mapped[int] = mapped_column(ForeignKey('quarry.id', ondelete='CASCADE'))
    """ID карьера"""
    quarry: Mapped['Quarry'] = relationship(back_populates='map_overlays')
    """Карьер"""

    __table_args__ = (
        CheckConstraint(
            or_(
                geojson_data.is_not(None),
                source_file_id.is_not(None),
            ),
            'source_file_or_geojson_data_is_not_null'
        ),
        CheckConstraint(
            color.regexp_match(color_regex),
            'color_is_rgba_hex'
        ),
    )


class PlannedIdle(BaseObject):
    """Плановый простой"""

    __tablename__ = "planned_idle"

    name = None

    vehicle_type: Mapped[str] = mapped_column(String(100))
    """Тип техники (Generic FK)"""
    vehicle_id: Mapped[int] = mapped_column()
    """ID техники (Generic FK)"""
    valid_vehicle_models = (Truck, Shovel)
    """Допустимая техника, модели (Generic FK)"""
    valid_vehicle_types = tuple(m.__tablename__ for m in valid_vehicle_models)
    """Допустимая техника, типы (Generic FK)"""

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    """Начало простоя"""
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    """Окончание простоя"""

    quarry_id: Mapped[int] = mapped_column(ForeignKey('quarry.id', ondelete='CASCADE'))
    """ID карьера"""
    quarry: Mapped['Quarry'] = relationship()
    """Карьер"""

    __table_args__ = (
        Index('vehicle_type_id', vehicle_type, vehicle_id),
        Index('time_range', start_time, end_time),
        CheckConstraint(
            vehicle_type.in_(valid_vehicle_types),
            'vehicle_type_is_valid'
        ),
    )


# endregion


# region Globals

TYPE_MODEL_MAP: dict[str, type[Base]] = {
    Blasting.__tablename__: Blasting,
    ShovelTemplate.__tablename__: ShovelTemplate,
    Shovel.__tablename__: Shovel,
    TruckTemplate.__tablename__: TruckTemplate,
    Truck.__tablename__: Truck,
    UnloadTemplate.__tablename__: UnloadTemplate,
    Unload.__tablename__: Unload,
    Trail.__tablename__: Trail,
    Quarry.__tablename__: Quarry,
    IdleArea.__tablename__: IdleArea,
    FuelStationTemplate.__tablename__: FuelStationTemplate,
    FuelStation.__tablename__: FuelStation,
    Scenario.__tablename__: Scenario,
    RoadNet.__tablename__: RoadNet,
    MapOverlay.__tablename__: MapOverlay,
    PlannedIdle.__tablename__: PlannedIdle,
}

TYPE_SCHEDULE_MAP = {
    Blasting.__tablename__: Blasting,
    PlannedIdle.__tablename__: PlannedIdle,
}


def validate_schedule_type(type: str):
    if not type or type not in TYPE_SCHEDULE_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid type. Valid types are: {list(TYPE_SCHEDULE_MAP.keys())}",
        )
    return type


def validate_object_type(type: str):
    all_object_types = list(TYPE_SCHEDULE_MAP.keys()) + list(TYPE_MODEL_MAP.keys())
    if not type or type not in all_object_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid type. Valid types are: {list(TYPE_MODEL_MAP.keys())}",
        )
    return type

# endregion
