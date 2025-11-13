from pathlib import Path
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Mapping, ClassVar, Type, TYPE_CHECKING

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator, PrivateAttr, ConfigDict

from sqlalchemy import exists, select, update, and_, or_

from app.dxf.dxf_converter import DXFConverter
from app.enums import PayloadType, TrailType, UnloadType
from app.models import (
    BaseObject,
    Blasting,
    FuelStation,
    FuelStationTemplate,
    MapOverlay,
    RoadNet,
    Scenario,
    IdleArea,
    PlannedIdle,
    Shovel,
    ShovelTemplate,
    Trail,
    Truck,
    TruckTemplate,
    Quarry,
    Unload,
    UnloadTemplate,
    UploadedFile,
)
from app.geojson_schema import FEATURE_COLLECTION_POINT_LINESTRING, FEATURE_COLLECTION_POINT
from app.road_net import RoadNetCleaner
from app.shift import ShiftLogic, ShiftConfigException
from app import SessionLocal
from roadnet.core import BaseSchemaValidator, RoadNetFactory, RoadNetGraph
from roadnet.exceptions import RoadNetException

from app.sim_engine.enums import SolverType


db = SessionLocal()

__all__ = (
    'BlastingSchema',
    'ShovelTemplateSchema',
    'ShovelSchema',
    'TruckTemplateSchema',
    'TruckSchema',
    'UnloadTemplateSchema',
    'UnloadSchema',
    'TrailSchema',
    'QuarrySchema',
    'IdleAreaSchema',
    'FuelStationTemplateSchema',
    'FuelStationSchema',
    'MapOverlaySchema',
    'PlannedIdleSchema',
    'ScheduleItemDTO',
    'ShiftDetailsDTO',
    'ScheduleDataResponseDTO',
    'BlastingScheduleItemDTO',
    'PlannedIdleScheduleItemDTO',
    'TYPE_SCHEMA_MAP',
)


# ----------------------
# Helpers
# ----------------------
def collect_model_field_names(schema_cls: type) -> List[str]:
    """
    Возвращает имена полей Pydantic-схемы.
    """
    if hasattr(schema_cls, '__fields__'):
        return list(schema_cls.__fields__.keys())
    return [k for k in dir(schema_cls) if not k.startswith('_')]

class ObjectActionRequest(BaseModel):
    action: str
    type: str
    data: Dict[str, Any]


# ----------------------
# Mixins as Pydantic models
# ----------------------

class LocationMixin(BaseModel):
    initial_lat: Optional[float] = Field(None, ge=-90, le=90)
    initial_lon: Optional[float] = Field(None, ge=-180, le=180)
    initial_height: Optional[float] = Field(None, ge=-6000, le=8000)


class TemplateRefMixin(BaseModel):
    template_id: Optional[int] = None

    # метаданные класса
    template_model: ClassVar[Optional[Type[Any]]] = None
    template_fields_class: ClassVar[Optional[Type[Any]]] = None

    def verify_template_bond(self, orm_obj) -> None:
        """
        Если orm_obj.template_id установлен, проверяем, совпадают ли поля шаблона и объекта.
        Если нет — обнуляем связь.
        """
        if not orm_obj or not getattr(orm_obj, 'template_id', None):
            return

        db.flush()
        field_names = collect_model_field_names(self.__class__.__dict__.get('template_fields_class', type(self)))
        for field_name in field_names:
            if (
                    hasattr(orm_obj, field_name)
                    and hasattr(orm_obj, 'template')
                    and getattr(orm_obj, 'template')
                    and getattr(orm_obj, field_name) != getattr(orm_obj.template, field_name)
            ):
                orm_obj.template_id = None
                break


