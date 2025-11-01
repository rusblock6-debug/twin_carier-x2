# Анализ проекта

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\conftest.py`

### Импорты
- `import os`

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\consts.py`

### Импорты
- `import os`

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\dxf_converter.py`

### Импорты
- `import logging`
- `import pathlib`
- `import re`
- `from ezdxf.entities.dxfgfx import DXFGraphic`
- `from ezdxf.entities.line import Line`
- `from ezdxf.entities.lwpolyline import LWPolyline`
- `from ezdxf.entities.polyline import Polyline`
- `from ezdxf.filemanagement import readfile`
- `from app.geo_utils import local_to_global`

### Публичные функции

#### __init__ (`DXFConverter`)
**Аргументы:**
- `self`
- `anchor_lat`: float
- `anchor_lon`: float
- `anchor_height`: float | None

**Возвращает:** `None`

---

#### convert_coords (`DXFConverter`)
**Аргументы:**
- `self`
- `x`: float
- `y`: float
- `z`: float | None = None

**Возвращает:** `tuple[float, float, float | None]`

**Вызывает:** `local_to_global`

---

#### safe_geojson_coords (`DXFConverter`)
**Аргументы:**
- `self`
- `x`: float
- `y`: float
- `z`: float | None

**Возвращает:** `tuple[float, float] | tuple[float, float, float]`

---

#### extract_elevation_from_str (`DXFConverter`)
Extract elevation from layer name

**Аргументы:**
- `self`
- `layer_name`: str

**Возвращает:** `float | None`

**Вызывает:** `search`, `float`, `group`

---

#### process_line (`DXFConverter`)
Process LINE entity

**Аргументы:**
- `self`
- `line`: Line
- `layer_name`: str
- `elevation`: float | None

**Возвращает:** `dict`

**Вызывает:** `convert_coords`, `safe_geojson_coords`

---

#### process_polyline (`DXFConverter`)
Process POLYLINE entity

**Аргументы:**
- `self`
- `polyline`: Polyline
- `layer_name`: str
- `elevation`: float | None

**Возвращает:** `dict | None`

**Вызывает:** `append`, `len`, `convert_coords`, `safe_geojson_coords`

---

#### process_lwpolyline (`DXFConverter`)
Process LWPOLYLINE entity

**Аргументы:**
- `self`
- `lwpolyline`: LWPolyline
- `layer_name`: str
- `elevation`: float | None

**Возвращает:** `dict | None`

**Вызывает:** `safe_geojson_coords`, `get_points`, `convert_coords`, `len`, `append`

---

#### convert_dxf_to_geojson (`DXFConverter`)
Convert DXF file to GeoJSON format

**Аргументы:**
- `self`
- `dxf_file`: pathlib.Path

**Возвращает:** `dict`

**Вызывает:** `ezdxf_readfile`, `Exception`, `warning`, `process_line`, `exception`, `dxftype`, `process_lwpolyline`, `len`, `modelspace`, `extract_elevation_from_str`, `process_polyline`, `append`, `info`, `items`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\enums.py`

### Импорты
- `import enum`

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\forms.py`

### Импорты
- `import os`
- `from pathlib import Path`
- `from datetime import date, datetime, timedelta`
- `from typing import Any, Dict, List, Optional, Union, Mapping, ClassVar, Type`
- `from zoneinfo import ZoneInfo, ZoneInfoNotFoundError`
- `from fastapi import HTTPException`
- `from fastapi.responses import JSONResponse`
- `from pydantic import BaseModel, Field, field_validator, PrivateAttr`
- `from sqlalchemy import exists, select, update, delete, and_, or_`
- `from app import get_db`
- `from app.dxf_converter import DXFConverter`
- `from app.enums import PayloadType, TrailType, UnloadType`
- `from app.models import BaseObject, Blasting, FuelStation, FuelStationTemplate, MapOverlay, RoadNet, Scenario, IdleArea, PlannedIdle, Shovel, ShovelTemplate, Trail, Truck, TruckTemplate, Quarry, Unload, UnloadTemplate, UploadedFile`
- `from app.geojson_schema import FEATURE_COLLECTION_POINT_LINESTRING, FEATURE_COLLECTION_POINT`
- `from app.road_net import RoadNetCleaner`
- `from app.shift import ShiftLogic, ShiftConfigException`
- `from app import SessionLocal`
- `from roadnet.core import BaseSchemaValidator, RoadNetFactory, RoadNetGraph`
- `from roadnet.exceptions import RoadNetException`

### Публичные функции

#### collect_model_field_names
Возвращает имена полей Pydantic-схемы.

**Аргументы:**
- `schema_cls`: type

**Возвращает:** `List[str]`

**Вызывает:** `list`, `startswith`, `dir`, `keys`, `hasattr`

---

#### verify_template_bond (`TemplateRefMixin`)
Если orm_obj.template_id установлен, проверяем, совпадают ли поля шаблона и объекта.
Если нет — обнуляем связь.

**Аргументы:**
- `self`
- `orm_obj`

**Возвращает:** `None`

**Вызывает:** `flush`, `getattr`, `collect_model_field_names`, `type`, `get`, `hasattr`

---

#### verify_template_bond_reversed (`TemplateMixin`)
Если у текущего шаблона изменились поля — удалить связь template_id у всех привязанных объектов.

**Аргументы:**
- `self`
- `orm_obj`

**Возвращает:** `None`

**Вызывает:** `values`, `getattr`, `update`, `where`, `collect_model_field_names`, `type`, `execute`

---

#### delete_schedule_items (`ScheduleMixin`)
**Аргументы:**
- `obj_data`: Dict[str, Any]
- `model`
- `enterprise_tz`: ZoneInfo

**Возвращает:** `int`

**Вызывает:** `all`, `execute`, `ValueError`, `astimezone`, `where`, `factory`, `delete`, `strptime`, `for_date`, `get`, `ZoneInfo`, `total_seconds`, `date`

---

#### handle_schedule_create (`ScheduleMixin`)
**Аргументы:**
- `self`
- `obj_data`: Dict[str, Any]
- `model`
- `schedule_type`: str

**Вызывает:** `str`, `delete_schedule_items`, `replace`, `append`, `add`, `len`, `JSONResponse`, `enumerate`, `commit`, `fromisoformat`, `rollback`, `getenv`, `get`, `ZoneInfo`, `model`

---

#### handle_schedule_delete (`ScheduleMixin`)
**Аргументы:**
- `self`
- `obj_data`: Dict[str, Any]
- `model`
- `schedule_type`: str

**Вызывает:** `delete_schedule_items`, `commit`, `JSONResponse`, `rollback`, `getenv`, `str`, `ZoneInfo`

---

#### validate_name_unique (`BaseObjectSchema`)
Проверка уникальности имени — вызывать из роутера перед сохранением.

**Аргументы:**
- `self`

**Вызывает:** `select`, `HTTPException`, `where`, `scalar`, `exists`, `execute`

---

#### instantiate_object (`BaseObjectSchema`)
Возвращает ORM-объект: если id задан — загружает, иначе создаёт новый и добавляет в сессию.

**Аргументы:**
- `self`

**Вызывает:** `select`, `getattr`, `add`, `where`, `scalar`, `execute`, `model`

---

#### populate_obj (`BlastingSchema`)
**Аргументы:**
- `self`
- `orm_obj`

---

#### check_end_after_start (`ScenarioSchema`)
**Аргументы:**
- `cls`
- `v`
- `info`

**Вызывает:** `field_validator`, `get`, `ValueError`

---

#### check_payload (`ShovelArgsMixin`)
**Аргументы:**
- `cls`
- `v`

**Вызывает:** `field_validator`, `list`, `ValueError`

---

#### check_unload_type (`UnloadArgsMixin`)
**Аргументы:**
- `cls`
- `v`

**Вызывает:** `field_validator`, `list`, `ValueError`

---

#### check_payload (`UnloadArgsMixin`)
**Аргументы:**
- `cls`
- `v`

**Вызывает:** `field_validator`, `list`, `ValueError`

---

#### validate_logic (`IdleAreaSchema`)
**Аргументы:**
- `self`

**Вызывает:** `HTTPException`, `any`

---

#### check_trail_type (`TrailSchema`)
**Аргументы:**
- `cls`
- `v`

**Вызывает:** `field_validator`, `list`, `ValueError`

---

#### validate_timezone (`QuarrySchema`)
**Аргументы:**
- `self`

**Вызывает:** `HTTPException`, `ZoneInfo`

---

#### validate_shift_config (`QuarrySchema`)
**Аргументы:**
- `self`

**Вызывает:** `validate_shift_config`, `HTTPException`

---

#### value_from_form_or_obj (`QuarrySchema`)
**Аргументы:**
- `field_name`

**Вызывает:** `getattr`

---

#### offset_td (`QuarrySchema`)
**Аргументы:**
- `field_name`

**Вызывает:** `value_from_form_or_obj`, `timedelta`

---

#### validate_complex_rules (`QuarrySchema`)
**Аргументы:**
- `self`

**Вызывает:** `value_from_form_or_obj`, `timedelta`

---

#### validate_logic (`RoadNetSchema`)
**Аргументы:**
- `self`

**Вызывает:** `create_from_geojson`, `RoadNetFactory`, `HTTPException`, `validate_points_bonds`, `RoadNetCleaner`, `BaseSchemaValidator`

---

#### save_geojson_data (`RoadNetSchema`)
**Аргументы:**
- `self`
- `orm_obj`

**Вызывает:** `create_from_geojson`, `RoadNetFactory`, `RoadNetGraph`, `update_graph_bonds`, `RoadNetCleaner`, `BaseSchemaValidator`, `graph_to_geojson`

---

#### validate_source_file_id_unique (`MapOverlaySchema`)
**Аргументы:**
- `self`

**Вызывает:** `select`, `HTTPException`, `where`, `scalar`, `exists`, `execute`

---

#### validate_convert_overlay_possible (`MapOverlaySchema`)
**Аргументы:**
- `self`

**Вызывает:** `select`, `HTTPException`, `where`, `scalar`, `execute`

---

#### convert_dxf (`MapOverlaySchema`)
**Аргументы:**
- `self`
- `orm_obj`

**Вызывает:** `select`, `Path`, `where`, `scalar`, `first`, `DXFConverter`, `convert_dxf_to_geojson`, `execute`

---

#### vehicle_type_allowed (`PlannedIdleSchema`)
**Аргументы:**
- `cls`
- `v`

**Вызывает:** `field_validator`, `ValueError`

---

#### validate_vehicle_id_exists (`PlannedIdleSchema`)
**Аргументы:**
- `self`

**Вызывает:** `select`, `next`, `HTTPException`, `filter`, `where`, `scalar`, `exists`, `execute`

---

#### validate_no_time_overlap (`PlannedIdleSchema`)
**Аргументы:**
- `self`

**Вызывает:** `select`, `or_`, `HTTPException`, `where`, `scalar`, `exists`, `and_`, `execute`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\geojson_schema.py`

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\geo_utils.py`

### Импорты
- `import math`
- `from pyproj import Geod`

### Публичные функции

#### calc_distance
**Аргументы:**
- `coord0`: tuple[float, float, float | None]
- `coord1`: tuple[float, float, float | None]
- `geod`: Geod | None = None

**Возвращает:** `float`

**Вызывает:** `inv`, `Geod`, `hypot`

---

#### local_to_global
**Аргументы:**
- `x`: float
- `y`: float
- `z`: float | None
- `lat0`: float
- `lon0`: float
- `alt0`: float | None

**Возвращает:** `tuple[float, float, float | None]`

**Вызывает:** `sin`, `cos`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\gunicorn.conf.py`

### Импорты
- `import os`

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\models.py`

### Импорты
- `import json`
- `import pathlib`
- `from datetime import datetime`
- `from typing import Any, List, Optional`
- `from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text, text`
- `from sqlalchemy.dialects.postgresql import JSONB`
- `from sqlalchemy.orm import Mapped, scoped_session, mapped_column, relationship, DeclarativeBase, Session`
- `from sqlalchemy.sql import func, delete, or_`
- `from sqlalchemy.sql.schema import CheckConstraint, Index`
- `from sqlalchemy import MetaData`
- `from fastapi import HTTPException`
- `from app.consts import COMMON_SHIFT_CONFIG`
- `from app.enums import PayloadType, TrailType, UnloadType`
- `from app.utils import TZ, utc_now`

### Публичные функции

#### collect_default_values (`DefaultValuesMixin`)
**Аргументы:**
- `cls`

**Возвращает:** `dict[str, Any]`

**Вызывает:** `values`, `getattr`

---

#### collect_default_values_of_all_models (`DefaultValuesMixin`)
**Аргументы:**
- `cls`

**Вызывает:** `collect_default_values`, `issubclass`

---

#### initial_location (`LocationMixin`)
**Аргументы:**
- `self`

**Возвращает:** `List[float]`

---

#### set_location (`LocationMixin`)
**Аргументы:**
- `self`
- `location`: List[float]

**Возвращает:** `None`

**Вызывает:** `len`

---

#### types (`IdleArea`)
**Аргументы:**
- `self`

**Возвращает:** `List[str]`

**Вызывает:** `append`

---

#### delete_with_file (`UploadedFile`)
**Аргументы:**
- `cls`
- `session`: scoped_session[Session]
- `id_`: int | None = None
- `name`: str | None = None

**Возвращает:** `bool`

**Вызывает:** `returning`, `resolve`, `Path`, `where`, `scalar`, `delete`, `unlink`, `execute`

---

#### validate_schedule_type
**Аргументы:**
- `type`: str

**Вызывает:** `HTTPException`, `list`, `keys`

---

#### validate_object_type
**Аргументы:**
- `type`: str

**Вызывает:** `HTTPException`, `list`, `keys`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\road_net.py`

### Импорты
- `from collections import defaultdict`
- `from sqlalchemy import select`
- `from roadnet.core import RoadNetGraph, BaseRoadNetCleaner`
- `from app import SessionLocal`
- `from app.models import FuelStation, IdleArea, Shovel, Unload, TYPE_MODEL_MAP`

### Публичные функции

#### __init__ (`RoadNetCleaner`)
**Аргументы:**
- `self`
- `quarry_id`: int

---

#### clean (`RoadNetCleaner`)
**Аргументы:**
- `self`
- `graph`: RoadNetGraph
- `*args` (vararg)
- `**kwargs` (kwarg)

**Возвращает:** `None`

