from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import uuid, json
from operator import itemgetter

from app.consts import STORED_RESULTS_NUMBER
from app.sim_engine.writer import BatchWriter
from app.sim_engine.simulation_manager import SimulationManager

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, field_validator, ValidationInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import RoadNet, TYPE_SCHEDULE_MAP


class SimulationRequestDTO(BaseModel):
    """Модель запроса для запуска симуляции."""

    quarry: Dict[str, Any]
    start_time: str = Field(..., description="ISO datetime string (UTC или с таймзоной)")
    end_time: str = Field(..., description="ISO datetime string (UTC или с таймзоной)")
    scenario: Optional[Dict[str, Any]] = None

    @field_validator("quarry")
    @classmethod
    def validate_quarry(cls, v):
        if not v or "id" not in v:
            raise ValueError("Field 'quarry.id' is required")
        return v

    @field_validator("end_time")
    @classmethod
    def validate_times(cls, v: str, info: ValidationInfo):
        start_str = info.data.get("start_time")
        if not start_str:
            return v

        try:
            start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        except Exception:
            raise ValueError("Invalid datetime format for 'start_time' or 'end_time'")

        if end_dt <= start_dt:
            raise ValueError("'end_time' must be after 'start_time'")

        return v

class SimulationDAO:
    """Работа с базой данных для симуляции."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def fetch_road_net_by_id(self, road_net_id: int):
        stmt = select(RoadNet).where(RoadNet.id == road_net_id)
        return self.db.execute(stmt).scalar()

    def get_filtered_schedule_items(self, model, start_time_utc, end_time_utc, quarry_id, schedule_type) -> list:
        model_cols = set(model.__table__.columns.keys())

        stmt = select(model).where(
            model.quarry_id == quarry_id,
            model.start_time < end_time_utc,
            start_time_utc < model.end_time
        ).order_by(model.id.asc())

        res = self.db.execute(stmt).scalars()

        item_list = []
        for obj in res:
            obj_dict = {
                col_name: getattr(obj, col_name)
                for col_name in model_cols
            }
            if schedule_type == 'blasting':
                if 'geojson_data' in obj_dict and isinstance(obj_dict['geojson_data'], str):
                    try:
                        obj_dict['geojson_data'] = json.loads(obj_dict['geojson_data'])
                    except json.JSONDecodeError:
                        obj_dict['geojson_data'] = None
            item_list.append(obj_dict)

        return item_list



    def fetch_schedules(self, quarry_id: int, start_time: datetime, end_time: datetime) -> dict:
        """Получает blasting и planned_idle расписания для карьера."""
        schedules = {"blasting": [], "planned_idle": []}

        for schedule_type in ["blasting", "planned_idle"]:
            model = TYPE_SCHEDULE_MAP.get(schedule_type)
            items = self.get_filtered_schedule_items(
                model, start_time, end_time, quarry_id, schedule_type
            )
            schedules[schedule_type] = items

        return schedules

class GetSimIdService:
    """Основной сервис симуляции — собирает данные, запускает SimulationManager и сохраняет результат."""

    def __init__(self, data: SimulationRequestDTO, db, redis_client):
        self.data = data
        self.db = db
        self.redis = redis_client
        self.dao = SimulationDAO(db)

    async def __call__(self):
        quarry_id = self.data.quarry["id"]

        start_dt = datetime.fromisoformat(self.data.start_time.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(self.data.end_time.replace("Z", "+00:00"))
        start_time_utc = start_dt.astimezone(ZoneInfo("UTC"))
        end_time_utc = end_dt.astimezone(ZoneInfo("UTC"))

        # Получение расписаний
        schedules = self.dao.fetch_schedules(quarry_id, start_time_utc, end_time_utc)
        self.data.quarry["schedules"] = schedules

        # Добавление RoadNet
        road_net_id = self.data.quarry.get("road_net_id")
        if road_net_id:
            rn = self.dao.fetch_road_net_by_id(road_net_id)
            if rn:
                self.data.quarry["road_net"] = rn.geojson_data

        # Запуск SimulationManager
        writer = BatchWriter(batch_size_seconds=60)
        scenario = self.data.scenario or {}

        mode = "auto" if scenario.get("is_auto_truck_distribution") else "manual"
        reliability = scenario.get("is_calc_reliability_enabled", False)
        options = {
            "mode": mode,
            "reliability_calc_enabled": reliability
        }

        manager = SimulationManager(
            raw_data=self.data.model_dump(),
            writer=writer,
            options=options
        )

        sim_data = manager.run()

        # Сохранение в Redis
        sim_id = str(uuid.uuid4())
        scenario_id = scenario.get("id", "unknown")
        sim_key_base = f"simulation:scenario_{scenario_id}"
        sim_key_plus_id = f"{sim_key_base}:{sim_id}"
        ttl = timedelta(hours=12)

        self._store_simulation_data(sim_key_plus_id, sim_data, ttl)
        self._cleanup_old_simulations(sim_key_base)

        return sim_id

    # region Helpers
    def _store_simulation_data(self, sim_key_base: str, sim_data: dict, ttl: timedelta):
        """Сохраняет результаты симуляции в Redis."""
        self.redis.setex(f"{sim_key_base}:meta", ttl, json.dumps(sim_data["meta"]))
        self.redis.setex(f"{sim_key_base}:summary", ttl, json.dumps(sim_data["summary"]))
        self.redis.setex(f"{sim_key_base}:events", ttl, json.dumps(sim_data["events"]))

        pipe = self.redis.pipeline()
        for batch_key, batch_data in sim_data["batches"].items():
            pipe.setex(f"{sim_key_base}:batch:{batch_key}", ttl, json.dumps(batch_data))
        pipe.execute()

    def _cleanup_old_simulations(self, sim_key_base: str):
        """Удаляет старые симуляции, если их слишком много."""
        stored_meta_keys = [
            (key, self.redis.ttl(key))
            for key in self.redis.scan_iter(f"{sim_key_base}:*:meta", 1000)
        ]
        stored_meta_keys.sort(key=itemgetter(1), reverse=True)

        if len(stored_meta_keys) <= STORED_RESULTS_NUMBER:
            return

        key_patterns_to_delete = [
            meta_key[0].replace(":meta", ":*")
            for meta_key in stored_meta_keys[STORED_RESULTS_NUMBER:]
        ]
        for key_pattern in key_patterns_to_delete:
            stored_keys_to_delete = [
                key for key in self.redis.scan_iter(key_pattern, 1000)
            ]
            if stored_keys_to_delete:
                self.redis.delete(*stored_keys_to_delete)
    # endregion