class TemplateMixin(BaseModel):
    templatable_model: ClassVar[Optional[Type[Any]]] = None
    template_fields_class: ClassVar[Optional[Type[Any]]] = None

    def verify_template_bond_reversed(self, orm_obj) -> None:
        """
        Если у текущего шаблона изменились поля — удалить связь template_id у всех привязанных объектов.
        """
        if not orm_obj or not getattr(orm_obj, 'id', None):
            return


        field_names = collect_model_field_names(self.template_fields_class or type(self))
        for field_name in field_names:
            value_now = getattr(orm_obj, field_name, None)
            value_new = getattr(self, field_name, None)
            if value_now != value_new:
                db.execute(
                    update(self.templatable_model).where(
                        self.templatable_model.template_id == orm_obj.id
                    ).values(template_id=None)
                )
                break


class QuarryRefMixin(BaseModel):
    quarry_id: Optional[int] = None


# ----------------------
# Common base schemas
# ----------------------

class BaseObjectSchema(BaseModel):
    id: Optional[int] = Field(None, ge=1, description="ID должен быть >= 1 (опционально)")
    name: str = Field(None, min_length=1, max_length=100, description="Имя 1..100 символов")

    model: ClassVar[Type[BaseObject]] = BaseObject

    # внутренний ORM-объект, не поле Pydantic
    _obj: Any = PrivateAttr(default=None)

    def validate_name_unique(self):
        """Проверка уникальности имени — вызывать из роутера перед сохранением."""
        if not self.name:
            return
        inner_stmt = exists(1).where(self.model.name == self.name)
        if self.id:
            inner_stmt = inner_stmt.where(self.model.id != self.id)
        name_exists = db.execute(select(inner_stmt)).scalar()
        if name_exists:
            raise HTTPException(status_code=400, detail='Запись с таким названием уже существует')

    def instantiate_object(self):
        """
        Возвращает ORM-объект: если id задан — загружает, иначе создаёт новый и добавляет в сессию.
        """
        if getattr(self, '_obj', None) is not None:
            return self._obj

        if self.id:
            self._obj = db.execute(select(self.model).where(self.model.id == self.id)).scalar()
        else:
            self._obj = self.model()
            db.add(self._obj)
        return self._obj


class BaseVehicleSchema(BaseObjectSchema):
    is_calc_enabled: Optional[bool] = None


# ----------------------
# Specific schemas
# ----------------------


class ScheduleItemDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quarry_id: int
    start_time: datetime
    end_time: datetime


class ShiftDetailsDTO(BaseModel):
    number: int
    begin_time_enterprise: str
    end_time_enterprise: str
    day: str


class BlastingScheduleItemDTO(ScheduleItemDTO):
    geojson_data: Optional[Dict]


class PlannedIdleScheduleItemDTO(ScheduleItemDTO):
    vehicle_id: int
    vehicle_type: str


class ScheduleDataResponseDTO(BaseModel):
    time: dict
    filters: dict
    shift_details: Optional[ShiftDetailsDTO] = None
    items: List[PlannedIdleScheduleItemDTO | BlastingScheduleItemDTO]


class CoordinateSchema(BaseModel):
    lat: float
    lng: float


class TimelineItemSchema(BaseModel):
    id: int
    coordinates: List[CoordinateSchema]
    start: datetime
    end: datetime
    content: str = Field(default='')
    group: Optional[int] = Field(default=None)

    def start_utc(self, enterprise_tz: ZoneInfo) -> datetime:
        return self.__to_utc(self.start, enterprise_tz)

    def end_utc(self, enterprise_tz: ZoneInfo) -> datetime:
        return self.__to_utc(self.end, enterprise_tz)

    @staticmethod
    def __to_utc(dt: datetime, enterprise_tz: ZoneInfo) -> datetime:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=enterprise_tz)

        return dt.astimezone(ZoneInfo('UTC'))

    def to_geojson(self, timeline_index: int) -> dict:
        coordinates = [
            [coord.lng, coord.lat] for coord in self.coordinates
        ]

        if coordinates and coordinates[0] != coordinates[-1]:
            coordinates.append(coordinates[0])

        return {
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [coordinates]
                },
                'properties': {
                    'id': self.id,
                    'group': self.group,
                    'content': self.content or '',
                    'timeline_index': timeline_index
                }
            }]
        }