**Вызывает:** `__clean_graph_bonds_by_data`, `__clean_graph_bonds_by_schema`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\routes.py`

### Импорты
- `import json`
- `import os`
- `import pathlib`
- `import uuid`
- `from datetime import datetime, timedelta`
- `from operator import itemgetter`
- `from zoneinfo import ZoneInfo`
- `from typing import Optional, List, Dict, Any`
- `from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request`
- `from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse`
- `from fastapi.templating import Jinja2Templates`
- `from sqlalchemy import delete, select`
- `from sqlalchemy.orm import Session`
- `from pydantic import BaseModel, ValidationError`
- `from app import get_db, get_redis`
- `from app.consts import STORED_RESULTS_NUMBER`
- `from app.forms import BlastingSchema, PlannedIdleSchema`
- `from app.models import TYPE_MODEL_MAP, TYPE_SCHEDULE_MAP, DefaultValuesMixin, MapOverlay, RoadNet, UploadedFile, validate_schedule_type`
- `from app.forms import ObjectActionRequest`
- `from app.services.date_time_service import StartEndTimeGenerateService`
- `from app.services.template_service import AllTemplatesListService`
- `from app.services.quarry_data_service import QuarryDataService`
- `from app.services.schedule_data_service import ScheduleDataService, ScheduleDataResponseDTO`
- `from app.services.scenario_service import ScenarioService, ScenarioDTO`
- `from app.services.object_service import ObjectService`
- `from app.services.simulation_id_service import GetSimIdService, SimulationRequestDTO`
- `from app.shift import ShiftConfigDataException, ShiftConfigParseException`
- `from app.sim_engine.writer import BatchWriter`
- `from app.simulate_test import generate_simulation_data`
- `from app.sim_engine.simulation_manager import SimulationManager`
- `from app.utils import secure_filename`

### Публичные функции

#### index
**Аргументы:**
- `request`: Request

**Вызывает:** `FileResponse`, `get`

---

#### quarry_data
**Аргументы:**
- `db`: Session = Depends(get_db)

**Вызывает:** `AllTemplatesListService`, `StartEndTimeGenerateService`, `QuarryDataService`, `Depends`, `model_dump`, `get`

---

#### schedule_data_by_date_shift
**Аргументы:**
- `date`: str
- `quarry_id`: int
- `type`: str = Depends(validate_schedule_type)
- `shift_number`: Optional[int] = None
- `start_time`: Optional[str] = None
- `end_time`: Optional[str] = None
- `db` = Depends(get_db)

**Вызывает:** `get`, `HTTPException`, `Depends`, `getenv`, `str`, `ZoneInfo`, `ScheduleDataService`, `service`

---

#### update_location
**Аргументы:**
- `data`: UpdateLocationRequest
- `db`: Session = Depends(get_db)

**Вызывает:** `select`, `execute`, `HTTPException`, `where`, `scalar`, `Depends`, `commit`, `post`, `get`

---

#### get_scenarios
**Аргументы:**
- `db`: Session = Depends(get_db)

**Вызывает:** `ScenarioService`, `Depends`, `get`

---

#### get_road_net
**Аргументы:**
- `rn_id`: int
- `db`: Session = Depends(get_db)

**Вызывает:** `select`, `HTTPException`, `where`, `scalar`, `Depends`, `execute`, `get`

---

#### defaults_data
**Вызывает:** `collect_default_values_of_all_models`, `get`

---

#### create_object
Создание объекта (ранее action == 'create')

**Аргументы:**
- `data`: ObjectActionRequest
- `db`: Session = Depends(get_db)

**Вызывает:** `str`, `HTTPException`, `update_object`, `Depends`, `create_object`, `post`, `ObjectService`, `get`

---

#### update_object
Обновление объекта (ранее action == 'update')

**Аргументы:**
- `obj_id`: int
- `data`: ObjectActionRequest
- `db`: Session = Depends(get_db)

**Вызывает:** `ObjectService`, `HTTPException`, `update_object`, `Depends`, `put`, `str`

---

#### delete_object
**Аргументы:**
- `data`: DeleteObjectRequest
- `db`: Session = Depends(get_db)

**Вызывает:** `select`, `BlastingSchema`, `PlannedIdleSchema`, `returning`, `issubclass`, `execute`, `HTTPException`, `where`, `scalar`, `Depends`, `delete`, `commit`, `handle_schedule_delete`, `dict`, `delete_with_file`, `get`

---

#### run_simulation
**Аргументы:**
- `data`: SimulationRequestDTO
- `db`: Session = Depends(get_db)
- `redis_client` = Depends(get_redis)

**Вызывает:** `post`, `Depends`, `GetSimIdService`, `RedirectResponse`

---

#### api_run_simulation
**Аргументы:**
- `data`: SimulationRequestDTO
- `db`: Session = Depends(get_db)
- `redis_client` = Depends(get_redis)

**Вызывает:** `GetSimIdService`, `HTTPException`, `Depends`, `post`, `type`

---

#### get_simulation_meta
**Аргументы:**
- `sim_id`: str
- `redis_client` = Depends(get_redis)

**Вызывает:** `loads`, `next`, `HTTPException`, `Depends`, `scan_iter`, `get`

---

#### get_simulation_batch
**Аргументы:**
- `sim_id`: str
- `batch_index`: int
- `redis_client` = Depends(get_redis)

**Вызывает:** `loads`, `next`, `HTTPException`, `Depends`, `scan_iter`, `get`

---

#### get_simulation_batches
**Аргументы:**
- `sim_id`: str
- `indices`: List[int] = None
- `redis_client` = Depends(get_redis)

**Вызывает:** `loads`, `extend`, `mget`, `next`, `HTTPException`, `Depends`, `scan_iter`, `replace`, `get`

---

#### get_simulation_summary
**Аргументы:**
- `sim_id`: str
- `redis_client` = Depends(get_redis)

**Вызывает:** `loads`, `next`, `HTTPException`, `Depends`, `scan_iter`, `get`

---

#### get_simulation_events
**Аргументы:**
- `sim_id`: str
- `redis_client` = Depends(get_redis)

**Вызывает:** `loads`, `next`, `HTTPException`, `Depends`, `scan_iter`, `get`

---

#### handle_file_get
**Аргументы:**
- `id_or_name`: str
- `db`: Session = Depends(get_db)

**Вызывает:** `select`, `int`, `HTTPException`, `isoformat`, `where`, `scalar`, `Depends`, `execute`, `get`

---

#### handle_file_post
**Аргументы:**
- `request`: Request
- `file`: UploadFile = File(...)
- `name`: str = Form(None)
- `db`: Session = Depends(get_db)

**Вызывает:** `write`, `stat`, `Form`, `Path`, `read`, `open`, `UploadedFile`, `add`, `secure_filename`, `Depends`, `exists`, `len`, `File`, `with_stem`, `commit`, `unlink`, `post`, `str`

---

#### handle_file_delete
**Аргументы:**
- `id_or_name`: str
- `db`: Session = Depends(get_db)

**Вызывает:** `int`, `HTTPException`, `Depends`, `delete`, `commit`, `delete_with_file`

---

#### uploaded_file_route
**Аргументы:**
- `filename`: str
- `request`: Request

**Вызывает:** `FileResponse`, `resolve`, `get`, `Path`

---

#### get_map_overlay
**Аргументы:**
- `mo_id`: int
- `db`: Session = Depends(get_db)

**Вызывает:** `select`, `HTTPException`, `isoformat`, `where`, `scalar`, `Depends`, `execute`, `get`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\shift.py`

### Импорты
- `import json`
- `from dataclasses import dataclass`
- `from datetime import date, datetime, time, timedelta, timezone, tzinfo`
- `from typing import Any, Mapping, Sequence, Tuple`
- `import jsonschema`
- `from app.consts import COMMON_SHIFT_CONFIG, THREEFOLD_SHIFT_CONFIG`

### Публичные функции

#### __init__ (`ShiftConfigException`)
**Аргументы:**
- `self`
- `message`: str
- `status_code` = None

**Вызывает:** `super`, `__init__`

---

#### __init__ (`ShiftLogic`)
**Аргументы:**
- `self`
- `offsets_tuple`: Tuple['ShiftOffsetsDTO', ...]

**Возвращает:** `None`

---

#### factory (`ShiftLogic`)
**Аргументы:**
- `cls`
- `shift_config`: str | Mapping | Sequence

**Возвращает:** `'ShiftLogic'`

**Вызывает:** `validate_shift_config`, `isinstance`, `loads`, `ShiftOffsetsDTO`, `ShiftConfigParseException`, `cls`, `tuple`, `timedelta`

---

#### validate_shift_config (`ShiftLogic`)
**Аргументы:**
- `cls`
- `shift_config`: Any

**Возвращает:** `None`

**Вызывает:** `ShiftConfigSchemaException`, `ShiftConfigDataException`, `enumerate`, `validate`

---

#### for_date (`ShiftLogic`)
**Аргументы:**
- `self`
- `day`: date
- `tzinfo`: tzinfo | None = None

**Возвращает:** `list['ShiftDTO']`

**Вызывает:** `append`, `enumerate`, `combine`, `ShiftDTO`

---

#### for_datetime (`ShiftLogic`)
**Аргументы:**
- `self`
- `moment`: datetime

**Возвращает:** `'ShiftDTO'`

**Вызывает:** `date`, `ShiftConfigDataException`, `combine`, `ShiftDTO`, `enumerate`, `timedelta`

---

#### for_range (`ShiftLogic`)
**Аргументы:**
- `self`
- `start`: datetime
- `stop`: datetime

**Возвращает:** `list['ShiftDTO']`

**Вызывает:** `combine`, `ShiftDTO`, `for_datetime`, `len`, `append`, `timedelta`

---

#### prev_from (`ShiftLogic`)
**Аргументы:**
- `self`
- `shift`: 'ShiftDTO'

**Возвращает:** `'ShiftDTO'`

**Вызывает:** `len`, `combine`, `ShiftDTO`, `timedelta`

---

#### next_from (`ShiftLogic`)
**Аргументы:**
- `self`
- `shift`: 'ShiftDTO'

**Возвращает:** `'ShiftDTO'`

**Вызывает:** `len`, `combine`, `ShiftDTO`, `timedelta`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\simulate_test.py`

### Импорты
- `import random`
- `from datetime import datetime, timedelta`
- `from app.sim_engine.enums import ObjectType`

### Публичные функции

#### generate_simulation_data
**Вызывает:** `now`, `key`, `randint`, `range`, `min`, `append`, `str`, `timedelta`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\utils.py`

### Импорты
- `import os`
- `import pathlib`
- `import re`
- `import unicodedata`
- `from datetime import datetime, timezone`
- `from zoneinfo import ZoneInfo`

### Публичные функции

#### utc_now
**Вызывает:** `now`

---

#### utc_to_enterprise
Конвертирует UTC время в указанную таймзону

**Аргументы:**
- `utc_time`: str
- `tz`: str = TZ

**Возвращает:** `datetime`

**Вызывает:** `replace`, `ZoneInfo`, `fromisoformat`, `astimezone`

---

#### enterprise_to_utc
Конвертирует локальное время предприятия в UTC

**Аргументы:**
- `local_time`: str
- `tz`: str = TZ

**Возвращает:** `datetime`

**Вызывает:** `replace`, `ZoneInfo`, `fromisoformat`, `astimezone`

---

#### str_to_snake_case
**Аргументы:**
- `s`: str

**Возвращает:** `str`

**Вызывает:** `sub`, `lower`

---

#### secure_filename
Copy of :func:`werkzeug.utils.secure_filename`, but with `allow_unicode` arg

Pass it a filename and it will return a secure version of it.  This
filename can then safely be stored on a regular file system and passed
to :func:`os.path.join`.  The filename returned is an ASCII only string
for maximum portability.

On windows systems the function also makes sure that the file is not
named after one of the special device files.

>>> secure_filename("My cool movie.mov")
'My_cool_movie.mov'
>>> secure_filename("../../../etc/passwd")
'etc_passwd'
>>> secure_filename('i contain cool \xfcml\xe4uts.txt')
'i_contain_cool_umlauts.txt'

The function might return an empty filename.  It's your responsibility
to ensure that the filename is unique and that you abort or
generate a random filename if the function returned an empty one.

.. versionadded:: 0.5

:param filename: the filename to secure

**Аргументы:**
- `filename`: str
- `allow_unicode`: bool = False

**Возвращает:** `str`

**Вызывает:** `strip`, `sub`, `encode`, `split`, `decode`, `upper`, `normalize`, `replace`, `str`, `join`

---

#### human_size
Return human-readable file size

**Аргументы:**
- `path`: pathlib.Path

**Возвращает:** `str`

**Вызывает:** `stat`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\__init__.py`

### Импорты
- `import os`
- `from contextlib import asynccontextmanager`
- `from pathlib import Path`
- `import redis`
- `from dotenv import load_dotenv`
- `from fastapi import FastAPI`
- `from fastapi.middleware.cors import CORSMiddleware`
- `from fastapi.staticfiles import StaticFiles`
- `from sqlalchemy import create_engine`
- `from sqlalchemy.orm import sessionmaker`
- `from app.sim_engine.infra.logger.logger import Logger`
- `from app.routes import router`

### Публичные функции

#### get_db
**Вызывает:** `SessionLocal`, `close`

---

#### get_redis
---

#### lifespan
**Аргументы:**
- `app`: FastAPI

**Вызывает:** `print`

---

#### create_app
**Аргументы:**
- `test_config` = None

**Вызывает:** `FastAPI`, `Path`, `mount`, `add_middleware`, `mkdir`, `StaticFiles`, `getenv`, `include_router`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\env.py`

### Импорты
- `import logging`
- `from logging.config import fileConfig`
- `from sqlalchemy import pool`
- `from alembic import context`
- `from app import engine`

### Публичные функции

#### run_migrations_offline
Запуск миграций в оффлайн-режиме.

**Вызывает:** `configure`, `run_migrations`, `replace`, `str`, `begin_transaction`

---

#### run_migrations_online
Запуск миграций в онлайн-режиме.

**Вызывает:** `run_migrations`, `configure`, `connect`, `begin_transaction`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\049327069ed2_add_arm_turn_angle_to_shovel.py`

### Импорты
- `from alembic import op`
- `import sqlalchemy`

### Публичные функции

#### upgrade
**Вызывает:** `batch_alter_table`, `Column`, `add_column`, `Float`

---

#### downgrade
**Вызывает:** `batch_alter_table`, `drop_column`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\173b757501f6_add_scenario_model.py`

### Импорты
- `from alembic import op`
- `import sqlalchemy`

### Публичные функции

#### upgrade
**Вызывает:** `String`, `f`, `Boolean`, `PrimaryKeyConstraint`, `text`, `DateTime`, `Column`, `create_table`, `Integer`, `ForeignKeyConstraint`

---

#### downgrade
**Вызывает:** `drop_table`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\2f3ca3217c27_add_blasting_model.py`

### Импорты
- `from alembic import op`
- `import sqlalchemy`
- `from sqlalchemy.dialects import postgresql`

### Публичные функции

#### upgrade
**Вызывает:** `f`, `PrimaryKeyConstraint`, `text`, `Column`, `DateTime`, `Text`, `create_table`, `Integer`, `JSONB`, `ForeignKeyConstraint`

---

#### downgrade
**Вызывает:** `drop_table`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\34d2db5b9f3c_drop_columns.py`

### Импорты
- `from alembic import op`
- `import sqlalchemy`

### Публичные функции

#### upgrade
**Вызывает:** `batch_alter_table`, `alter_column`, `drop_column`

---

#### downgrade
**Вызывает:** `batch_alter_table`, `DOUBLE_PRECISION`, `add_column`, `Column`, `INTEGER`, `drop_column`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\5e034f7cece7_initial_migration_attempt_3.py`

### Импорты
- `from alembic import op`
- `import sqlalchemy`

### Публичные функции

#### upgrade
**Вызывает:** `String`, `Integer`, `f`, `Boolean`, `Enum`, `PrimaryKeyConstraint`, `Column`, `DateTime`, `Text`, `Float`, `create_table`, `ForeignKeyConstraint`

---

#### downgrade
**Вызывает:** `execute`, `drop_table`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\660043dae00e_add_shoveltemplate_trucktemplate_.py`

### Импорты
- `from alembic import op`
- `import sqlalchemy`
- `from sqlalchemy.dialects import postgresql`

### Публичные функции

#### upgrade
**Вызывает:** `String`, `batch_alter_table`, `create_foreign_key`, `f`, `ENUM`, `add_column`, `PrimaryKeyConstraint`, `Column`, `DateTime`, `create_table`, `Integer`, `Float`

---

#### downgrade
**Вызывает:** `batch_alter_table`, `f`, `drop_constraint`, `drop_table`, `drop_column`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\689dff3c9f22_new_fields_for_shovel_truck_and_unload.py`

### Импорты
- `from alembic import op`
- `import sqlalchemy`

### Публичные функции

#### upgrade
**Вызывает:** `batch_alter_table`, `Column`, `add_column`, `Integer`

---

#### downgrade
**Вызывает:** `batch_alter_table`, `drop_column`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\741a88f7abe1_add_scenario_relation_to_.py`

### Импорты
- `from alembic import op`
- `from datetime import datetime`
- `import sqlalchemy`

### Публичные функции

#### upgrade
**Вызывает:** `batch_alter_table`, `get_bind`, `now`, `create_foreign_key`, `f`, `execute`, `add_column`, `scalar`, `text`, `Column`, `Integer`, `bindparams`, `datetime`

---

#### downgrade
**Вызывает:** `batch_alter_table`, `drop_column`, `drop_constraint`, `f`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\77aa09bc992e_add_primary_key_to_scenario_id_in_.py`

### Импорты
- `from alembic import op`
- `import sqlalchemy`

### Публичные функции

#### upgrade
**Вызывает:** `batch_alter_table`, `drop_constraint`, `alter_column`, `create_primary_key`, `INTEGER`

---

#### downgrade
**Вызывает:** `batch_alter_table`, `drop_constraint`, `alter_column`, `create_primary_key`, `INTEGER`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\8520318762c4_rename_shiftchangearea_to_idlearea.py`

### Импорты
- `from alembic import op`
- `import sqlalchemy`

### Публичные функции

#### upgrade
**Вызывает:** `add_column`, `Column`, `rename_table`, `Boolean`

---

#### downgrade
**Вызывает:** `rename_table`, `drop_column`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\8d394792dc14_add_shift_change_fields_to_quarry.py`

### Импорты
- `from alembic import op`
- `import sqlalchemy`

### Публичные функции

#### upgrade
**Вызывает:** `batch_alter_table`, `Column`, `add_column`, `Integer`

---

#### downgrade
**Вызывает:** `batch_alter_table`, `drop_column`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\9daa452a370b_new_reliability_related_fields_for_.py`

### Импорты
- `from alembic import op`
- `import sqlalchemy`

### Публичные функции

#### upgrade
**Вызывает:** `batch_alter_table`, `Boolean`, `add_column`, `Column`, `Float`, `Integer`

---

#### downgrade
**Вызывает:** `batch_alter_table`, `drop_column`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\a06b87cc0807_add_shiftchangearea_and_fuelstation_.py`

### Импорты
- `from alembic import op`
- `import sqlalchemy`

### Публичные функции

#### upgrade
**Вызывает:** `String`, `batch_alter_table`, `Integer`, `f`, `add_column`, `PrimaryKeyConstraint`, `text`, `Column`, `DateTime`, `Float`, `create_table`, `ForeignKeyConstraint`

---

#### downgrade
**Вызывает:** `batch_alter_table`, `drop_column`, `drop_table`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\a43abb6acab2_add_uploadedfile_and_mapoverlay.py`

### Импорты
- `from alembic import op`
- `import sqlalchemy`
- `from sqlalchemy.dialects import postgresql`

### Публичные функции

#### upgrade
**Вызывает:** `String`, `f`, `Boolean`, `UniqueConstraint`, `PrimaryKeyConstraint`, `text`, `DateTime`, `Column`, `Text`, `create_table`, `Integer`, `Float`, `ForeignKeyConstraint`, `JSONB`, `CheckConstraint`

---

#### downgrade
**Вызывает:** `drop_table`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\b7dcacd91b4a_add_quarry.py`

### Импорты
- `from alembic import op`
- `import sqlalchemy`

### Публичные функции

#### upgrade
**Вызывает:** `create_foreign_key`, `f`, `Column`, `create_table`, `String`, `values`, `alter_column`, `PrimaryKeyConstraint`, `text`, `column`, `table`, `execute`, `update`, `DateTime`, `JSON`, `batch_alter_table`, `add_column`, `insert`, `Float`, `Integer`

---

#### downgrade
**Вызывает:** `batch_alter_table`, `f`, `drop_constraint`, `drop_table`, `drop_column`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\c5fb8550f985_add_plannedidle.py`

### Импорты
- `from alembic import op`
- `import sqlalchemy`

### Публичные функции

#### upgrade
**Вызывает:** `String`, `batch_alter_table`, `f`, `PrimaryKeyConstraint`, `text`, `DateTime`, `Column`, `create_table`, `Integer`, `create_index`, `ForeignKeyConstraint`, `CheckConstraint`

---

#### downgrade
**Вызывает:** `batch_alter_table`, `drop_table`, `drop_index`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\f07a8f73270d_update_unload_payload_type_values.py`

### Импорты
- `from alembic import op`
- `import sqlalchemy`

### Публичные функции

#### upgrade
**Вызывает:** `values`, `update`, `Enum`, `column`, `table`, `execute`

---

#### downgrade
---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\fa791c45aefa_add_field_is_repair_area_to_idlearea.py`