class BlastingSchema(QuarryRefMixin, BaseObjectSchema):
    start_date: datetime = Field(alias='startDate')
    geojson_data: dict = None
    timeline_items: list[TimelineItemSchema] = Field(alias='timelineItems')

    model: ClassVar[Type[Blasting]] = Blasting


class ScenarioSchema(BaseObjectSchema):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_auto_truck_distribution: Optional[bool] = Field(default=True)
    is_calc_reliability_enabled: Optional[bool] = Field(default=False)
    solver_type: Optional[int] = Field(default=SolverType.GREEDY.code())

    quarry_id: Optional[int] = None
    trails: Optional[List[Dict]] = []

    model: ClassVar[Type[Scenario]] = Scenario

    @field_validator('end_time')
    @classmethod
    def check_end_after_start(cls, v, info):
        start = info.data.get('start_time')
        if start and v and v <= start:
            raise ValueError('Конец сценария должен быть позже начала')
        return v


class ShovelArgsMixin(BaseModel):
    bucket_volume: Optional[float] = Field(None, ge=0)
    bucket_lift_speed: Optional[float] = Field(None, ge=0)
    arm_turn_angle: Optional[float] = Field(None, ge=0)
    arm_turn_speed: Optional[float] = Field(None, ge=0)
    bucket_dig_speed: Optional[float] = Field(None, ge=0)
    bucket_fill_speed: Optional[float] = Field(None, ge=0)
    bucket_fill_coef: Optional[float] = Field(None, ge=0)
    arm_inertia_coef: Optional[float] = Field(None, ge=0)
    return_move_coef: Optional[float] = Field(None, ge=0)
    payload_type: Optional[str] = None
    initial_operating_time: Optional[int] = Field(None, ge=0)
    initial_failure_count: Optional[int] = Field(None, ge=0)
    average_repair_duration: Optional[int] = Field(None, ge=0)

    @field_validator('payload_type')
    @classmethod
    def check_payload(cls, v):
        if v is None:
            return v
        if v not in list(PayloadType):
            raise ValueError('Invalid payload_type')
        return v


class ShovelTemplateSchema(TemplateMixin, ShovelArgsMixin, BaseObjectSchema):
    model: ClassVar[Type[ShovelTemplate]] = ShovelTemplate
    templatable_model: ClassVar[Type[Shovel]] = Shovel
    template_fields_class: ClassVar[Type[ShovelArgsMixin]] = ShovelArgsMixin


class ShovelSchema(QuarryRefMixin, TemplateRefMixin, ShovelArgsMixin, LocationMixin, BaseVehicleSchema):
    model: ClassVar[Type[Shovel]] = Shovel
    template_model: ClassVar[Type[ShovelTemplate]] = ShovelTemplate
    template_fields_class: ClassVar[Type[ShovelArgsMixin]] = ShovelArgsMixin


class TruckArgsMixin(BaseModel):
    body_capacity: Optional[float] = Field(None, ge=0)
    speed_empty: Optional[float] = Field(None, ge=0)
    speed_loaded: Optional[float] = Field(None, ge=0)
    initial_operating_time: Optional[int] = Field(None, ge=0)
    initial_failure_count: Optional[int] = Field(None, ge=0)
    average_repair_duration: Optional[int] = Field(None, ge=0)

    fuel_capacity: Optional[float] = Field(None, ge=0)
    fuel_threshold_critical: Optional[float] = Field(None, ge=0)
    fuel_threshold_planned: Optional[float] = Field(None, ge=0)
    fuel_level: Optional[float] = Field(None, ge=0)
    fuel_idle_lph: Optional[float] = Field(None, ge=0)
    fuel_specific_consumption: Optional[float] = Field(None, ge=0)
    fuel_density: Optional[float] = Field(None, ge=0)
    engine_power_kw: Optional[float] = Field(None, ge=0)


class TruckTemplateSchema(TemplateMixin, TruckArgsMixin, BaseObjectSchema):
    model: ClassVar[Type[TruckTemplate]] = TruckTemplate
    templatable_model: ClassVar[Type[Truck]] = Truck
    template_fields_class: ClassVar[Type[TruckArgsMixin]] = TruckArgsMixin


class TruckSchema(QuarryRefMixin, TemplateRefMixin, TruckArgsMixin, LocationMixin, BaseVehicleSchema):
    model: ClassVar[Type[Truck]] = Truck
    template_model: ClassVar[Type[TruckTemplate]] = TruckTemplate
    template_fields_class: ClassVar[Type[TruckArgsMixin]] = TruckArgsMixin


class UnloadArgsMixin(BaseModel):
    unload_type: Optional[str] = None
    capacity: Optional[int] = Field(None, ge=0)
    angle: Optional[float] = None
    payload_type: Optional[str] = None
    trucks_at_once: Optional[int] = Field(None, ge=0)
    initial_operating_time: Optional[int] = Field(None, ge=0)
    initial_failure_count: Optional[int] = Field(None, ge=0)
    average_repair_duration: Optional[int] = Field(None, ge=0)

    @field_validator('unload_type')
    @classmethod
    def check_unload_type(cls, v):
        if v is None:
            return v
        if v not in list(UnloadType):
            raise ValueError('Invalid unload_type')
        return v

    @field_validator('payload_type')
    @classmethod
    def check_payload(cls, v):
        if v is None:
            return v
        if v not in list(PayloadType):
            raise ValueError('Invalid payload_type')
        return v


class UnloadTemplateSchema(TemplateMixin, UnloadArgsMixin, BaseObjectSchema):
    model: ClassVar[Type[UnloadTemplate]] = UnloadTemplate
    templatable_model: ClassVar[Type[Unload]] = Unload
    template_fields_class: ClassVar[Type[UnloadArgsMixin]] = UnloadArgsMixin


class UnloadSchema(QuarryRefMixin, TemplateRefMixin, UnloadArgsMixin, LocationMixin, BaseObjectSchema):
    model: ClassVar[Type[Unload]] = Unload
    template_model: ClassVar[Type[UnloadTemplate]] = UnloadTemplate
    template_fields_class: ClassVar[Type[UnloadArgsMixin]] = UnloadArgsMixin


class IdleAreaSchema(QuarryRefMixin, LocationMixin, BaseObjectSchema):
    is_lunch_area: Optional[bool] = None
    is_shift_change_area: Optional[bool] = None
    is_blast_waiting_area: Optional[bool] = None
    is_repair_area: Optional[bool] = None

    model: ClassVar[Type[IdleArea]] = IdleArea

    def validate_logic(self):
        if not any([self.is_lunch_area, self.is_shift_change_area, self.is_blast_waiting_area, self.is_repair_area]):
            raise HTTPException(status_code=400, detail='Хотя бы одно из полей должно быть выбрано: зона обеда, пересменки или ожидания взрыва.')


class FuelStationArgsMixin(BaseModel):
    num_pumps: Optional[int] = Field(None, ge=0)
    flow_rate: Optional[float] = Field(None, ge=0)


class FuelStationTemplateSchema(TemplateMixin, FuelStationArgsMixin, BaseObjectSchema):
    model: ClassVar[Type[FuelStationTemplate]] = FuelStationTemplate
    templatable_model: ClassVar[Type[FuelStation]] = FuelStation
    template_fields_class: ClassVar[Type[FuelStationArgsMixin]] = FuelStationArgsMixin


class FuelStationSchema(QuarryRefMixin, TemplateRefMixin, FuelStationArgsMixin, LocationMixin, BaseObjectSchema):
    model: ClassVar[Type[FuelStation]] = FuelStation
    template_model: ClassVar[Type[FuelStationTemplate]] = FuelStationTemplate
    template_fields_class: ClassVar[Type[FuelStationArgsMixin]] = FuelStationArgsMixin