### Импорты
- `from alembic import op`
- `import sqlalchemy`

### Публичные функции

#### upgrade
**Вызывает:** `add_column`, `Column`, `Boolean`

---

#### downgrade
**Вызывает:** `drop_column`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\migrations\versions\fea74ce0faa7_add_roadnet.py`

### Импорты
- `from alembic import op`
- `import sqlalchemy`
- `from sqlalchemy.dialects import postgresql`

### Публичные функции

#### upgrade
**Вызывает:** `f`, `PrimaryKeyConstraint`, `text`, `DateTime`, `Column`, `Text`, `create_table`, `Integer`, `JSONB`, `ForeignKeyConstraint`

---

#### downgrade
**Вызывает:** `drop_table`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\services\date_time_service.py`

### Импорты
- `from __future__ import annotations`
- `import os`
- `from datetime import datetime, date`
- `from zoneinfo import ZoneInfo, ZoneInfoNotFoundError`
- `from typing import Optional`
- `from pydantic import BaseModel`

### Публичные функции

#### __init__ (`StartEndTimeGenerateService`)
:param tz_name: имя таймзоны (например, 'Europe/Berlin'). Если None — используется переменная окружения TZ или 'UTC'.
:param start_hour: час начала рабочего дня в локальном времени предприятия.
:param end_hour: час конца рабочего дня в локальном времени предприятия.

**Аргументы:**
- `self`
- `tz_name`: Optional[str] = None
- `start_hour`: int = 10
- `end_hour`: int = 18

**Вызывает:** `getenv`, `_load_zone`, `int`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\services\object_service.py`

### Импорты
- `import json`
- `from fastapi import HTTPException`
- `from sqlalchemy.orm import Session`
- `from sqlalchemy import select, delete`
- `from pydantic import ValidationError`
- `from app.models import TrailTruckAssociation, TYPE_MODEL_MAP, validate_object_type`
- `from app.forms import BlastingSchema, TemplateMixin, TemplateRefMixin, RoadNetSchema, MapOverlaySchema, TYPE_SCHEMA_MAP, ObjectActionRequest`

### Публичные функции

#### __init__ (`ObjectDAO`)
**Аргументы:**
- `self`
- `db`: Session

---

#### get_by_id (`ObjectDAO`)
**Аргументы:**
- `self`
- `model`
- `obj_id`: int

**Вызывает:** `select`, `execute`, `scalar`, `where`

---

#### delete_scenario_associations (`ObjectDAO`)
**Аргументы:**
- `self`
- `scenario_id`: int

**Вызывает:** `delete`, `execute`, `where`

---

#### association_exists (`ObjectDAO`)
**Аргументы:**
- `self`
- `scenario_id`: int
- `trail_id`: int
- `truck_id`: int

**Возвращает:** `bool`

**Вызывает:** `select`, `execute`, `scalar`, `where`

---

#### create_association (`ObjectDAO`)
**Аргументы:**
- `self`
- `scenario_id`: int
- `trail_id`: int
- `truck_id`: int

**Вызывает:** `TrailTruckAssociation`, `add`

---

#### __init__ (`ObjectService`)
**Аргументы:**
- `self`
- `db`: Session

**Вызывает:** `ObjectDAO`

---

#### create_object (`ObjectService`)
**Аргументы:**
- `self`
- `data`: ObjectActionRequest

**Вызывает:** `_dispatch`

---

#### update_object (`ObjectService`)
**Аргументы:**
- `self`
- `obj_id`: int
- `data`: ObjectActionRequest

**Вызывает:** `_dispatch`

---

#### __init__ (`BaseObjectService`)
**Аргументы:**
- `self`
- `db`: Session
- `dao`: ObjectDAO
- `model`
- `schema_cls`

---

#### process (`GenericObjectService`)
**Аргументы:**
- `self`
- `data`: ObjectActionRequest
- `action`: str

**Вызывает:** `str`, `_prepare_data`, `isinstance`, `save_geojson_data`, `_apply_form`, `_validate_form`, `HTTPException`, `_get_or_create`, `verify_template_bond`, `verify_template_bond_reversed`, `commit`, `refresh`, `convert_dxf`, `get`

---

#### process (`ScheduleObjectService`)
**Аргументы:**
- `self`
- `data`: ObjectActionRequest
- `action`: str

**Вызывает:** `_prepare_data`, `isinstance`, `_apply_form`, `_validate_form`, `_get_or_create`, `handle_schedule_create`, `commit`, `refresh`, `get`

---

#### process (`ScenarioObjectService`)
**Аргументы:**
- `self`
- `data`: ObjectActionRequest
- `action`: str

**Вызывает:** `_prepare_data`, `create_association`, `isinstance`, `_apply_form`, `_validate_form`, `delete_scenario_associations`, `_get_or_create`, `verify_template_bond`, `association_exists`, `commit`, `refresh`, `get`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\services\quarry_data_service.py`

### Импорты
- `from typing import List, Dict, Any, Tuple`
- `import json`
- `from pydantic import BaseModel`
- `from sqlalchemy import select`
- `from sqlalchemy.orm import Session, defer, selectinload`
- `from app.models import Quarry, Shovel, Truck, Unload, Trail, FuelStation, IdleArea, Scenario, MapOverlay, PlannedIdle, RoadNet`

### Публичные функции

#### __init__ (`QuarryDAO`)
**Аргументы:**
- `self`
- `db_session`: Session

---

#### fetch_all (`QuarryDAO`)
Универсальный fetch для простых моделей: select(model).order_by(model.id.asc()).
Возвращает список экземпляров модели.

**Аргументы:**
- `self`
- `model`

**Возвращает:** `List`

**Вызывает:** `select`, `all`, `scalars`, `order_by`, `asc`, `execute`

---

#### fetch_roadnet_id_pairs (`QuarryDAO`)
Возвращает список (roadnet.id, roadnet.quarry_id) упорядоченных по id ASC.

**Аргументы:**
- `self`

**Возвращает:** `List[Tuple[int, int]]`

**Вызывает:** `select`, `all`, `order_by`, `asc`, `execute`

---

#### fetch_map_overlays_deferred_geojson (`QuarryDAO`)
Возвращает MapOverlay без подгрузки большого поля geojson_data.

**Аргументы:**
- `self`

**Возвращает:** `List`

**Вызывает:** `select`, `all`, `scalars`, `order_by`, `asc`, `defer`, `options`, `execute`

---

#### fetch_trails_with_quarry_id (`QuarryDAO`)
Возвращает список кортежей (Trail, quarry_id) — делается join через Shovel.
Также подгружаем associations (selectinload).

**Аргументы:**
- `self`

**Возвращает:** `List[Tuple['Trail', int]]`

**Вызывает:** `select`, `all`, `options`, `order_by`, `asc`, `join`, `selectinload`, `execute`

---

#### __init__ (`QuarryDataService`)
**Аргументы:**
- `self`
- `db_session`: Session

**Вызывает:** `QuarryDAO`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\services\scenario_service.py`

### Импорты
- `from typing import List, Dict, Any, Optional`
- `import json`
- `from datetime import datetime`
- `from pydantic import BaseModel`
- `from datetime import datetime`
- `from sqlalchemy import select`
- `from sqlalchemy.orm import Session, selectinload`
- `from app.models import Scenario, Trail, Shovel`

### Публичные функции

#### __init__ (`ScenarioDAO`)
**Аргументы:**
- `self`
- `db_session`: Session

---

#### fetch_all_with_assocs (`ScenarioDAO`)
Возвращает все Scenario.

**Аргументы:**
- `self`

**Возвращает:** `List[Scenario]`

**Вызывает:** `select`, `all`, `scalars`, `options`, `order_by`, `asc`, `selectinload`, `execute`

---

#### fetch_trails_by_quarry (`ScenarioDAO`)
Возвращает Trail, принадлежащие карьерам quarry_id (через Shovel).

**Аргументы:**
- `self`
- `quarry_id`: int

**Возвращает:** `List[Trail]`

**Вызывает:** `select`, `selectinload`, `all`, `scalars`, `where`, `order_by`, `asc`, `join`, `options`, `execute`

---

#### __init__ (`ScenarioService`)
**Аргументы:**
- `self`
- `db_session`: Session

**Вызывает:** `ScenarioDAO`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\services\schedule_data_service.py`

### Импорты
- `import json`
- `from datetime import datetime`
- `from typing import List, Optional, Any`
- `from zoneinfo import ZoneInfo`
- `from sqlalchemy import select`
- `from sqlalchemy.orm import Session`
- `from pydantic import BaseModel`
- `from app.models import Quarry`
- `from app.shift import ShiftLogic`
- `from app.shift import ShiftConfigDataException, ShiftConfigParseException`

### Публичные функции

#### __init__ (`ScheduleDAO`)
**Аргументы:**
- `self`
- `db_session`: Session

---

#### fetch_filtered (`ScheduleDAO`)
Возвращает список отфильтрованных элементов расписания в виде DTO.

**Аргументы:**
- `self`
- `model`
- `start_time_utc`: datetime
- `end_time_utc`: datetime
- `quarry_id`: int
- `schedule_type`: str

**Возвращает:** `List[ScheduleItemDTO]`

**Вызывает:** `select`, `isinstance`, `all`, `getattr`, `scalars`, `loads`, `where`, `keys`, `order_by`, `ScheduleItemDTO`, `asc`, `set`, `append`, `execute`, `get`

---

#### __init__ (`ScheduleDataService`)
**Аргументы:**
- `self`
- `db_session`: Session

**Вызывает:** `ScheduleDAO`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\services\simulation_id_service.py`

### Импорты
- `from datetime import datetime, timedelta`
- `from zoneinfo import ZoneInfo`
- `import uuid`
- `import json`
- `from operator import itemgetter`
- `from app.consts import STORED_RESULTS_NUMBER`
- `from app.models import RoadNet`
- `from app.sim_engine.writer import BatchWriter`
- `from app.sim_engine.simulation_manager import SimulationManager`
- `from typing import Any, Dict, Optional`
- `from pydantic import BaseModel, Field, field_validator, ValidationInfo`
- `from sqlalchemy import select`
- `from sqlalchemy.orm import Session`
- `from app.models import RoadNet, TYPE_SCHEDULE_MAP`

### Публичные функции

#### validate_quarry (`SimulationRequestDTO`)
**Аргументы:**
- `cls`
- `v`

**Вызывает:** `field_validator`, `ValueError`

---

#### validate_times (`SimulationRequestDTO`)
**Аргументы:**
- `cls`
- `v`: str
- `info`: ValidationInfo

**Вызывает:** `ValueError`, `field_validator`, `replace`, `get`, `fromisoformat`

---

#### __init__ (`SimulationDAO`)
**Аргументы:**
- `self`
- `db_session`: Session

---

#### fetch_road_net_by_id (`SimulationDAO`)
**Аргументы:**
- `self`
- `road_net_id`: int

**Вызывает:** `select`, `execute`, `scalar`, `where`

---

#### get_filtered_schedule_items (`SimulationDAO`)
**Аргументы:**
- `self`
- `model`
- `start_time_utc`
- `end_time_utc`
- `quarry_id`
- `schedule_type`

**Возвращает:** `list`

**Вызывает:** `select`, `isinstance`, `set`, `getattr`, `scalars`, `loads`, `where`, `order_by`, `asc`, `keys`, `append`, `execute`

---

#### fetch_schedules (`SimulationDAO`)
Получает blasting и planned_idle расписания для карьера.

**Аргументы:**
- `self`
- `quarry_id`: int
- `start_time`: datetime
- `end_time`: datetime

**Возвращает:** `dict`

**Вызывает:** `get_filtered_schedule_items`, `get`

---

#### __init__ (`GetSimIdService`)
**Аргументы:**
- `self`
- `data`: SimulationRequestDTO
- `db`
- `redis_client`

**Вызывает:** `SimulationDAO`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\services\template_service.py`

### Импорты
- `from typing import List, Dict, Any, Optional`
- `from pydantic import BaseModel`
- `from sqlalchemy import select`
- `from sqlalchemy.orm import Session`
- `from app.forms import ShovelTemplate, TruckTemplate, UnloadTemplate, FuelStationTemplate`

### Публичные функции

#### __init__ (`TemplateDAO`)
**Аргументы:**
- `self`
- `db_session`: Session

---

#### fetch_all (`TemplateDAO`)
Вернуть все строки модели, упорядоченные по id ASC.

**Аргументы:**
- `self`
- `model`

**Возвращает:** `List`

**Вызывает:** `select`, `all`, `scalars`, `order_by`, `asc`, `execute`

---

#### __init__ (`AllTemplatesListService`)
**Аргументы:**
- `self`
- `db_session`: Session

**Вызывает:** `TemplateDAO`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\config.py`

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\enums.py`

### Импорты
- `import enum`

### Публичные функции

#### ru (`ObjectType`)
**Аргументы:**
- `self`

**Возвращает:** `str`

---

#### key (`ObjectType`)
**Аргументы:**
- `self`

**Возвращает:** `str`

---

#### code (`ObjectType`)
**Аргументы:**
- `self`

**Возвращает:** `int`

---

#### ru (`IdleAreaType`)
**Аргументы:**
- `self`

**Возвращает:** `str`

---

#### key (`IdleAreaType`)
**Аргументы:**
- `self`

**Возвращает:** `str`

---

#### code (`IdleAreaType`)
**Аргументы:**
- `self`

**Возвращает:** `int`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\events.py`

### Импорты
- `import enum`
- `from dataclasses import dataclass, fields, is_dataclass, asdict`
- `from enum import Enum`
- `from typing import Any`
- `from app.sim_engine.core.simulations.utils.mixins import DataclassEnumSerializerMixin`
- `from app.sim_engine.enums import ObjectType`

### Публичные функции

#### code (`EventType`)
**Аргументы:**
- `self`

---

#### ru (`EventType`)
**Аргументы:**
- `self`

---

#### en (`EventType`)
**Аргументы:**
- `self`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\planner.py`

### Импорты
- `from __future__ import annotations`
- `import logging`
- `from collections import defaultdict`
- `from copy import deepcopy`
- `from dataclasses import dataclass`
- `from datetime import datetime`
- `from typing import Dict, Tuple, List, Optional`
- `from math import floor`
- `from ortools.sat.python import cp_model`
- `from pulp import LpProblem, LpMaximize, LpVariable, LpBinary, LpInteger, lpSum, LpStatus, value, PULP_CBC_CMD, HiGHS_CMD, SCIP_CMD`
- `import os`
- `from app.sim_engine.core.calculations.shovel import ShovelCalc`
- `from app.sim_engine.core.calculations.truck import TruckCalc`
- `from app.sim_engine.core.calculations.unload import UnloadCalc`
- `from app.sim_engine.core.geometry import build_route_edges_by_road_net, build_route_edges_by_road_net_from_position`
- `from app.sim_engine.core.props import SimData, PlannedTrip`
- `from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver`
- `from app.sim_engine.enums import ObjectType`

### Публичные функции

#### truck_ids (`InputPlanningData`)
**Аргументы:**
- `self`

**Возвращает:** `List[int]`

**Вызывает:** `sorted`, `keys`

---

#### shovel_ids (`InputPlanningData`)
**Аргументы:**
- `self`

**Возвращает:** `List[int]`

**Вызывает:** `sorted`, `keys`

---

#### unload_ids (`InputPlanningData`)
**Аргументы:**
- `self`

**Возвращает:** `List[int]`

**Вызывает:** `sorted`, `keys`

---

#### compute_Kmax_i
Грубая верхняя граница числа рейсов для самосвала i

**Аргументы:**
- `inst`: InputPlanningData
- `i`: int

**Возвращает:** `int`

**Вызывает:** `floor`, `max`, `min`, `keys`

---

#### default_Kmax
Если Kmax не задан, вычислить его для каждого самосвала

**Аргументы:**
- `inst`: InputPlanningData

**Возвращает:** `Dict[int, int]`

**Вызывает:** `compute_Kmax_i`

---

#### a_use
**Аргументы:**
- `i`
- `k`
- `j`

**Вызывает:** `lpSum`

---

#### b_use
**Аргументы:**
- `i`
- `k`
- `z`

**Вызывает:** `lpSum`

---

#### build_model
Собираем все ограничения и условия поиска решения

**Аргументы:**
- `inst`: InputPlanningData
- `shovel_queue`: bool = True

**Вызывает:** `lpSum`

---

#### solve_and_extract
Решить модель и получить расписание
    

**Аргументы:**
- `inst`: InputPlanningData

**Вызывает:** `int`, `ValueError`, `cpu_count`, `value`, `PULP_CBC_CMD`, `solve`, `range`, `HiGHS_CMD`, `round`, `append`, `build_model`, `info`, `sim_conf`, `sort`

---

#### build_cp_model
**Аргументы:**
- `inst`: InputPlanningData
- `use_individual_kmax`: bool = True

**Вызывает:** `int`, `CpModel`, `OnlyEnforceIf`, `sum`, `Add`, `values`, `range`, `max`, `dict`, `round`, `compute_Kmax_i`, `NewBoolVar`, `append`, `AddNoOverlap`, `Maximize`, `Not`, `NewOptionalIntervalVar`, `AddBoolOr`, `NewIntVar`

---

#### solve_and_extract_cp
Решение CP‑SAT и извлечение расписания в прежнем формате.

**Аргументы:**
- `inst`: InputPlanningData
- `time_limit`: Optional[int] = None
- `num_workers`: int = 16

**Вызывает:** `build_cp_model`, `int`, `float`, `range`, `BooleanValue`, `Solve`, `ObjectiveValue`, `CpSolver`, `append`, `Value`, `get`, `info`, `sim_conf`, `sort`

---

#### make_example
Заполняем исходные данные
Количество техники, матрица времен выполнение каждой операции (полный перебор)

**Возвращает:** `InputPlanningData`

**Вызывает:** `range`, `InputPlanningData`

---

#### dummy_func
---

#### get_planning_data
Метод набивающий матрицу данных

**Аргументы:**
- `simdata`: SimData

**Возвращает:** `InputPlanningData`