class TrailSchema(BaseObjectSchema):
    trail_type: Optional[str] = None
    shovel_id: Optional[int] = None
    unload_id: Optional[int] = None
    raw_graph: Optional[str] = None

    model: ClassVar[Type[Trail]] = Trail

    @field_validator('trail_type')
    @classmethod
    def check_trail_type(cls, v):
        if v is None:
            return v
        if v not in list(TrailType):
            raise ValueError('Invalid trail_type')
        return v


class QuarrySchema(BaseObjectSchema):
    center_lat: Optional[float] = Field(None, ge=-90, le=90)
    center_lon: Optional[float] = Field(None, ge=-180, le=180)
    center_height: Optional[float] = Field(None, ge=-6000, le=8000)
    timezone: Optional[str] = None
    shift_config: Optional[Union[str, Mapping[str, Any], List[Mapping[str, Any]]]] = None
    work_break_duration: Optional[int] = Field(None, ge=0)
    work_break_rate: Optional[int] = Field(None, ge=0)
    lunch_break_offset: Optional[int] = Field(None, ge=0)
    lunch_break_duration: Optional[int] = Field(None, ge=0)
    shift_change_offset: Optional[int] = Field(None, ge=0)
    shift_change_duration: Optional[int] = Field(None, ge=0)
    target_shovel_load: Optional[float] = Field(None, gt=0, lt=1)

    model: ClassVar[Type[Quarry]] = Quarry

    def validate_timezone(self):
        if self.timezone is None:
            return
        try:
            ZoneInfo(self.timezone)
        except (TypeError, ZoneInfoNotFoundError) as exc:
            raise HTTPException(status_code=400, detail='Given value must be a valid time zone key')

    def validate_shift_config(self):
        if self.shift_config is None:
            return
        try:
            ShiftLogic.validate_shift_config(self.shift_config)
        except ShiftConfigException as exc:
            exc_msg = 'Given value must be a valid shift configuration'
            if exc.args:
                exc_msg = f'{exc_msg}. {exc.args[0]}'
            raise HTTPException(status_code=400, detail=exc_msg)

    def validate_complex_rules(self):
        orm_obj = self.instantiate_object()
        if not orm_obj:
            return

        shift_config = self.shift_config if self.shift_config is not None else getattr(orm_obj, 'shift_config', None)
        shift_logic = ShiftLogic.factory(shift_config)
        shifts_list = shift_logic.for_date(date(2011, 7, 9))

        def value_from_form_or_obj(field_name):
            val = getattr(self, field_name)
            if val is not None:
                return val
            return getattr(orm_obj, field_name)

        def offset_td(field_name):
            return timedelta(minutes=value_from_form_or_obj(field_name))

        lunch_break_offset = offset_td('lunch_break_offset')
        lunch_break_duration = offset_td('lunch_break_duration')
        lunch_break_offset_end = lunch_break_offset + lunch_break_duration

        for shift in shifts_list:
            if lunch_break_offset >= shift.length or lunch_break_offset_end > shift.length:
                raise HTTPException(status_code=400, detail='Перерыв на обед должен целиком помещаться во все смены')


        shift_change_offset = offset_td('shift_change_offset')
        shift_change_duration = offset_td('shift_change_duration')
        shift_change_offset_end = shift_change_offset + shift_change_duration

        for shift in shifts_list:
            if (shift_change_offset != timedelta(minutes=0) and shift_change_offset_end != shift.length) or shift_change_offset_end > shift.length:
                raise HTTPException(status_code=400, detail='Пересменка должна целиком помещаться во все смены и быть причалена к их началу или окончанию')

        if (shift_change_offset <= lunch_break_offset < shift_change_offset_end) or (lunch_break_offset <= shift_change_offset < lunch_break_offset_end):
            raise HTTPException(status_code=400, detail='Обеденный перерыв и пересменка не должны пересекаться')


class RoadNetSchema(QuarryRefMixin, BaseObjectSchema):
    geojson_data: Any = None
    geojson_points_data: Optional[str] = None

    _graph: Any = PrivateAttr(default=None)
    _points_graph: Any = PrivateAttr(default=None)

    model: ClassVar[Type[RoadNet]] = RoadNet

    def validate_logic(self):
        if self.quarry_id is None:
            if self.geojson_data is not None:
                raise HTTPException(status_code=400, detail='Failed to validate road net - other fields of form are invalid')

        if self.geojson_data is not None:
            try:
                self._graph = RoadNetFactory(
                    schema_validator=BaseSchemaValidator(schema=FEATURE_COLLECTION_POINT_LINESTRING),
                    cleaner=RoadNetCleaner(self.quarry_id),
                    graph_validator=None,
                ).create_from_geojson(
                    geojson_data=self.geojson_data,
                )
            except RoadNetException as exc:
                err_msg = 'Given value must be a valid road net'
                if exc.args:
                    err_msg = f'{err_msg}. {exc.args[0]}'

        if self.geojson_points_data is not None:
            try:
                self._points_graph = RoadNetFactory(
                    schema_validator=BaseSchemaValidator(schema=FEATURE_COLLECTION_POINT),
                    cleaner=RoadNetCleaner(self.quarry_id),
                    graph_validator=None,
                ).validate_points_bonds(
                    geojson_data=self.geojson_points_data
                )
            except RoadNetException as exc:
                err_msg = 'Given value must be a valid point bonds'
                if exc.args:
                    err_msg = f'{err_msg}. {exc.args[0]}'

    def save_geojson_data(self, orm_obj):
        if self._graph:
            rn_logic = RoadNetGraph(self._graph.graph)
        else:
            rn_logic = RoadNetFactory(
                schema_validator=BaseSchemaValidator(schema=FEATURE_COLLECTION_POINT_LINESTRING),
                cleaner=RoadNetCleaner(orm_obj.quarry_id),
                graph_validator=None,
            ).create_from_geojson(
                geojson_data=self.geojson_data,
            )

        if self._points_graph:
            rn_logic.update_graph_bonds(self._points_graph)
        orm_obj.geojson_data = rn_logic.graph_to_geojson()


class MapOverlaySchema(QuarryRefMixin, BaseObjectSchema):
    is_active: Optional[bool] = None
    anchor_lat: Optional[float] = Field(None, ge=-90, le=90)
    anchor_lon: Optional[float] = Field(None, ge=-180, le=180)
    anchor_height: Optional[float] = Field(None, ge=-6000, le=8000)
    color: Optional[str] = None
    source_file_id: Optional[int] = None
    convert_overlay: Optional[bool] = Field(default=False)

    model: ClassVar[Type[MapOverlay]] = MapOverlay


    def validate_source_file_id_unique(self):
        if self.source_file_id is None:
            return
        inner_stmt = exists(1).where(self.model.source_file_id == self.source_file_id)
        if self.id:
            inner_stmt = inner_stmt.where(self.model.id != self.id)
        already_exists = db.execute(select(inner_stmt)).scalar()
        if already_exists:
            raise HTTPException(status_code=400, detail='Подложка карты, указывающая на этот файл, уже существует')

    def validate_convert_overlay_possible(self):
        if not self.convert_overlay:
            return
        if self.source_file_id is None and self.id:
            source_file_id = db.execute(select(self.model.source_file_id).where(self.model.id == self.id)).scalar()
        else:
            source_file_id = self.source_file_id
        if not source_file_id:
            raise HTTPException(status_code=400, detail='Невозможно произвести конвертацию - исходный DXF-файл отсутствует')

    def convert_dxf(self, orm_obj):
        if not self.convert_overlay:
            return
        stmt = select(UploadedFile.path).where(UploadedFile.id == orm_obj.source_file_id)
        result = db.execute(stmt)
        source_file_path = result.scalar()
        if not source_file_path:
            return
        if orm_obj.anchor_lat is None or orm_obj.anchor_lon is None:
            stmt = select(Quarry.center_lat, Quarry.center_lon, Quarry.center_height).where(
                Quarry.id == orm_obj.quarry_id)
            result = db.execute(stmt).first()
            anchor_lat, anchor_lon, anchor_height = result
        else:
            anchor_lat, anchor_lon, anchor_height = orm_obj.anchor_lat, orm_obj.anchor_lon, orm_obj.anchor_height

        source_file_path = Path(source_file_path)
        dxf_conv = DXFConverter(anchor_lat, anchor_lon, anchor_height)
        feature_collection = dxf_conv.convert_dxf_to_geojson(source_file_path)
        orm_obj.geojson_data = feature_collection