**Вызывает:** `values`, `int`, `build_route_edges_by_road_net_from_position`, `unload_calculation_by_norm`, `len`, `build_route_edges_by_road_net`, `calculate_load_cycles`, `dict`, `calculate_time_motion_by_edges`, `InputPlanningData`

---

#### run_planning
**Аргументы:**
- `simdata`: SimData

**Вызывает:** `get_planning_data`, `solve_and_extract_cp`, `info`, `sim_conf`

---

#### run_planning_trips
**Аргументы:**
- `sim_data`: SimData
- `exclude_objects`: dict[str, list[int]]

**Возвращает:** `dict`

**Вызывает:** `defaultdict`, `int`, `run_planning`, `PlannedTrip`, `append`, `pop`, `total_seconds`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\reliability.py`

### Импорты
- `import logging`
- `import random`
- `import numpy`
- `from scipy import stats`

### Публичные функции

#### extract_metric
Извлекает выбранную метрику из первых записей

Параметры:
    runs   : исходные записи симуляций
    metric : название метрики: "trips" | "volume" | "weight"

Возвращает:
    Массив значений выбранной метрики без пропусков.

**Аргументы:**
- `runs`: list[dict]
- `metric`: str

**Возвращает:** `np.ndarray`

**Вызывает:** `ValueError`, `float`, `append`, `asarray`, `isnan`, `get`

---

#### descriptive_stats
Краткая описательная статистика, полезная для понимания формы распределения

Возвращает:
    n        : объём выборки
    mean     : среднее
    std      : выборочное стандартное отклонение
    median   : медиана
    q1, q3   : квартильный интервал
    iqr      : межквартильный размах
    skew     : асимметрия
    kurtosis : избыточный эксцесс
    xmin,xmax: минимальное и максимальное наблюдения

**Аргументы:**
- `x`: np.ndarray

**Возвращает:** `dict`

**Вызывает:** `quantile`, `kurtosis`, `float`, `len`, `skew`, `max`, `median`, `dict`, `std`, `min`, `mean`, `asarray`

---

#### predictive_interval_t
Двусторонний t-предиктивный интервал уровня 1-α для будущего наблюдения

Идея:
    Если данные близки к симметрии и нормальности, то
    (X_new - среднее)/[S*sqrt(1+1/n)] ~ t_{n-1}.
    Отсюда границы: среднее ± t_{1-α/2, n-1} * S * sqrt(1+1/n).

Возвращает:
    (нижняя, верхняя) границы вероятностного коридора

**Аргументы:**
- `x`: np.ndarray
- `alpha`: float = 0.05

**Возвращает:** `tuple[float, float]`

**Вызывает:** `ppf`, `float`, `len`, `sqrt`, `std`, `mean`, `asarray`

---

#### robust_pi_quantiles
Робастный предиктивный интервал по эмпирическим квантилям.

Идея:
    Никаких предположений о форме: берём квантиль α/2 и 1-α/2.
    Интервал естественно подстраивается под асимметрию распределения

**Аргументы:**
- `x`: np.ndarray
- `alpha`: float = 0.05

**Возвращает:** `tuple[float, float]`

**Вызывает:** `float`, `len`, `asarray`, `quantile`

---

#### split_conformal_pi
Симметричный split-conformal интервал с гарантией покрытия ≈ 1-α

Идея:
    Делим данные на обучение и калибровку.
    На обучении считаем центр (среднее), на калибровке - остатки |X-центр|
    Берём дискретный квантиль остатка уровня 1-α
    симметрично откладываем от центра.

**Аргументы:**
- `x`: np.ndarray
- `alpha`: float = 0.05
- `seed`: int = 123

**Возвращает:** `tuple[float, float]`

**Вызывает:** `clip`, `int`, `ceil`, `float`, `partition`, `shuffle`, `abs`, `sort`, `default_rng`, `len`, `mean`, `asarray`, `copy`

---

#### lognormal_pi
Интервал при лог-нормальной аппроксимации

**Аргументы:**
- `x`: np.ndarray
- `alpha`: float = 0.05

**Возвращает:** `tuple[float, float]`

**Вызывает:** `ppf`, `predictive_interval_t`, `float`, `log`, `len`, `any`, `sqrt`, `std`, `mean`, `asarray`, `exp`

---

#### kde_hdi
Интервал наибольшей плотности (HDI) по сглаженной оценке плотности (KDE).

**Аргументы:**
- `x`: np.ndarray
- `alpha`: float = 0.05
- `grids`: int = 2048

**Возвращает:** `tuple[float, float]`

**Вызывает:** `gaussian_kde`, `float`, `linspace`, `kde`, `argsort`, `max`, `cumsum`, `min`, `len`, `asarray`, `sort`

---

#### bootstrap_pi
Бутстрэп-интервал (перцентильный): эмпирическое предиктивное распределение.

**Аргументы:**
- `x`: np.ndarray
- `alpha`: float = 0.05
- `B`: int = 5000
- `seed`: int = 123

**Возвращает:** `tuple[float, float]`

**Вызывает:** `quantile`, `float`, `default_rng`, `choice`, `asarray`

---

#### jackknife_plus_pi
Интервал Jackknife+

**Аргументы:**
- `x`: np.ndarray
- `alpha`: float = 0.05

**Возвращает:** `tuple[float, float]`

**Вызывает:** `quantile`, `predictive_interval_t`, `float`, `abs`, `array`, `len`, `sum`, `mean`, `asarray`

---

#### split_conformal_asymmetric
Асимметричный split-conformal

**Аргументы:**
- `x`: np.ndarray
- `alpha`: float = 0.05
- `seed`: int = 123

**Возвращает:** `tuple[float, float]`

**Вызывает:** `quantile`, `float`, `shuffle`, `default_rng`, `len`, `mean`, `asarray`, `copy`

---

#### inv_yj
**Аргументы:**
- `yv`: np.ndarray
- `lmbda`: float

**Возвращает:** `np.ndarray`

**Вызывает:** `finfo`, `empty_like`, `power`, `abs`, `errstate`, `any`, `expm1`, `maximum`, `exp`, `asarray`

---

#### yeojohnson_pi
Интервал на основе преобразования Йео–Джонсона

**Аргументы:**
- `x`: np.ndarray
- `alpha`: float = 0.05

**Возвращает:** `tuple[float, float]`

**Вызывает:** `finfo`, `empty_like`, `power`, `abs`, `errstate`, `any`, `expm1`, `maximum`, `exp`, `asarray`

---

#### half_sample_mode
Робастная мода (Half-Sample Mode, HSM).

**Аргументы:**
- `x`: np.ndarray

**Возвращает:** `float`

**Вызывает:** `argmin`, `int`, `float`, `len`, `half_sample_mode`, `mean`, `asarray`, `sort`

---

#### kde_mode
Мода по сглаженной плотности (KDE)

**Аргументы:**
- `x`: np.ndarray
- `grids`: int = 512

**Возвращает:** `float`

**Вызывает:** `gaussian_kde`, `float`, `linspace`, `kde`, `max`, `min`, `argmax`

---

#### loo_coverage
Эмпирическое покрытие leave-one-out кросс-валидайция

**Аргументы:**
- `x`: np.ndarray
- `get_interval`
- `alpha`: float = 0.05
- `**kwargs` (kwarg)

**Возвращает:** `float`

**Вызывает:** `int`, `get_interval`, `range`, `len`, `delete`, `asarray`

---

#### pit_values_t_predictive
PIT (вероятностное преобразование) для t-предиктивной модели

**Аргументы:**
- `x`: np.ndarray

**Возвращает:** `np.ndarray`

**Вызывает:** `float`, `len`, `max`, `sqrt`, `cdf`, `std`, `mean`, `asarray`

---

#### interval_width
Ширина интервала. Если границы нечисловые - вернуть бесконечность,
чтобы такой метод оказался в конце при сравнении

**Аргументы:**
- `iv`: tuple[float, float]

**Возвращает:** `float`

**Вызывает:** `float`, `isfinite`

---

#### score
**Аргументы:**
- `name`: str

**Вызывает:** `interval_width`, `max`, `abs`, `isnan`, `get`

---

#### select_best_interval
Выбирает лучший интервал по простому и понятному правилу.

Правило:
    1) Сначала фильтруем методы с покрытием LOO не хуже цели (1-α-допуск)
    2) Среди них берём наименьшую ширину
    3) При сильной асимметрии (|skew|>1) отдаём предпочтение робастным методам

Возвращает:
    (название метода, его интервал, строка-обоснование выбора)

**Аргументы:**
- `alpha`: float
- `intervals`: dict[str, tuple[float, float]]
- `coverages`: dict[str, float]
- `skew`: float
- `tol`: float = 0.03

**Возвращает:** `tuple[str, tuple[float, float], str]`

**Вызывает:** `interval_width`, `max`, `abs`, `isnan`, `get`

---

#### assess_stability
Оценка стабильности переданного набора данных с учётом предыдущих оценок на более
узкой выборке (от предыдущего запуска требуются `prev_metric_median` и `cur_stable_streak`).

Критерии оценки:
    1) Относительная половина ширины t-интервала мала:
       ((верх - низ)/2) / |медиана| ≤ r_target.
       Это означает, что коридор неопределённости относительно уровня
       метрики уже достаточно узок
    2) Медиана почти не меняется относительно предыдущего шага:
       |сдвиг медианы| / |медиана| ≤ delta_target

Параметр `consecutive` требует, чтобы оба условия выполнялись указанное
число шагов подряд - так мы избегаем преждевременной остановки
из-за случайных колебаний

**Аргументы:**
- `results`: list[dict]
- `metric`: str = 'weight'
- `prev_metric_median`: float | None = None
- `cur_stable_streak`: int = 0
- `alpha`: float = 0.05
- `r_target`: float = 0.05
- `delta_target`: float = 0.01
- `consecutive`: int = 2

**Возвращает:** `tuple[bool, np.ndarray, float, int]`

**Вызывает:** `predictive_interval_t`, `float`, `extract_metric`, `len`, `max`, `median`, `abs`, `info`

---

#### calc_reliability
Расчёт наиболее правдоподобного значения на основании стабильной выборки данных

**Аргументы:**
- `metric_array`: np.ndarray
- `alpha`: float = 0.05
- `boot_b`: int = 5000
- `seed`: int | None = None

**Возвращает:** `tuple[float, float, float]`

**Вызывает:** `bootstrap_pi`, `split_conformal_pi`, `interval_width`, `kstest`, `descriptive_stats`, `jackknife_plus_pi`, `pit_values_t_predictive`, `anderson`, `float`, `kde_hdi`, `half_sample_mode`, `median`, `lognormal_pi`, `info`, `isnan`, `split_conformal_asymmetric`, `yeojohnson_pi`, `loo_coverage`, `getrandbits`, `kde_mode`, `mean`, `get`, `items`, `predictive_interval_t`, `shapiro`, `len`, `select_best_interval`, `robust_pi_quantiles`

---

#### find_closest_result
Поиск ближайшего к правдоподобному значению результата, не превышающего лучшее максимальное

**Аргументы:**
- `results`: list[dict]
- `metric_reliable`: float
- `metric_best_max`: float
- `metric`: str = 'weight'

**Возвращает:** `dict`

**Вызывает:** `abs`, `enumerate`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\serializer.py`

### Импорты
- `import json`
- `from datetime import datetime, timedelta`
- `from app.sim_engine.core.props import TruckProperties, ShovelProperties, UnlProperties, FuelStationProperties, Truck, Shovel, Unload, FuelStation, SimData, Route, Segment, Point, ShiftChangeArea, Blasting, PlannedIdle, IdleAreaStorage, IdleArea`
- `from app.utils import utc_to_enterprise, TZ`

### Публичные функции

#### calculate_lunch_breaks
Расчитывает обеденные перерывы в заданном временном интервале

**Аргументы:**
- `start_time`: datetime
- `end_time`: datetime
- `shift_config`: list[dict]
- `lunch_break_offset`: int
- `lunch_break_duration`: int

**Вызывает:** `append`, `sort`, `max`, `any`, `min`, `replace`, `abs`, `total_seconds`, `timedelta`

---

#### collect_planned_idles
Организует список плановых простоев в словарь,
сгруппированный по vehicle_type и vehicle_id,
с сортировкой по start_time.

Args:
    idles_data (list): Список словарей с информацией о простоях

Returns:
    dict: Словарь вида {(vehicle_type, vehicle_id): [sorted_downtimes]}}

**Аргументы:**
- `idles_data`: list[dict]

**Вызывает:** `values`, `isinstance`, `PlannedIdle`, `isoformat`, `utc_to_enterprise`, `append`, `sort`

---

#### create_blasting_list
Создает список объектов Blasting из данных взрывных работ.

Args:
    data: Словарь с данными взрывных работ
    timezone: Часовой пояс

Returns:
    List[Blasting]: Отсортированный по start_time список объектов Blasting

**Аргументы:**
- `data`: dict
- `timezone`: str = TZ

**Возвращает:** `list[Blasting]`

**Вызывает:** `isinstance`, `utc_to_enterprise`, `isoformat`, `Blasting`, `append`, `sort`

---

#### serialize (`SimDataSerializer`)
**Аргументы:**
- `cls`
- `data`: dict

**Возвращает:** `SimData`

**Вызывает:** `collect_planned_idles`, `int`, `ShovelProperties`, `Shovel`, `create_blasting_list`, `calculate_lunch_breaks`, `Point`, `utc_to_enterprise`, `IdleAreaStorage`, `Segment`, `append`, `UnlProperties`, `get`, `SimData`, `Unload`, `FuelStationProperties`, `FuelStation`, `TruckProperties`, `IdleArea`, `Route`, `Truck`, `total_seconds`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\simulate.py`

### Импорты
- `import functools`
- `import logging`
- `import multiprocessing`
- `from typing import Callable`
- `from app.sim_engine.core.environment import QSimEnvironment`
- `from app.sim_engine.core.geometry import Point, Route, RouteEdge, build_route_by_road_net, build_route_edges_by_road_net`
- `from app.sim_engine.core.props import SimData, PlannedTrip`
- `from app.sim_engine.core.simulations.fuel_station import FuelStation`
- `from app.sim_engine.core.simulations.quarry import Quarry`
- `from app.sim_engine.core.simulations.shovel import Shovel`
- `from app.sim_engine.core.simulations.truck import Truck`
- `from app.sim_engine.core.simulations.unload import Unload`
- `from app.sim_engine.enums import ObjectType`
- `from app.sim_engine.reliability import assess_stability, calc_reliability, find_closest_result`
- `from app.sim_engine.writer import IWriter, DictReliabilityWriter`

### Публичные функции

#### wrapper
**Аргументы:**
- `*args` (vararg)
- `**kwargs` (kwarg)

**Вызывает:** `func`, `wraps`, `DataValidateError`

---

#### sim_data_validate
**Аргументы:**
- `func`

**Вызывает:** `func`, `wraps`, `DataValidateError`

---

#### run_simulation
Run simulation with manual truck routes

This func needs to be **picklable** for `run_reliability` (multiprocessing limitations)

**Аргументы:**
- `sim_data`: SimData
- `writer`: IWriter
- `sim_conf`: dict

**Возвращает:** `dict`

**Вызывает:** `Shovel`, `QSimEnvironment`, `values`, `PlannedTrip`, `get_summary`, `info`, `Point`, `getattr`, `build_route_by_road_net`, `run`, `build_route_edges_by_road_net`, `append`, `finalize`, `Quarry`, `prepare_seeded_random`, `Unload`, `FuelStation`, `update_data`, `Truck`

---

#### run_simulation_for_planned_trips
Run simulation with auto truck routes

This func needs to be **picklable** for `run_reliability` (multiprocessing limitations)

**Аргументы:**
- `sim_data`: SimData
- `writer`: IWriter
- `planned_trips`: dict[int, list[PlannedTrip]]
- `sim_conf`: dict

**Возвращает:** `dict`

**Вызывает:** `Unload`, `finalize`, `values`, `Quarry`, `get_summary`, `run`, `FuelStation`, `update_data`, `Shovel`, `info`, `append`, `Truck`, `QSimEnvironment`, `get`, `Point`, `prepare_seeded_random`

---

#### run_reliability
Run given simulation engaging reliablility calculation

`run_func` needs to be **picklable** (multiprocessing limitations)

**Аргументы:**
- `run_func`: Callable
- `sim_data`: SimData
- `writer`: IWriter
- `sim_conf`: dict
- `*extra_run_func_args` (vararg)

**Возвращает:** `dict`

**Вызывает:** `calc_reliability`, `int`, `extend`, `assess_stability`, `get_context`, `Pool`, `round`, `info`, `range`, `len`, `DictReliabilityWriter`, `run_func`, `find_closest_result`, `starmap`, `cpu_count`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\simulation_manager.py`

### Импорты
- `import inspect`
- `import logging`
- `import multiprocessing`
- `import traceback`
- `from collections import defaultdict`
- `from multiprocessing import Manager`
- `from multiprocessing.managers import DictProxy`
- `from typing import Any`
- `from app.sim_engine.config import SIM_CONFIG`
- `from app.sim_engine.core.planner.manage import Planner`
- `from app.sim_engine.core.props import SimData, PlannedTrip`
- `from app.sim_engine.infra.exception_traceback import catch_errors`
- `from app.sim_engine.serializer import SimDataSerializer`
- `from app.sim_engine.simulate import run_reliability, run_simulation, run_simulation_for_planned_trips`
- `from app.sim_engine.writer import IWriter, DictSimpleWriter`

### Публичные функции

#### validate (`IManagerValidator`)
**Аргументы:**
- `data`: Any

**Возвращает:** `Any`

---

#### validate (`RawSimDataValidator`)
**Аргументы:**
- `data`: dict

**Возвращает:** `dict`

**Вызывает:** `SimDataValidationError`, `isinstance`

---

#### validate (`SimConfigOptionsValidator`)
**Аргументы:**
- `data`: dict

**Возвращает:** `dict`

**Вызывает:** `isinstance`, `SimConfigValidationError`

---

#### __init__ (`SimulationManager`)
Инициализация менеджера.

Аргументы:
raw_data - сырые данные, необходимые для проведения симуляции/планирования
options - опции конфигурации для применения в процессе симуляции/планирования
writer - писарь результатов симуляции
raw_data_validator - валидатор сырых данных raw_data
options_validator - валидатор опций конфигурации

**Аргументы:**
- `self`
- `raw_data`: dict
- `options`: dict | None = None
- `writer`: type[IWriter] = DictSimpleWriter
- `raw_data_validator`: type[IManagerValidator] = RawSimDataValidator
- `options_validator`: type[IManagerValidator] = SimConfigOptionsValidator
- `use_multiprocessing`: bool = False

**Возвращает:** `None`

**Вызывает:** `validate_validator`, `__set_default_config`, `set_options`, `validate_writer`, `validate`, `serialize`

---

#### simdata (`SimulationManager`)
Возвращает текущие сериализованные данные, используемые для симуляции

**Аргументы:**
- `self`

**Возвращает:** `SimData`

---

#### config (`SimulationManager`)
Возвращает текущую конфигурацию

**Аргументы:**
- `self`

**Возвращает:** `dict`

---

#### writer (`SimulationManager`)
Возвращает текущий класс логгера симуляции

**Аргументы:**
- `self`

**Возвращает:** `IWriter`

---

#### result (`SimulationManager`)
Возвращает результат симуляции при его наличии

**Аргументы:**
- `self`

**Возвращает:** `dict`

**Вызывает:** `RuntimeError`

---

#### set_new_simdata (`SimulationManager`)
Проводит валидацию переданных сырых данных для симуляции и
устанавливает сериализованные данные в качестве текущих

**Аргументы:**
- `self`
- `raw_data`: dict

**Возвращает:** `None`

**Вызывает:** `serialize`, `validate`

---

#### set_options (`SimulationManager`)
Проводит валидацию и устанавливает переданные опции конфигурации

**Аргументы:**
- `self`
- `options`: dict

**Возвращает:** `None`

**Вызывает:** `update`, `validate`

---

#### validate_writer (`SimulationManager`)
Производит валидацию переданного писаря результатов симуляции

**Аргументы:**
- `writer`: Any

**Возвращает:** `IWriter`

**Вызывает:** `isinstance`, `issubclass`, `SimWriterValidationError`, `writer`, `isclass`

---

#### validate_validator (`SimulationManager`)
Производит валидацию переданного валидатора

**Аргументы:**
- `validator`: Any

**Возвращает:** `IManagerValidator`

**Вызывает:** `ValidatorValidationError`, `isinstance`, `issubclass`, `isclass`, `validator`

---

#### set_raw_data_validator (`SimulationManager`)
Устанавливает валидатор сырых данных для симуляции

**Аргументы:**
- `self`
- `validator`: IManagerValidator

**Возвращает:** `None`

**Вызывает:** `validate_validator`

---

#### set_options_validator (`SimulationManager`)
Устанавливает валидатор опций конфигурации

**Аргументы:**
- `self`
- `validator`: IManagerValidator

**Возвращает:** `None`

**Вызывает:** `validate_validator`

---

#### run (`SimulationManager`)
Запускает симуляцию в ручном/автоматическом режиме (зависит от текущей конфигурации)
в отдельном процессе

**Аргументы:**
- `self`

**Возвращает:** `dict`

**Вызывает:** `_process_simulation`, `_run_using_multiprocessing`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\states.py`

### Импорты
- `from enum import Enum`

### Публичные функции

#### is_work (`TruckState`)
**Аргументы:**
- `self`

---

#### is_moving (`TruckState`)
**Аргументы:**
- `self`

---

#### ru (`TruckState`)
**Аргументы:**
- `self`

---

#### en (`TruckState`)
**Аргументы:**
- `self`

---

#### is_work (`ExcState`)
**Аргументы:**
- `self`

---

#### ru (`ExcState`)
**Аргументы:**
- `self`

---

#### en (`ExcState`)
**Аргументы:**
- `self`

---

#### is_work (`UnloadState`)
**Аргументы:**
- `self`

---

#### ru (`UnloadState`)
**Аргументы:**
- `self`

---

#### en (`UnloadState`)
**Аргументы:**
- `self`

---

#### ru (`FuelStationState`)
**Аргументы:**
- `self`

---

#### en (`FuelStationState`)
**Аргументы:**
- `self`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\writer.py`

### Импорты
- `from abc import ABC, abstractmethod`
- `from app.sim_engine.events import Event`

### Публичные функции

#### update_data (`IWriter`)
**Аргументы:**
- `self`
- `key`: str
- `**kwargs` (kwarg)

**Возвращает:** `None`

---

#### push_event (`IWriter`)
**Аргументы:**
- `self`
- `evt`: Event

**Возвращает:** `None`

---

#### writerow (`IWriter`)
**Аргументы:**
- `self`
- `row`: dict

**Возвращает:** `None`

---

#### finalize (`IWriter`)
**Аргументы:**
- `self`

---

#### __init__ (`DictSimpleWriter`)
**Аргументы:**
- `self`

**Возвращает:** `None`

---

#### update_data (`DictSimpleWriter`)
**Аргументы:**
- `self`
- `key`
- `**kwargs` (kwarg)

**Возвращает:** `None`

**Вызывает:** `update`

---

#### push_event (`DictSimpleWriter`)
**Аргументы:**
- `self`
- `evt`: Event

**Возвращает:** `None`

**Вызывает:** `to_dict`, `append`

---

#### writerow (`DictSimpleWriter`)
**Аргументы:**
- `self`
- `row`: dict

**Возвращает:** `None`

**Вызывает:** `append`

---

#### finalize (`DictSimpleWriter`)
**Аргументы:**
- `self`

**Возвращает:** `dict`

---

#### __init__ (`DictReliabilityWriter`)
**Аргументы:**
- `self`

**Возвращает:** `None`

**Вызывает:** `super`, `__init__`, `pop`

---

#### push_event (`DictReliabilityWriter`)
**Аргументы:**
- `self`
- `evt`: Event

**Возвращает:** `None`

---

#### writerow (`DictReliabilityWriter`)
**Аргументы:**
- `self`
- `row`: dict

**Возвращает:** `None`

---

#### __init__ (`BatchWriter`)
**Аргументы:**
- `self`
- `batch_size_seconds`: int = 60

**Возвращает:** `None`

---

#### update_data (`BatchWriter`)
**Аргументы:**
- `self`
- `key`
- `**kwargs` (kwarg)

**Возвращает:** `None`

**Вызывает:** `getattr`, `update`

---

#### push_event (`BatchWriter`)
**Аргументы:**
- `self`
- `evt`: Event

**Возвращает:** `None`

**Вызывает:** `to_dict`, `append`

---

#### writerow (`BatchWriter`)
**Аргументы:**
- `self`
- `row`: dict

**Возвращает:** `None`

**Вызывает:** `append`, `int`

---

#### finalize (`BatchWriter`)
**Аргументы:**
- `self`

**Возвращает:** `dict`

**Вызывает:** `len`, `list`, `keys`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\__init__.py`

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\coefficients.py`

### Публичные функции

#### koef_vlazhnosti
Возвращает коэффициент по влажности грунта (%)
0–5%   → 0.8 (сухой)
5–15%  → 1.0 (оптимальная)
15–30% → 1.2 (влажный)
30–50% → 1.5–2.0 (глинистый)

**Аргументы:**
- `percent`: float

**Возвращает:** `float`

**Вызывает:** `max`, `min`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\constants.py`

### Импорты
- `from app.enums import PayloadType, UnloadType`

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\environment.py`

### Импорты
- `import simpy`
- `from app.sim_engine.core.planner.solvers.greedy import GreedySolver`
- `from app.sim_engine.core.props import SimData`
- `from app.sim_engine.core.simulations.entities import SimContext`
- `from app.sim_engine.core.simulations.utils.idle_area_service import IdleAreaService`
- `from app.sim_engine.core.simulations.utils.service_locator import ServiceLocator`
- `from app.sim_engine.core.simulations.utils.trip_service import TripService`
- `from app.sim_engine.writer import IWriter`

### Публичные функции

#### __init__ (`QSimEnvironment`)
**Аргументы:**
- `self`
- `sim_data`: SimData
- `writer`: IWriter
- `sim_conf`: dict

**Вызывает:** `__init__`, `GreedySolver`, `SimContext`, `unbind_all`, `TripService`, `super`, `IdleAreaService`, `bind`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\geometry.py`

### Импорты
- `import math`
- `import copy`
- `from dataclasses import dataclass`
- `from typing import Tuple`
- `from roadnet.core import Edge, Vertex, RoadNetFactory`
- `from app.sim_engine.core.props import Route, SimData`
- `from app.sim_engine.enums import ObjectType`

### Публичные функции

#### __init__ (`Route`)
**Аргументы:**
- `self`
- `name`: str
- `points`: list[Point]

---

#### start (`Route`)
**Аргументы:**
- `self`

---

#### end (`Route`)
**Аргументы:**
- `self`

---

#### __init__ (`RouteEdge`)
**Аргументы:**
- `self`
- `edges`: list[Edge]

**Вызывает:** `_reverse`

---

#### start_point (`RouteEdge`)
**Аргументы:**
- `self`

**Возвращает:** `Vertex`

---

#### end_point (`RouteEdge`)
**Аргументы:**
- `self`

**Возвращает:** `Vertex`

---

#### move_along_edges_gen (`RouteEdge`)
**Аргументы:**
- `self`

**Возвращает:** `Edge`

---

#### move_along_edges_reversed_gen (`RouteEdge`)
**Аргументы:**
- `self`

**Возвращает:** `Edge`

---

#### cross_product
Векторное произведение координат

**Аргументы:**
- `o`: Tuple[float, float]
- `a`: Tuple[float, float]
- `b`: Tuple[float, float]

---

#### on_segment
Лежит ли точка C на отрезке AB

**Аргументы:**
- `a`
- `b`
- `c`

**Вызывает:** `max`, `min`

---

#### segments_intersect
Проверяет, пересекаются ли отрезки AB и CD

**Аргументы:**
- `a`: Tuple[float, float]
- `b`: Tuple[float, float]
- `c`: Tuple[float, float]
- `d`: Tuple[float, float]

**Возвращает:** `bool`

**Вызывает:** `max`, `min`

---

#### path_intersects_polygons
Проверяет, попадает ли путь на графе хотя бы в один полигон.

Args:
    path: объект RouteEdge, хранящий список рёбер пути на графе
    polygons: список полигонов в виде списков координат

Returns:
    bool: True если путь пересекает или находится внутри хотя бы одного полигона

**Аргументы:**
- `path`: RouteEdge
- `polygons`: Tuple[Tuple[Tuple[float, float]]] | list[list[list[float]]]

**Вызывает:** `move_along_edges_gen`, `zip`, `segments_intersect`, `list`

---

#### build_route_sim
Конвертирует наш dataclass Route (список сегментов)
в RouteSim (список уникальных точек по порядку).

**Аргументы:**
- `route_dc`: SimRoute

**Возвращает:** `Route`

**Вызывает:** `add`, `Route`, `set`, `append`, `Point`

---

#### build_route_by_road_net
**Аргументы:**
- `shovel_id`: int
- `unload_id`: int
- `road_net`: dict

**Возвращает:** `Route`

**Вызывает:** `create_from_geojson`, `key`, `RoadNetFactory`, `add`, `Route`, `set`, `append`, `search_path_dijkstra`, `Point`

---

#### build_route_edges_by_road_net
**Аргументы:**
- `from_object_id`: int
- `from_object_type`: ObjectType
- `to_object_id`: int
- `to_object_type`: ObjectType
- `road_net`: dict

**Возвращает:** `RouteEdge`

**Вызывает:** `create_from_geojson`, `key`, `RoadNetFactory`, `RouteEdge`, `search_path_dijkstra`

---

#### build_route_edges_by_road_net_from_position
**Аргументы:**
- `lon`: int | float
- `lat`: int | float
- `height`: int | None
- `edge_idx`: int
- `to_object_id`: int
- `to_object_type`: ObjectType
- `road_net`: dict

**Возвращает:** `RouteEdge`

**Вызывает:** `create_from_geojson`, `key`, `RoadNetFactory`, `RouteEdge`, `search_path_dijkstra`

---

#### build_route_edges_by_road_net_from_position_to_position
Строит кратчайший путь на графе от позиции до позиции

**Аргументы:**
- `lon`: float
- `lat`: float
- `height`: float | None
- `edge_idx`: int
- `end_lon`: float
- `end_lat`: float
- `end_height`: float | None
- `end_edge_idx`: int | None
- `road_net`: dict

**Возвращает:** `RouteEdge`

**Вызывает:** `RouteEdge`, `RoadNetFactory`, `create_from_geojson`, `search_path_dijkstra`

---

#### find_all_route_edges_by_road_net_from_position_to_position
Ищет все пути на графе от указанной позиции до указанной позиции

**Аргументы:**
- `lon`: float
- `lat`: float
- `height`: float | None
- `edge_idx`: int | None
- `end_lon`: float
- `end_lat`: float
- `end_height`: float | None
- `end_edge_idx`: int | None
- `road_net`: dict

**Вызывает:** `create_from_geojson`, `RoadNetFactory`, `search_all_paths`, `RouteEdge`, `sum`, `sort`

---

#### find_all_route_edges_by_road_net_from_position
Ищет все пути на графе от указанной позиции до указанного объекта

**Аргументы:**
- `lon`: float
- `lat`: float
- `height`: float | None
- `edge_idx`: int | None
- `to_object_id`: int
- `to_object_type`: ObjectType
- `road_net`: dict

**Вызывает:** `create_from_geojson`, `key`, `RoadNetFactory`, `search_all_paths`, `RouteEdge`, `sum`, `sort`

---

#### find_all_route_edges_by_road_net_from_object_to_object
Ищет все пути на графе от указанной позиции до указанного объекта

**Аргументы:**
- `from_object_id`: int
- `from_object_type`: ObjectType
- `to_object_id`: int
- `to_object_type`: ObjectType
- `road_net`: dict

**Вызывает:** `create_from_geojson`, `key`, `RoadNetFactory`, `search_all_paths`, `RouteEdge`, `sum`, `sort`

---

#### interpolate_position
**Аргументы:**
- `p1`: Point
- `p2`: Point
- `ratio`: float

**Возвращает:** `Point`

**Вызывает:** `Point`

---

#### haversine_km
**Аргументы:**
- `p1`: Point
- `p2`: Point

**Возвращает:** `float`

**Вызывает:** `radians`, `atan2`, `sqrt`, `sin`, `cos`

---

#### find_nearest_point
**Аргументы:**
- `point`: Point
- `point_list`: list[Point]

**Вызывает:** `haversine_km`, `min`

---

#### find_route_edges_around_restricted_zones_from_base_route
Поиск маршрута в объезд запрещённых зон (полигонов) на основе заданного маршрута

**Аргументы:**
- `base_route`: RouteEdge
- `restricted_zones`: Tuple[Tuple[Tuple[float, float]]] | list[list[list[float]]]
- `road_net`: dict

**Возвращает:** `RouteEdge | None`

**Вызывает:** `find_all_route_edges_by_road_net_from_position_to_position`, `path_intersects_polygons`

---

#### find_route_edges_around_restricted_zones_from_position_to_object
Поиск маршрута в объезд запрещённых зон (полигонов) от позиции до объекта

**Аргументы:**
- `lon`: float
- `lat`: float
- `edge_idx`: int | None
- `to_object_id`: int
- `to_object_type`: ObjectType
- `restricted_zones`: Tuple[Tuple[Tuple[float, float]]] | list[list[list[float]]]
- `road_net`: dict

**Возвращает:** `RouteEdge | None`

**Вызывает:** `find_all_route_edges_by_road_net_from_position`, `path_intersects_polygons`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\props.py`

### Импорты
- `from dataclasses import dataclass, field`
- `from datetime import datetime`
- `from typing import Literal`
- `from app.sim_engine.enums import ObjectType`

### Публичные функции

#### all (`IdleAreaStorage`)
**Аргументы:**
- `self`

---

#### lunch_areas (`IdleAreaStorage`)
**Аргументы:**
- `self`

---

#### shift_change_areas (`IdleAreaStorage`)
**Аргументы:**
- `self`

---

#### planned_idle_areas (`IdleAreaStorage`)
**Аргументы:**
- `self`

---

#### blast_waiting_areas (`IdleAreaStorage`)
**Аргументы:**
- `self`

---

#### is_finished (`ActualTrip`)
**Аргументы:**
- `self`

**Возвращает:** `bool`

---

#### to_telemetry (`ActualTrip`)
**Аргументы:**
- `self`

**Возвращает:** `dict`

**Вызывает:** `key`, `int`, `is_finished`, `isoformat`, `RuntimeError`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\__init__.py`

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\calculations\base.py`

### Импорты
- `import random`
- `from datetime import datetime`

### Публичные функции

#### __init__ (`BreakdownCalc`)
**Аргументы:**
- `self`
- `seeded_random`: random.Random

---

#### calculate_failure_time (`BreakdownCalc`)
Время не секунд семуляции, а секунд работы актора
самосвал: работа - движение груженым, движение порожним, разгрузка
экскаватор: работа - погрузка
ПР: во время разгрузки

**Аргументы:**
- `self`
- `**kwargs` (kwarg)

**Вызывает:** `expovariate`, `_calculate_rates`

---

#### calculate_repair_time (`BreakdownCalc`)
**Аргументы:**
- `self`
- `**kwargs` (kwarg)

**Вызывает:** `expovariate`, `_calculate_rates`

---

#### calculate_fuel_level_while_moving (`FuelCalc`)
**Аргументы:**
- `fuel_lvl`
- `sfc`
- `density`
- `p_engine`

---

#### calculate_fuel_level_while_idle (`FuelCalc`)
**Аргументы:**
- `fuel_lvl`
- `fuel_idle_lph`

---