class PlannedIdleSchema(QuarryRefMixin, BaseObjectSchema):
    vehicle_type: Optional[str] = None
    vehicle_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    model: ClassVar[Type[PlannedIdle]] = PlannedIdle

    @field_validator('vehicle_type')
    @classmethod
    def vehicle_type_allowed(cls, v):
        if v is None:
            return v
        if v not in PlannedIdle.valid_vehicle_types:
            raise ValueError('Invalid vehicle type')
        return v

    def validate_vehicle_id_exists(self):
        if not self.vehicle_id:
            return
        vehicle_model = next(
            filter(lambda m: m.__tablename__ == self.vehicle_type, self.model.valid_vehicle_models),
            None
        )
        if vehicle_model:
            stmt = select(exists(1).where(vehicle_model.id == self.vehicle_id))
            vehicle_exists = db.execute(stmt).scalar()
            if not vehicle_exists:
                raise HTTPException(status_code=400, detail='Техника с таким типом и идентификатором не найдена')

    def validate_no_time_overlap(self):
        if self.start_time is None or self.end_time is None:
            return
        if self.start_time >= self.end_time:
            raise HTTPException(status_code=400, detail='Время окончания простоя должно превышать время начала')

        inner_stmt = exists(1).where(
            self.model.vehicle_type == self.vehicle_type,
            self.model.vehicle_id == self.vehicle_id,
            or_(
                and_(
                    self.model.start_time <= self.start_time,
                    self.start_time < self.model.end_time
                ),
                and_(
                    self.start_time <= self.model.start_time,
                    self.model.start_time < self.end_time
                )
            )
        )
        if self.id:
            inner_stmt = inner_stmt.where(self.model.id != self.id)
        idle_exists = db.execute(select(inner_stmt)).scalar()
        if idle_exists:
            raise HTTPException(status_code=400, detail='Простой не должен пересекаться с другими простоями этой же техники')


# ----------------------
# Globals mapping
# ----------------------
TYPE_SCHEMA_MAP: Dict[str, Type[BaseModel]] = {
    Blasting.__tablename__: BlastingSchema,
    Scenario.__tablename__: ScenarioSchema,
    ShovelTemplate.__tablename__: ShovelTemplateSchema,
    Shovel.__tablename__: ShovelSchema,
    TruckTemplate.__tablename__: TruckTemplateSchema,
    Truck.__tablename__: TruckSchema,
    UnloadTemplate.__tablename__: UnloadTemplateSchema,
    Unload.__tablename__: UnloadSchema,
    Trail.__tablename__: TrailSchema,
    Quarry.__tablename__: QuarrySchema,
    IdleArea.__tablename__: IdleAreaSchema,
    FuelStationTemplate.__tablename__: FuelStationTemplateSchema,
    FuelStation.__tablename__: FuelStationSchema,
    RoadNet.__tablename__: RoadNetSchema,
    MapOverlay.__tablename__: MapOverlaySchema,
    PlannedIdle.__tablename__: PlannedIdleSchema,
}