#### calculate_lunch_times (`LunchCalc`)
Рассчитываем моменты начала и конца обеденных перерывов относительно времени симуляции

**Аргументы:**
- `sim_start_time`: datetime
- `lunch_times`: list[tuple[datetime, datetime]]

**Возвращает:** `list[tuple[int, int]]`

**Вызывает:** `append`, `total_seconds`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\calculations\shovel.py`

### Импорты
- `from typing import Tuple, Generator`
- `import numpy`
- `from app.sim_engine.core.coefficients import koef_vlazhnosti`
- `from app.sim_engine.core.constants import koef_soprotivleniya, density_by_material`
- `from app.sim_engine.core.props import ShovelProperties, TruckProperties`

### Публичные функции

#### calculate_cycle (`ShovelCalc`)
Расчёт времён всех стадий одного цикла работы Экскаватора
ждём самосвал, наполняем ковш, поворачиваемся, грузим и всё с самого начала

**Аргументы:**
- `cls`
- `props`: ShovelProperties
- `glubina_vrezki_m` = 0.3
- `dlina_drag_m` = 2.0
- `visota_podem_m` = 3.0
- `ugol_swing_rad` = np.pi / 2
- `ugol_dump_rad` = np.pi / 6
- `alpha_idle` = 0.3

**Возвращает:** `dict`

**Вызывает:** `get_koef`, `sum`, `idle`

---

#### calculate_load_cycles (`ShovelCalc`)
Рассчитывает суммарные показатели полного цикла погрузки самосвала.

Агрегирует данные всех циклов погрузки, сгенерированных методом
`_calculate_load_cycles_generator`, и возвращает общие итоги по времени,
весу и объему за всю операцию погрузки одного самосвала.

Parameters
----------
shovel_props : ShovelProperties
    Свойства экскаватора
truck_props : TruckProperties
    Свойства самосвала

Returns
-------
Tuple[int, float, float]
    Кортеж содержащий:
    - int: общее время погрузки в секундах
    - float: суммарный вес груза в тоннах
    - float: суммарный объем груза в м³

Notes
-----
- Метод использует генератор `_calculate_load_cycles_generator` для получения
  последовательности циклов погрузки
- Суммирование прекращается при достижении максимальной грузоподъемности самосвала
- Возвращаемые значения представляют полную загрузку одного самосвала

**Аргументы:**
- `cls`
- `shovel_props`: ShovelProperties
- `truck_props`: TruckProperties

**Возвращает:** `Tuple[int, float, float]`

**Вызывает:** `_calculate_load_cycles_generator`

---

#### calculate_load_cycles_cumulative_generator (`ShovelCalc`)
Генератор циклов погрузки с накопленными итогами.

Последовательно выдает данные каждого цикла погрузки с кумулятивными
(накопленными) значениями веса и объема. Позволяет отслеживать прогресс
заполнения самосвала после каждого цикла.

Parameters
----------
shovel_props : ShovelProperties
    Свойства экскаватора для расчета циклов погрузки
truck_props : TruckProperties
    Свойства самосвала, определяющие максимальную грузоподъемность

Yields
------
Tuple[int, float, float]
    Кортеж содержащий:
    - int: продолжительность ТЕКУЩЕГО ЦИКЛА в секундах
    - float: накопленный суммарный вес груза в тоннах (с учетом текущего цикла)
    - float: накопленный суммарный объем груза в м³ (с учетом текущего цикла)

Notes
-----
- В отличие от `_calculate_load_cycles_generator`, возвращает накопленные значения
- Полезен для анализа прогресса погрузки и построения графиков заполнения
- ВРЕМЯ ВОЗВРАЩАЕТСЯ ДЛЯ ОТДЕЛЬНОГО ЦИКЛА, а вес и объем - кумулятивные

**Аргументы:**
- `cls`
- `shovel_props`: ShovelProperties
- `truck_props`: TruckProperties

**Возвращает:** `Generator[Tuple[int, float, float], None, None]`

**Вызывает:** `_calculate_load_cycles_generator`

---

#### get_koef (`ShovelCalc`)
**Аргументы:**
- `props`

**Возвращает:** `dict`

**Вызывает:** `koef_vlazhnosti`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\calculations\truck.py`

### Импорты
- `from typing import Generator`
- `import numpy`
- `from roadnet.core import Edge`
- `from app.sim_engine.core.geometry import Point, interpolate_position, haversine_km, RouteEdge`

### Публичные функции

#### calculate_segment_motion (`TruckCalc`)
Расчет движения между двумя точками в маршруте

**Аргументы:**
- `cls`
- `p1`: Point
- `p2`: Point
- `initial_speed`: float
- `speed_limit`: float
- `acceleration`: float
- `time_step_sec`: int = 1

**Возвращает:** `Generator[tuple[float, Point], None, None]`

**Вызывает:** `interpolate_position`, `haversine_km`, `min`

---

#### calculate_motion (`TruckCalc`)
Расчет движения по маршруту состоящего из списка точек

**Аргументы:**
- `cls`
- `route`
- `props`
- `forward`

**Вызывает:** `list`, `calculate_segment_motion`, `range`, `len`, `reversed`

---

#### calculate_edge_motion (`TruckCalc`)
Расчет движения по ребру графа

**Аргументы:**
- `cls`
- `edge`: Edge
- `initial_speed`: float
- `speed_limit`: float
- `acceleration`: float
- `time_step_sec`: int = 1

**Возвращает:** `Generator[tuple[float, Point], None, None]`

**Вызывает:** `interpolate_position`, `min`

---

#### calculate_motion_by_edges (`TruckCalc`)
Расчет движения по списку ребер графа

**Аргументы:**
- `cls`
- `route`: RouteEdge
- `props`
- `forward`
- `is_loaded`

**Вызывает:** `generator_path`, `calculate_edge_motion`

---

#### calculate_time_motion_by_edges (`TruckCalc`)
**Аргументы:**
- `cls`
- `route`: RouteEdge
- `props`
- `forward`

**Вызывает:** `sum`, `calculate_motion_by_edges`

---

#### time_empty (`TruckCalc`)
Время движения порожним к экскаватору (сек)
Формула: t = S / v * 3600 / driver_skill,
где S — длина пути (км), v — скорость порожним (км/ч)

**Аргументы:**
- `self`

**Возвращает:** `int`

**Вызывает:** `int`, `ceil`

---

#### time_loaded (`TruckCalc`)
Время движения гружённым к разгрузке (сек)
Формула: t = S / v * 3600 / driver_skill,
где S — длина пути (км), v — скорость гружённым (км/ч)

**Аргументы:**
- `self`

**Возвращает:** `int`

**Вызывает:** `int`, `ceil`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\calculations\unload.py`

### Импорты
- `from app.sim_engine.core.constants import koef_soprotivleniya, unloading_speed, density_by_material`
- `from app.sim_engine.core.props import TruckProperties, UnlProperties`

### Публичные функции

#### unload_calculation (`UnloadCalc`)
1. t_drive — подъезд (сек), фиксированно 30 сек
2. t_stop — остановка и установка (15 сек)
3. t_lift — подъем кузова (20 сек)
4. t_dump — высыпание груза:
    t_dump = V / (speed * K_угол * K_мат * K_темп)
5. t_down — опускание кузова (15 сек)
6. t_leave — уход (30 сек)
потом исправлю CHANGE
длина участка для маневра
средняя скорость маневра
замедление

**Аргументы:**
- `cls`
- `props`: UnlProperties
- `truck_volume`

**Вызывает:** `max`, `dict`

---

#### unload_calculation_by_norm (`UnloadCalc`)
1. t_drive — подъезд (сек), фиксированно 30 сек
2. t_stop — остановка и установка (15 сек)
3. t_lift — подъем кузова (20 сек)
4. t_dump — высыпание груза:
    t_dump = V / (speed * K_угол * K_мат * K_темп)
5. t_down — опускание кузова (15 сек)
6. t_leave — уход (30 сек)
потом исправлю CHANGE
длина участка для маневра
средняя скорость маневра
замедление

**Аргументы:**
- `cls`
- `unload_props`: UnlProperties
- `truck_props`: TruckProperties

**Вызывает:** `max`, `dict`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\calculations\__init__.py`

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\planner\entities.py`

### Импорты
- `from dataclasses import dataclass`
- `from typing import Dict, Tuple, Optional, List`

### Публичные функции

#### truck_ids (`InputPlanningData`)
**Аргументы:**
- `self`

**Возвращает:** `List[int]`

**Вызывает:** `sorted`, `keys`

---

#### shovel_ids (`InputPlanningData`)
**Аргументы:**
- `self`

**Возвращает:** `List[int]`

**Вызывает:** `sorted`, `keys`

---

#### unload_ids (`InputPlanningData`)
**Аргументы:**
- `self`

**Возвращает:** `List[int]`

**Вызывает:** `sorted`, `keys`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\planner\manage.py`

### Импорты
- `import logging`
- `from collections import defaultdict`
- `from app.sim_engine.core.calculations.shovel import ShovelCalc`
- `from app.sim_engine.core.calculations.truck import TruckCalc`
- `from app.sim_engine.core.calculations.unload import UnloadCalc`
- `from app.sim_engine.core.geometry import build_route_edges_by_road_net_from_position, build_route_edges_by_road_net`
- `from app.sim_engine.core.planner.entities import InputPlanningData`
- `from app.sim_engine.core.planner.solvers.cp import CPSolver`
- `from app.sim_engine.core.planner.solvers.milp import MILPSolver`
- `from app.sim_engine.core.props import SimData, PlannedTrip`
- `from app.sim_engine.enums import ObjectType`

### Публичные функции

#### __init__ (`Planner`)
**Аргументы:**
- `self`
- `solver`: str = None
- `msg`: bool = False
- `workers`: int = 4
- `time_limit`: int = 60

---

#### get_planning_data (`Planner`)
Метод набивающий матрицу данных

**Аргументы:**
- `simdata`: SimData

**Возвращает:** `InputPlanningData`

**Вызывает:** `values`, `int`, `build_route_edges_by_road_net_from_position`, `unload_calculation_by_norm`, `len`, `build_route_edges_by_road_net`, `calculate_load_cycles`, `dict`, `calculate_time_motion_by_edges`, `InputPlanningData`

---

#### run_with_exclude (`Planner`)
**Аргументы:**
- `self`
- `sim_data`: SimData
- `exclude_objects`: dict[str, list[int]]

**Возвращает:** `dict`

**Вызывает:** `defaultdict`, `int`, `run`, `PlannedTrip`, `append`, `pop`, `info`, `total_seconds`

---

#### run (`Planner`)
**Аргументы:**
- `self`
- `simdata`: SimData

**Вызывает:** `get_planning_data`, `run`, `_init_solver`, `info`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\planner\planning_matrix.py`

### Импорты
- `from app.sim_engine.core.calculations.shovel import ShovelCalc`
- `from app.sim_engine.core.calculations.truck import TruckCalc`
- `from app.sim_engine.core.calculations.unload import UnloadCalc`
- `from app.sim_engine.core.geometry import build_route_edges_by_road_net_from_position, build_route_edges_by_road_net`
- `from app.sim_engine.core.planner.entities import InputPlanningData`
- `from app.sim_engine.core.props import SimData`
- `from app.sim_engine.enums import ObjectType`

### Публичные функции

#### get_planning_data
Метод набивающий матрицу данных

**Аргументы:**
- `simdata`: SimData

**Возвращает:** `InputPlanningData`

**Вызывает:** `values`, `int`, `build_route_edges_by_road_net_from_position`, `unload_calculation_by_norm`, `len`, `build_route_edges_by_road_net`, `calculate_load_cycles`, `dict`, `calculate_time_motion_by_edges`, `InputPlanningData`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\planner\__init__.py`

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\planner\solvers\cp.py`

### Импорты
- `import logging`
- `from math import floor`
- `from ortools.sat.python import cp_model`
- `from app.sim_engine.core.planner.entities import InputPlanningData`

### Публичные функции

#### compute_Kmax_i (`CPSolver`)
Грубая верхняя граница числа рейсов для самосвала i

**Аргументы:**
- `inst`: InputPlanningData
- `i`: int

**Возвращает:** `int`

**Вызывает:** `floor`, `max`, `min`, `keys`

---

#### build_cp_model (`CPSolver`)
**Аргументы:**
- `cls`
- `inst`: InputPlanningData
- `use_individual_kmax`: bool = True

**Вызывает:** `int`, `CpModel`, `OnlyEnforceIf`, `sum`, `Add`, `values`, `range`, `max`, `dict`, `round`, `compute_Kmax_i`, `NewBoolVar`, `append`, `AddNoOverlap`, `Maximize`, `Not`, `NewOptionalIntervalVar`, `AddBoolOr`, `NewIntVar`

---

#### run (`CPSolver`)
Решение CP‑SAT и извлечение расписания в прежнем формате.

**Аргументы:**
- `cls`
- `inst`: InputPlanningData

**Вызывает:** `build_cp_model`, `int`, `float`, `range`, `BooleanValue`, `Solve`, `ObjectiveValue`, `CpSolver`, `append`, `Value`, `get`, `info`, `sort`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\planner\solvers\greedy.py`

### Импорты
- `import logging`
- `from copy import deepcopy`
- `from datetime import datetime`
- `from typing import List`
- `from app.sim_engine.core.planner.entities import InputPlanningData`
- `from app.sim_engine.core.planner.planning_matrix import get_planning_data`
- `from app.sim_engine.core.props import PlannedTrip`
- `from app.sim_engine.core.simulations.truck import Truck`
- `from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver`
- `from app.sim_engine.enums import ObjectType`
- `from app.sim_engine.states import TruckState`

### Публичные функции

#### __init__ (`GreedySolver`)
**Аргументы:**
- `self`
- `planning_data`: InputPlanningData = None

**Вызывает:** `deepcopy`, `env`

---

#### planning_data (`GreedySolver`)
**Аргументы:**
- `self`

**Вызывает:** `get_planning_data`

---

#### rebuild_planning_data (`GreedySolver`)
**Аргументы:**
- `self`
- `start_time` = None
- `end_time` = None
- `excluded_object`: tuple[int, ObjectType] = None
- `included_object`: tuple[int, ObjectType] = None

**Вызывает:** `debug`, `_update_trucks_position`, `_included_object`, `_reset_cycle`, `_excluded_object`, `items`

---

#### rebuild_planning_data_cascade (`GreedySolver`)
**Аргументы:**
- `self`
- `start_time`: datetime | None = None
- `end_time`: datetime | None = None
- `excluded_objects`: List[tuple[int, ObjectType]] | None = None
- `included_objects`: List[tuple[int, ObjectType]] | None = None

**Вызывает:** `debug`, `_update_trucks_position`, `_included_objects`, `_reset_cycle`, `_excluded_objects`, `items`

---

#### find_trucks_to_shovel (`GreedySolver`)
**Аргументы:**
- `shovel`

**Вызывает:** `append`, `values`

---

#### choose_next_trip (`GreedySolver`)
Выбирает лучшую связку (shovel, unload) для данного самосвала

**Аргументы:**
- `self`
- `truck`
- `now`: int

**Вызывает:** `find_trucks_to_shovel`, `debug`, `values`, `len`, `append`

---

#### assign_trip (`GreedySolver`)
Формирует новый PlannedTrip и обновляет маршруты для самосвала

**Аргументы:**
- `self`
- `truck`: Truck
- `now`: int

**Возвращает:** `PlannedTrip | None`

**Вызывает:** `choose_next_trip`, `PlannedTrip`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\planner\solvers\milp.py`

### Импорты
- `import logging`
- `from math import floor`
- `from typing import Dict, List, Tuple`
- `from pulp import LpProblem, LpMaximize, LpVariable, LpBinary, LpInteger, lpSum, LpStatus, value, PULP_CBC_CMD, HiGHS_CMD`
- `from app.sim_engine.core.planner.entities import InputPlanningData`
- `from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver`

### Публичные функции

#### compute_Kmax_i (`MILPSolver`)
Грубая верхняя граница числа рейсов для самосвала i

**Аргументы:**
- `inst`: InputPlanningData
- `i`: int

**Возвращает:** `int`

**Вызывает:** `floor`, `max`, `min`, `keys`

---

#### default_Kmax (`MILPSolver`)
Если Kmax не задан, вычислить его для каждого самосвала

**Аргументы:**
- `cls`
- `inst`: InputPlanningData

**Возвращает:** `Dict[int, int]`

**Вызывает:** `compute_Kmax_i`

---

#### a_use (`MILPSolver`)
**Аргументы:**
- `i`
- `k`
- `j`

**Вызывает:** `lpSum`

---

#### b_use (`MILPSolver`)
**Аргументы:**
- `i`
- `k`
- `z`

**Вызывает:** `lpSum`

---

#### build_model (`MILPSolver`)
Собираем все ограничения и условия поиска решения

**Аргументы:**
- `cls`
- `inst`: InputPlanningData
- `shovel_queue`: bool = True

**Вызывает:** `lpSum`

---

#### run (`MILPSolver`)
Решить модель и получить расписание
        

**Аргументы:**
- `cls`
- `inst`: InputPlanningData

**Вызывает:** `int`, `ValueError`, `value`, `PULP_CBC_CMD`, `solve`, `range`, `HiGHS_CMD`, `round`, `append`, `build_model`, `info`, `sim_conf`, `sort`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\planner\solvers\__init__.py`

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\simulations\base.py`

### Импорты
- `from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver`

### Публичные функции

#### __init__ (`TelemetryEmitter`)
**Аргументы:**
- `self`
- `tick`
- `data_callback`

**Вызывает:** `process`, `env`, `run`, `writer`

---

#### run (`TelemetryEmitter`)
**Аргументы:**
- `self`

**Вызывает:** `data_callback`, `writerow`, `timeout`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\simulations\entities.py`

### Импорты
- `from dataclasses import dataclass`
- `from app.sim_engine.core.simulations.quarry import Quarry`
- `from app.sim_engine.core.simulations.shovel import Shovel`
- `from app.sim_engine.core.simulations.truck import Truck`
- `from app.sim_engine.core.simulations.unload import Unload`

### Публичные функции

#### get_truck_by_id (`SimContext`)
**Аргументы:**
- `self`
- `truck_id`: int

---

#### get_shovel_by_id (`SimContext`)
**Аргументы:**
- `self`
- `shovel_id`: int

---

#### get_unload_by_id (`SimContext`)
**Аргументы:**
- `self`
- `unload_id`: int

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\simulations\fuel_station.py`

### Импорты
- `import copy`
- `from datetime import timedelta`
- `import simpy`
- `from app.sim_engine.core.props import FuelStationProperties`
- `from app.sim_engine.core.simulations.behaviors.base import BaseTickBehavior`
- `from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver`
- `from app.sim_engine.enums import ObjectType`
- `from app.sim_engine.events import FuelStationEvent, EventType`
- `from app.sim_engine.states import FuelStationState, TruckState`

### Публичные функции

#### __init__ (`FuelStation`)
**Аргументы:**
- `self`
- `properties`: FuelStationProperties
- `unit_id`
- `name`
- `initial_position`
- `tick` = 1

**Вызывает:** `BaseTickBehavior`, `env`, `writer`, `Resource`

---

#### current_time (`FuelStation`)
**Аргументы:**
- `self`

**Вызывает:** `timestamp`, `timedelta`

---

#### refuelling (`FuelStation`)
**Аргументы:**
- `self`
- `truck`

**Вызывает:** `remove`, `push_event`, `int`, `timeout`, `request`, `range`, `append`, `copy`

---

#### main_tic_process (`FuelStation`)
**Аргументы:**
- `self`

---

#### push_event (`FuelStation`)
**Аргументы:**
- `self`
- `event_type`: EventType
- `truck`

**Вызывает:** `FuelStationEvent`, `ru`, `push_event`, `code`

---

#### telemetry_process (`FuelStation`)
**Аргументы:**
- `self`

**Вызывает:** `writerow`, `ru`, `key`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\simulations\quarry.py`

### Импорты
- `import logging`
- `import random`
- `from copy import deepcopy`
- `from datetime import timedelta, datetime`
- `from typing import Tuple`
- `from app.sim_engine.core.planner.manage import Planner`
- `from app.sim_engine.core.props import ShiftChangeArea, SimData, Blasting, IdleArea`
- `from app.sim_engine.core.simulations.behaviors.blasting import QuarryBlastingWatcher`
- `from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver`
- `from app.sim_engine.enums import ObjectType`
- `from app.sim_engine.events import Event, EventType`
- `from app.sim_engine.states import TruckState`

### Публичные функции

#### __init__ (`Quarry`)
**Аргументы:**
- `self`

**Вызывает:** `trip_service`, `solver`, `env`, `writer`, `QuarryBlastingWatcher`, `sim_conf`

---

#### current_time (`Quarry`)
**Аргументы:**
- `self`

**Возвращает:** `datetime`

**Вызывает:** `timedelta`

---

#### current_timestamp (`Quarry`)
**Аргументы:**
- `self`

**Вызывает:** `timestamp`

---

#### prepare_seeded_random (`Quarry`)
Generate seed if it doesn't exist in `self.sim_data.seed` and init `random.Random` instance with it

Needs to be called when we already have `self.sim_data`

**Аргументы:**
- `self`

**Возвращает:** `None`

**Вызывает:** `getrandbits`, `Random`

---

#### update_planned_trips (`Quarry`)
**Аргументы:**
- `self`

**Вызывает:** `get`, `interrupt`, `items`

---

#### update_trucks_position (`Quarry`)
**Аргументы:**
- `self`
- `sim_data`

**Вызывает:** `items`

---

#### rebuild_plan_by_add_exclude (`Quarry`)
**Аргументы:**
- `self`
- `start_time`: datetime = None
- `end_time`: datetime = None
- `exclude_object_id`: int = None
- `exclude_object_type`: ObjectType = None

**Возвращает:** `None`

**Вызывает:** `deepcopy`, `Planner`, `run_with_exclude`, `update_trucks_position`, `update_planned_trips`, `append`

---

#### rebuild_plan_by_del_exclude (`Quarry`)
**Аргументы:**
- `self`
- `start_time`: datetime = None
- `end_time`: datetime = None
- `exclude_object_id`: int = None
- `exclude_object_type`: ObjectType = None

**Возвращает:** `None`

**Вызывает:** `remove`, `deepcopy`, `run_with_exclude`, `Planner`, `update_trucks_position`, `update_planned_trips`

---

#### get_summary (`Quarry`)
**Аргументы:**
- `self`
- `end_time`: datetime

**Возвращает:** `dict`

**Вызывает:** `get_summary`

---

#### push_event (`Quarry`)
**Аргументы:**
- `self`
- `event_type`: EventType
- `*args` (vararg)
- `**kwargs` (kwarg)

**Вызывает:** `ru`, `key`, `push_event`, `strftime`, `check_trucks_state`, `Event`, `rebuild_planning_data_cascade`, `get`, `code`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\simulations\shovel.py`

### Импорты
- `from datetime import timedelta`
- `import simpy`
- `from app.sim_engine.core.calculations.shovel import ShovelCalc`
- `from app.sim_engine.core.constants import density_by_material`
- `from app.sim_engine.core.geometry import Point`
- `from app.sim_engine.core.props import ShovelProperties`
- `from app.sim_engine.core.simulations.behaviors.base import BreakdownBehavior, BaseTickBehavior, PlannedIdleBehavior`
- `from app.sim_engine.core.simulations.behaviors.blasting import ShovelBlastingWatcher`
- `from app.sim_engine.core.simulations.quarry import Quarry`
- `from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver`
- `from app.sim_engine.enums import ObjectType`
- `from app.sim_engine.events import Event, EventType`
- `from app.sim_engine.states import ExcState, TruckState`

### Публичные функции

#### __init__ (`Shovel`)
**Аргументы:**
- `self`
- `unit_id`
- `name`
- `position`: Point
- `quarry`: Quarry
- `properties`: ShovelProperties
- `tick` = 1

**Вызывает:** `solver`, `ShovelBlastingWatcher`, `env`, `PlannedIdleBehavior`, `writer`, `BaseTickBehavior`, `get`, `BreakdownBehavior`, `sim_conf`, `Resource`

---

#### current_time (`Shovel`)
**Аргументы:**
- `self`

**Вызывает:** `timedelta`

---

#### current_timestamp (`Shovel`)
**Аргументы:**
- `self`

**Вызывает:** `timestamp`

---

#### load_truck (`Shovel`)
**Аргументы:**
- `self`
- `truck`

**Вызывает:** `remove`, `timeout`, `request`, `calculate_load_cycles_cumulative_generator`, `release`, `append`

---

#### main_tic_process (`Shovel`)
**Аргументы:**
- `self`

---

#### push_event (`Shovel`)
**Аргументы:**
- `self`
- `event_type`: EventType
- `write_event`: bool = True

**Вызывает:** `ru`, `push_event`, `rebuild_plan_by_add_exclude`, `Event`, `rebuild_planning_data`, `rebuild_plan_by_del_exclude`, `code`

---

#### telemetry_process (`Shovel`)
**Аргументы:**
- `self`

**Вызывает:** `writerow`, `ru`, `key`, `round`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\simulations\truck.py`

### Импорты
- `from datetime import timedelta`
- `from typing import List, Callable, Optional, Set`
- `import simpy`
- `from app.sim_engine.core.calculations.truck import TruckCalc`
- `from app.sim_engine.core.geometry import Point, Route, haversine_km, RouteEdge, build_route_edges_by_road_net, build_route_edges_by_road_net_from_position, build_route_edges_by_road_net_from_position_to_position, path_intersects_polygons, find_route_edges_around_restricted_zones_from_base_route`
- `from app.sim_engine.core.props import TruckProperties, PlannedTrip, TripData`
- `from app.sim_engine.core.simulations.behaviors.base import BaseTickBehavior, BreakdownBehavior, FuelBehavior, LunchBehavior, PlannedIdleBehavior`
- `from app.sim_engine.core.simulations.behaviors.blasting import TruckBlastingWatcher`
- `from app.sim_engine.core.simulations.fuel_station import FuelStation`
- `from app.sim_engine.core.simulations.quarry import Quarry`
- `from app.sim_engine.core.simulations.shovel import Shovel`
- `from app.sim_engine.core.simulations.unload import Unload`
- `from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver`
- `from app.sim_engine.enums import ObjectType, IdleAreaType`
- `from app.sim_engine.events import EventType, Event`
- `from app.sim_engine.states import TruckState`

### Публичные функции

#### __init__ (`Truck`)
**Аргументы:**
- `self`
- `unit_id`
- `name`
- `initial_position`: Point
- `route`: Route | None
- `route_edge`: RouteEdge | None
- `start_route`: RouteEdge | None
- `planned_trips`: list[PlannedTrip]
- `quarry`: Quarry
- `shovel`: Shovel | None
- `unload`: Unload | None
- `properties`: TruckProperties
- `fuel_stations`: list[FuelStation]
- `tick` = 1

**Вызывает:** `TruckBlastingWatcher`, `trip_service`, `key`, `solver`, `idle_area_service`, `process`, `env`, `run`, `FuelBehavior`, `writer`, `BaseTickBehavior`, `LunchBehavior`, `get`, `BreakdownBehavior`, `sim_conf`, `PlannedIdleBehavior`

---

#### nearest_fuel_station (`Truck`)
**Аргументы:**
- `self`

**Возвращает:** `FuelStation`

**Вызывает:** `len`, `haversine_km`, `min`

---

#### current_time (`Truck`)
**Аргументы:**
- `self`

**Вызывает:** `timedelta`

---

#### current_timestamp (`Truck`)
**Аргументы:**
- `self`

**Вызывает:** `timestamp`

---

#### travel_segment (`Truck`)
**Аргументы:**
- `self`
- `p1`: Point
- `p2`: Point
- `speed_limit`
- `acceleration`

**Вызывает:** `timeout`, `calculate_segment_motion`

---

#### broken_action (`Truck`)
**Аргументы:**
- `self`

**Вызывает:** `timeout`

---

#### refuel_action (`Truck`)
Логика заправок

**Аргументы:**
- `self`

**Вызывает:** `process`, `moving`, `build_route_edges_by_road_net_from_position`, `refuelling`

---

#### lunch_action (`Truck`)
Логика обеденных перерывов 

**Аргументы:**
- `self`

**Вызывает:** `timeout`, `move_to_area`

---

#### planned_idle_action (`Truck`)
Логика плановых простоев

**Аргументы:**
- `self`

**Вызывает:** `timeout`, `move_to_area`

---

#### wait_blasting (`Truck`)
Логика ожидания изменений во взрывных работах

**Аргументы:**
- `self`
- `current_zones`: Set[int]

**Вызывает:** `timeout`

---

#### blasting_action (`Truck`)
Логика поведения при активных взрывных работах

**Аргументы:**
- `self`

**Вызывает:** `wait_blasting`, `find_route_edges_around_restricted_zones_from_base_route`, `moving`, `path_intersects_polygons`, `build_route_edges_by_road_net_from_position_to_position`, `move_to_area`

---

#### move_to_area (`Truck`)
Логика поиска ближайшей площадки выбранного типа и следование на эту площадку

**Аргументы:**
- `self`
- `area_type`: IdleAreaType
- `actions`: Optional[List[Callable]] = None

**Вызывает:** `wait_blasting`, `get_areas`, `moving`, `path_intersects_polygons`, `find_nearest`

---

#### moving (`Truck`)
Метод, производящий перемещение самосвала по заданному маршруту с возможностью отклонения от маршрута при необходимости

**Аргументы:**
- `self`
- `route`: RouteEdge
- `forward`: bool
- `actions`: Optional[List[Callable]] = None

**Вызывает:** `timeout`, `build_route_edges_by_road_net_from_position_to_position`, `calculate_motion_by_edges`, `action`

---

#### set_route (`Truck`)
**Аргументы:**
- `self`

**Возвращает:** `None`

**Вызывает:** `build_route_edges_by_road_net`, `pop`

---

#### set_start_route (`Truck`)
**Аргументы:**
- `self`

**Возвращает:** `None`

**Вызывает:** `build_route_edges_by_road_net`, `build_route_edges_by_road_net_from_position`

---

#### run (`Truck`)
**Аргументы:**
- `self`

**Вызывает:** `remove`, `set_shift_change_area`, `process`, `timeout`, `set_start_route`, `moving`, `set_route`, `load_truck`, `current_trip_data`, `unload_truck`, `begin`, `cancel`, `len`, `append`, `assign_trip`, `finish`

---

#### push_event (`Truck`)
**Аргументы:**
- `self`
- `event_type`: EventType
- `write_event`: bool = True

**Возвращает:** `None`

**Вызывает:** `ru`, `push_event`, `rebuild_plan_by_add_exclude`, `Event`, `rebuild_planning_data`, `rebuild_plan_by_del_exclude`, `code`

---

#### telemetry_process (`Truck`)
**Аргументы:**
- `self`

**Вызывает:** `writerow`, `ru`, `key`, `round`

---

#### current_trip_data (`Truck`)
**Аргументы:**
- `self`

**Возвращает:** `TripData`

**Вызывает:** `TripData`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\simulations\unload.py`

### Импорты
- `from datetime import timedelta`
- `import simpy`
- `from app.sim_engine.core.calculations.unload import UnloadCalc`
- `from app.sim_engine.core.simulations.behaviors.base import BaseTickBehavior, BreakdownBehavior`
- `from app.sim_engine.core.simulations.behaviors.blasting import UnloadBlastingWatcher`
- `from app.sim_engine.core.simulations.quarry import Quarry`
- `from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver`
- `from app.sim_engine.enums import ObjectType`
- `from app.sim_engine.events import Event, EventType`
- `from app.sim_engine.states import UnloadState, TruckState`

### Публичные функции

#### __init__ (`Unload`)
**Аргументы:**
- `self`
- `properties`
- `unit_id`
- `name`
- `quarry`: Quarry
- `tick` = 1

**Вызывает:** `solver`, `UnloadBlastingWatcher`, `env`, `writer`, `BaseTickBehavior`, `BreakdownBehavior`, `sim_conf`, `Resource`

---

#### current_time (`Unload`)
**Аргументы:**
- `self`

**Вызывает:** `timedelta`

---

#### current_timestamp (`Unload`)
**Аргументы:**
- `self`

**Вызывает:** `timestamp`

---

#### unload_truck (`Unload`)
**Аргументы:**
- `self`
- `truck`

**Вызывает:** `remove`, `unload_calculation`, `int`, `timeout`, `request`, `range`, `append`

---

#### push_event (`Unload`)
**Аргументы:**
- `self`
- `event_type`: EventType
- `write_event`: bool = True

**Вызывает:** `ru`, `push_event`, `rebuild_plan_by_add_exclude`, `Event`, `rebuild_planning_data`, `rebuild_plan_by_del_exclude`, `code`

---

#### main_tic_process (`Unload`)
**Аргументы:**
- `self`

---

#### telemetry_process (`Unload`)
**Аргументы:**
- `self`

**Вызывает:** `writerow`, `ru`, `key`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\simulations\__init__.py`

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\simulations\behaviors\base.py`

### Импорты
- `from abc import ABC`
- `from typing import List, Any`
- `from app.sim_engine.core.calculations.base import BreakdownCalc, FuelCalc, LunchCalc`
- `from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver`
- `from app.sim_engine.enums import ObjectType`
- `from app.sim_engine.events import EventType`
- `from app.sim_engine.states import TruckState, ExcState`

### Публичные функции

#### __init__ (`BaseBehavior`)
**Аргументы:**
- `self`
- `target`: Any
- `props`: Any = None

**Вызывает:** `process`, `env`, `run`

---

#### run (`BaseBehavior`)
Основной цикл выполнения поведения

**Аргументы:**
- `self`

**Вызывает:** `timeout`

---

#### __init__ (`BaseTickBehavior`)
**Аргументы:**
- `self`
- `target`

**Вызывает:** `process`, `env`, `run`

---

#### run (`BaseTickBehavior`)
**Аргументы:**
- `self`

**Вызывает:** `main_tic_process`, `timeout`, `hasattr`, `telemetry_process`

---

#### __init__ (`BreakdownBehavior`)
**Аргументы:**
- `self`
- `target`
- `props`

**Вызывает:** `super`, `__init__`, `BreakdownCalc`

---

#### run (`BreakdownBehavior`)
**Аргументы:**
- `self`

**Вызывает:** `push_event`, `int`, `timeout`, `calculate_repair_time`, `calculate_failure_time`

---

#### __init__ (`FuelBehavior`)
**Аргументы:**
- `self`
- `target`
- `props`

**Вызывает:** `super`, `__init__`, `FuelCalc`

---

#### run (`FuelBehavior`)
**Аргументы:**
- `self`

**Вызывает:** `calculate_fuel_level_while_idle`, `timeout`, `calculate_fuel_level_while_moving`

---

#### __init__ (`LunchBehavior`)
**Аргументы:**
- `self`
- `target`

**Вызывает:** `super`, `__init__`, `LunchCalc`

---

#### run (`LunchBehavior`)
**Аргументы:**
- `self`

**Вызывает:** `timeout`, `push_event`, `pop`, `calculate_lunch_times`

---

#### __init__ (`PlannedIdleBehavior`)
**Аргументы:**
- `self`
- `target`
- `object_type`: ObjectType

**Вызывает:** `super`, `__init__`

---

#### run (`PlannedIdleBehavior`)
**Аргументы:**
- `self`

**Вызывает:** `_should_start_planned_idle`, `push_event`, `_calculate_idles_times`, `timeout`, `pop`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\simulations\behaviors\blasting.py`

### Импорты
- `from copy import deepcopy`
- `from datetime import timedelta`
- `from typing import List`
- `from app.sim_engine.core.geometry import path_intersects_polygons, find_all_route_edges_by_road_net_from_object_to_object`
- `from app.sim_engine.core.props import Blasting`
- `from app.sim_engine.core.simulations.behaviors.base import BaseBehavior`
- `from app.sim_engine.enums import ObjectType`
- `from app.sim_engine.events import EventType`
- `from app.sim_engine.states import TruckState`

### Публичные функции

#### __init__ (`QuarryBlastingWatcher`)
**Аргументы:**
- `self`
- `target`

**Вызывает:** `super`, `__init__`

---

#### generate_blasting_list (`QuarryBlastingWatcher`)
Создаёт список взрывных работ временами относительно времени симуляции

**Аргументы:**
- `self`

**Возвращает:** `list[Blasting]`

**Вызывает:** `deepcopy`, `total_seconds`

---

#### check_trucks_state (`QuarryBlastingWatcher`)
Проверяет состояние самосвалов карьера.
Если попал в состояние ожидания проведения взрывных работ, перепланируем рейсы, исключив этот самосвал.
Если вышел из состояния ожидания проведения взрывных работ, перепланируем рейсы, включив этот самосвал.

**Аргументы:**
- `self`

**Вызывает:** `remove`, `append`, `values`

---

#### run (`QuarryBlastingWatcher`)
**Аргументы:**
- `self`

**Вызывает:** `push_event`, `set`, `timeout`, `dict`, `keys`, `pop`, `generate_blasting_list`, `timedelta`

---

#### __init__ (`TruckBlastingWatcher`)
**Аргументы:**
- `self`
- `target`

**Вызывает:** `super`, `__init__`

---

#### run (`TruckBlastingWatcher`)
**Аргументы:**
- `self`

**Вызывает:** `timeout`, `push_event`

---

#### __init__ (`ShovelBlastingWatcher`)
**Аргументы:**
- `self`
- `target`

**Вызывает:** `super`, `__init__`

---

#### wait_blasting_changing (`ShovelBlastingWatcher`)
**Аргументы:**
- `self`

**Вызывает:** `timeout`

---

#### run (`ShovelBlastingWatcher`)
**Аргументы:**
- `self`

**Вызывает:** `values`, `push_event`, `timeout`, `path_intersects_polygons`, `wait_blasting_changing`, `find_all_route_edges_by_road_net_from_object_to_object`

---

#### __init__ (`UnloadBlastingWatcher`)
**Аргументы:**
- `self`
- `target`

**Вызывает:** `super`, `__init__`

---

#### wait_blasting_changing (`UnloadBlastingWatcher`)
**Аргументы:**
- `self`

**Вызывает:** `timeout`

---

#### run (`UnloadBlastingWatcher`)
**Аргументы:**
- `self`

**Вызывает:** `values`, `push_event`, `timeout`, `path_intersects_polygons`, `wait_blasting_changing`, `find_all_route_edges_by_road_net_from_object_to_object`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\simulations\behaviors\__init__.py`

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\simulations\utils\dependency_resolver.py`

### Импорты
- `from typing import TYPE_CHECKING, Any`
- `from app.sim_engine.core.simulations.utils.service_locator import ServiceLocator`
- `from app.sim_engine.writer import IWriter`
- `from app.sim_engine.core.environment import QSimEnvironment`
- `from app.sim_engine.core.planner.solvers.greedy import GreedySolver`
- `from app.sim_engine.core.simulations.utils.trip_service import TripService`
- `from app.sim_engine.core.simulations.utils.idle_area_service import IdleAreaService`

### Публичные функции

#### sim_conf (`DependencyResolver`)
**Аргументы:**
- `cls`

**Возвращает:** `dict`

**Вызывает:** `__resolve`

---

#### writer (`DependencyResolver`)
**Аргументы:**
- `cls`

**Возвращает:** `'IWriter'`

**Вызывает:** `__resolve`

---

#### solver (`DependencyResolver`)
**Аргументы:**
- `cls`

**Возвращает:** `'GreedySolver'`

**Вызывает:** `__resolve`

---

#### trip_service (`DependencyResolver`)
**Аргументы:**
- `cls`

**Возвращает:** `'TripService'`

**Вызывает:** `__resolve`

---

#### idle_area_service (`DependencyResolver`)
**Аргументы:**
- `cls`

**Возвращает:** `'IdleAreaService'`

**Вызывает:** `__resolve`

---

#### env (`DependencyResolver`)
**Аргументы:**
- `cls`

**Возвращает:** `'QSimEnvironment'`

**Вызывает:** `__resolve`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\simulations\utils\helpers.py`

### Импорты
- `from datetime import datetime, timedelta`
- `from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver`

### Публичные функции

#### sim_current_timestamp
**Возвращает:** `float`

**Вызывает:** `timestamp`, `sim_current_time`

---

#### sim_current_time
**Возвращает:** `datetime`

**Вызывает:** `env`, `timedelta`

---

#### sim_end_time
**Возвращает:** `datetime`

**Вызывает:** `env`

---

#### sim_start_time
**Возвращает:** `datetime`

**Вызывает:** `env`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\simulations\utils\idle_area_service.py`

### Импорты
- `from typing import Tuple`
- `from app.sim_engine.core.geometry import RouteEdge, find_route_edges_around_restricted_zones_from_position_to_object`
- `from app.sim_engine.core.props import IdleAreaStorage, IdleArea`
- `from app.sim_engine.enums import ObjectType, IdleAreaType`

### Публичные функции

#### __init__ (`IdleAreaService`)
**Аргументы:**
- `self`
- `idle_area_storage`: IdleAreaStorage

---

#### get_areas (`IdleAreaService`)
Сбор площадок соответствующего типа

**Аргументы:**
- `self`
- `area_type`: IdleAreaType | None = None

**Возвращает:** `list[IdleArea]`

---

#### find_nearest (`IdleAreaService`)
Поиск ближайшей площадки, соответствующей указанному типу.
Поиск происходит по графу относительно переданной позиции.
При наличии запрещённых зон для проезда поиск будет вестись с учётом этих зон.

При отсутствии проезда к площадке из-за запретных зон будет выбрана другая ближайшая площадка при наличии
к ней проезда.

Возвращает кортеж: площадка, маршрут на графе к площадке

**Аргументы:**
- `self`
- `area_type`: IdleAreaType
- `lon`: float
- `lat`: float
- `edge_idx`: int | None
- `restricted_zones`: Tuple[Tuple[Tuple[float, float]]] | list[list[list[float]]] | None
- `road_net`: dict

**Возвращает:** `Tuple[IdleArea, RouteEdge] | Tuple[None, None]`

**Вызывает:** `find_route_edges_around_restricted_zones_from_position_to_object`, `sum`, `get_areas`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\simulations\utils\mixins.py`

### Импорты
- `import enum`
- `from dataclasses import fields`
- `from typing import Any`

### Публичные функции

#### serialize (`DataclassEnumSerializerMixin`)
**Аргументы:**
- `field_value`: Any

**Вызывает:** `str`, `isinstance`

---

#### to_dict (`DataclassEnumSerializerMixin`)
**Аргументы:**
- `self`

**Возвращает:** `dict`

**Вызывает:** `str`, `isinstance`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\simulations\utils\service_locator.py`

### Импорты
- `from typing import Any`

### Публичные функции

#### bind (`ServiceLocator`)
**Аргументы:**
- `cls`
- `alias`: str
- `instance`: Any

**Возвращает:** `None`

**Вызывает:** `has`, `RuntimeError`

---

#### get_or_fail (`ServiceLocator`)
**Аргументы:**
- `cls`
- `alias`: str
- `fail_message`: str | None = None

**Возвращает:** `Any`

**Вызывает:** `RuntimeError`, `get`

---

#### get (`ServiceLocator`)
**Аргументы:**
- `cls`
- `alias`: str

**Возвращает:** `Any`

**Вызывает:** `has`

---

#### has (`ServiceLocator`)
**Аргументы:**
- `cls`
- `alias`: str

**Возвращает:** `bool`

---

#### unbind (`ServiceLocator`)
**Аргументы:**
- `cls`
- `alias`: str

**Возвращает:** `None`

---

#### unbind_all (`ServiceLocator`)
**Аргументы:**
- `cls`

**Возвращает:** `None`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\simulations\utils\trip_service.py`

### Импорты
- `import math`
- `import datetime`
- `import logging`
- `from collections import defaultdict`
- `from app.sim_engine.core.props import ActualTrip, ShiftChangeArea, QuarryObject, TripData, IdleArea`
- `from app.sim_engine.core.simulations.utils.helpers import sim_current_time, sim_start_time`
- `from app.sim_engine.enums import ObjectType`

### Публичные функции

#### __init__ (`TripService`)
**Аргументы:**
- `self`

**Возвращает:** `None`

**Вызывает:** `defaultdict`, `set`

---

#### set_shift_change_area (`TripService`)
**Аргументы:**
- `self`
- `shift_change_area`: IdleArea

**Возвращает:** `None`

---

#### begin (`TripService`)
**Аргументы:**
- `self`
- `trip_data`: TripData

**Возвращает:** `None`

**Вызывает:** `debug`, `sim_current_time`, `QuarryObject`, `RuntimeError`, `ActualTrip`

---

#### finish (`TripService`)
**Аргументы:**
- `self`
- `trip_data`: TripData

**Возвращает:** `None`

**Вызывает:** `append`, `to_telemetry`, `__finish_actual_trip`, `__update_summary_metrics`

---

#### get_summary (`TripService`)
**Аргументы:**
- `self`
- `end_time`: datetime.datetime

**Возвращает:** `dict`

**Вызывает:** `list`, `floor`, `sim_start_time`, `range`, `len`, `append`, `get`

---

#### print_summary (`TripService`)
**Аргументы:**
- `self`

**Вызывает:** `debug`, `sorted`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\core\simulations\utils\__init__.py`

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\infra\exception_traceback.py`

### Импорты
- `import functools`
- `import logging`
- `import traceback`

### Публичные функции

#### wrapper
**Аргументы:**
- `*args` (vararg)
- `**kwargs` (kwarg)

**Вызывает:** `wraps`, `getLogger`, `error`, `RunSimulationError`, `func`, `format_exc`

---

#### catch_errors
**Аргументы:**
- `func`

**Вызывает:** `wraps`, `getLogger`, `error`, `RunSimulationError`, `func`, `format_exc`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\infra\logger\config.py`

### Импорты
- `import logging`
- `import os`
- `from app.sim_engine.infra.logger.json_formatter import JsonFormatter`

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\infra\logger\json_formatter.py`

### Импорты
- `import datetime`
- `import json`
- `import logging`

### Публичные функции

#### format (`JsonFormatter`)
**Аргументы:**
- `self`
- `record`: logging.LogRecord

**Возвращает:** `str`

**Вызывает:** `getMessage`, `isinstance`, `update`, `dumps`, `isoformat`, `fromtimestamp`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\infra\logger\logger.py`

### Импорты
- `import logging`
- `import logging.config`
- `from app.sim_engine.infra.logger.config import LOGGING_CONFIG`

### Публичные функции

#### init (`Logger`)
**Возвращает:** `None`

**Вызывает:** `dictConfig`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\tests\run_simulate.py`

### Импорты
- `import json`
- `import logging`
- `import os`
- `from app.sim_engine.enums import ObjectType`
- `from app.sim_engine.simulation_manager import SimulationManager`

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\tests\test_simulate.py`

### Импорты
- `import json`
- `import math`
- `import os`
- `import pytest`
- `from app.sim_engine.enums import ObjectType`
- `from app.sim_engine.simulation_manager import SimulationManager`
- `from app.sim_engine.writer import DictSimpleWriter`

### Публичные функции

#### input_data
**Вызывает:** `open`, `dirname`, `load`, `join`

---

#### validate_result
**Аргументы:**
- `result`: dict

**Вызывает:** `floor`, `isinstance`

---

#### test_simulation_result
**Аргументы:**
- `input_data`

**Вызывает:** `isinstance`, `key`, `SimulationManager`, `run`, `len`, `validate_result`, `keys`

---

#### test_shovel_telemetry
**Аргументы:**
- `input_data`

**Вызывает:** `isinstance`, `key`, `SimulationManager`, `run`, `len`, `validate_result`, `keys`

---

#### test_truck_telemetry
**Аргументы:**
- `input_data`

**Вызывает:** `isinstance`, `key`, `SimulationManager`, `run`, `len`, `validate_result`, `keys`

---

#### test_unload_telemetry
**Аргументы:**
- `input_data`

**Вызывает:** `isinstance`, `key`, `SimulationManager`, `run`, `len`, `validate_result`, `keys`

---

#### test_fuel_station_telemetry
**Аргументы:**
- `input_data`

**Вызывает:** `isinstance`, `key`, `SimulationManager`, `run`, `len`, `validate_result`, `keys`

---

#### test_summary_result
**Аргументы:**
- `input_data`

**Вызывает:** `run`, `validate_result`, `SimulationManager`

---

#### test_events
**Аргументы:**
- `input_data`

**Вызывает:** `isinstance`, `SimulationManager`, `run`, `len`, `validate_result`, `keys`

---

#### test_summary_result_with_breakdown
**Аргументы:**
- `input_data`

**Вызывает:** `run`, `validate_result`, `SimulationManager`

---

#### test_breakdown_events_count
**Аргументы:**
- `input_data`

**Вызывает:** `len`, `run`, `validate_result`, `SimulationManager`

---

#### test_summary_result_with_refuel
**Аргументы:**
- `input_data`

**Вызывает:** `run`, `validate_result`, `SimulationManager`

---

#### test_refuel_events_count
**Аргументы:**
- `input_data`

**Вызывает:** `len`, `run`, `validate_result`, `SimulationManager`

---

#### test_summary_result_with_lunch
**Аргументы:**
- `input_data`

**Вызывает:** `run`, `validate_result`, `SimulationManager`

---

#### test_lunch_events_count
**Аргументы:**
- `input_data`

**Вызывает:** `len`, `run`, `validate_result`, `SimulationManager`

---

#### test_summary_result_with_planned_idle
**Аргументы:**
- `input_data`

**Вызывает:** `run`, `validate_result`, `SimulationManager`

---

#### test_planned_idle_events_count
**Аргументы:**
- `input_data`

**Вызывает:** `len`, `run`, `validate_result`, `SimulationManager`

---

#### test_blasting_events_count
**Аргументы:**
- `input_data`

**Вызывает:** `len`, `run`, `validate_result`, `SimulationManager`

---

#### test_auto_mode_summary_result
**Аргументы:**
- `input_data`

**Вызывает:** `run`, `validate_result`, `SimulationManager`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\sim_engine\tests\__init__.py`

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\tests\conftest.py`

### Импорты
- `import pytest`
- `from unittest.mock import Mock, patch, MagicMock`
- `from fastapi.testclient import TestClient`
- `from sqlalchemy import create_engine`
- `from sqlalchemy.orm import sessionmaker`
- `from pathlib import Path`
- `from app import create_app, get_db, get_redis`
- `from app.models import Quarry`

### Публичные функции

#### redis_mock
Создает мок-сессию базы данных

**Вызывает:** `Mock`, `patch`

---

#### override_get_db
---

#### app
---

#### client
Создает тестовый клиент FastAPI

**Аргументы:**
- `app`

**Вызывает:** `fixture`, `TestClient`

---

#### db_session
Создает мок-сессию базы данных

**Вызывает:** `Mock`, `fixture`, `patch`

---

#### init_database
Создает тестовые данные в базе (mocked)

**Аргументы:**
- `db_session`

**Вызывает:** `fixture`, `Mock`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\tests\test_api.py`

### Импорты
- `import pytest`
- `from unittest.mock import patch, MagicMock`
- `from app.models import Quarry, Truck, Shovel, FuelStation, Unload`

### Публичные функции

#### test_handbook_returns_200
**Аргументы:**
- `client`

**Вызывает:** `get`

---

#### test_defaults_returns_200_and_dict
**Аргументы:**
- `client`

**Вызывает:** `isinstance`, `get`, `json`

---

#### test_scenarios_returns_200_and_list
**Аргументы:**
- `client`

**Вызывает:** `isinstance`, `get`, `json`

---

#### test_quarry_data_returns_200_and_valid_json (`TestQuarryDataAPI`)
**Аргументы:**
- `self`
- `client`

**Вызывает:** `isinstance`, `get`, `json`

---

#### test_invalid_method_returns_405_on_get (`TestObjectAPI`)
**Аргументы:**
- `self`
- `client`

**Вызывает:** `get`

---

#### test_invalid_payload_returns_400_on_post (`TestObjectAPI`)
**Аргументы:**
- `self`
- `client`

**Вызывает:** `post`

---

#### __init__ (`DummyForm`)
**Аргументы:**
- `self`
- `*a` (vararg)
- `**kw` (kwarg)

---

#### validate (`DummyForm`)
**Аргументы:**
- `self`

---

#### instantiate_object (`DummyForm`)
**Аргументы:**
- `self`

**Вызывает:** `Quarry`

---

#### dict (`DummyForm`)
**Аргументы:**
- `self`
- `*args` (vararg)
- `**kwargs` (kwarg)

---

#### test_create_quarry_success (`TestObjectAPI`)
**Аргументы:**
- `self`
- `client`

---

#### __init__ (`DummyForm`)
**Аргументы:**
- `self`
- `*a` (vararg)
- `**kw` (kwarg)

---

#### validate (`DummyForm`)
**Аргументы:**
- `self`

---

#### instantiate_object (`DummyForm`)
**Аргументы:**
- `self`

**Вызывает:** `model_class`

---

#### dict (`DummyForm`)
**Аргументы:**
- `self`
- `*args` (vararg)
- `**kwargs` (kwarg)

---

#### test_create_object_success (`TestObjectAPI`)
**Аргументы:**
- `self`
- `client`
- `init_database`
- `object_type`
- `data_factory`
- `model_class`

---

#### test_returns_404 (`TestNotFoundEndpoints`)
Проверяем, что несуществующие ресурсы возвращают 404

**Аргументы:**
- `self`
- `client`
- `endpoint`

**Вызывает:** `parametrize`, `get`

---

## Файл: `C:\Сторонние\Цифровой двойник - документация\qsimmine12\app\tests\__init__.py`

