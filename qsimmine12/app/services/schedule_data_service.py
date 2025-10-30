import json
from datetime import datetime
from typing import List, Optional, Any
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models import Quarry
from app.shift import ShiftLogic
from app.shift import (
    ShiftConfigDataException,
    ShiftConfigParseException,
)

# region DTO
class ScheduleItemDTO(BaseModel):
    id: int
    quarry_id: int
    start_time: datetime
    end_time: datetime
    geojson_data: Optional[Any] = None

    class Config:
        from_attributes = True

class ShiftDetailsDTO(BaseModel):
    number: int
    begin_time_enterprise: str
    end_time_enterprise: str
    day: str

class ScheduleDataResponseDTO(BaseModel):
    time: dict
    filters: dict
    shift_details: Optional[ShiftDetailsDTO] = None
    items: List[ScheduleItemDTO]
# endregion

# region DAO
class ScheduleDAO:
    """DAO для выборки расписания из БД."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def fetch_filtered(
        self,
        model,
        start_time_utc: datetime,
        end_time_utc: datetime,
        quarry_id: int,
        schedule_type: str,
    ) -> List[ScheduleItemDTO]:
        """Возвращает список отфильтрованных элементов расписания в виде DTO."""

        stmt = (
            select(model)
            .where(
                model.quarry_id == quarry_id,
                model.start_time < end_time_utc,
                start_time_utc < model.end_time,
            )
            .order_by(model.id.asc())
        )

        res = self.db.execute(stmt).scalars().all()
        model_cols = set(model.__table__.columns.keys())
        items: List[ScheduleItemDTO] = []

        for obj in res:
            obj_dict = {col: getattr(obj, col) for col in model_cols}
            if schedule_type == "blasting":
                if isinstance(obj_dict.get("geojson_data"), str):
                    try:
                        obj_dict["geojson_data"] = json.loads(obj_dict["geojson_data"])
                    except json.JSONDecodeError:
                        obj_dict["geojson_data"] = None

            items.append(ScheduleItemDTO(**obj_dict))

        return items
# endregion

# region services
class ScheduleDataService:
    """Сервис для получения расписания по дате и смене или временному диапазону."""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.dao = ScheduleDAO(db_session)

    def __call__(
        self,
        model,
        date_str: str,
        quarry_id: int,
        schedule_type: str,
        enterprise_tz: ZoneInfo,
        shift_number: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> ScheduleDataResponseDTO:
        """Основная точка входа."""

        quarry = self.db.get(Quarry, quarry_id)
        if not quarry:
            raise ShiftConfigDataException("Quarry not found")

        # --- вычисляем start_time_utc / end_time_utc ---
        start_time_utc, end_time_utc, target_shift = self._resolve_time_window(
            quarry, date_str, enterprise_tz, shift_number, start_time, end_time
        )

        # --- получаем элементы расписания ---
        items = self.dao.fetch_filtered(
            model=model,
            start_time_utc=start_time_utc,
            end_time_utc=end_time_utc,
            quarry_id=quarry_id,
            schedule_type=schedule_type,
        )

        # --- формируем DTO-ответ ---
        return ScheduleDataResponseDTO(
            time={
                "start_time": start_time_utc.isoformat(),
                "end_time": end_time_utc.isoformat(),
            },
            filters={
                "date": date_str,
                "quarry_id": quarry_id,
                "type": schedule_type,
                "shift_number": shift_number,
                "start_time": start_time,
                "end_time": end_time,
            },
            items=items,
            shift_details=ShiftDetailsDTO(
                number=target_shift.number,
                begin_time_enterprise=target_shift.begin_time.isoformat(),
                end_time_enterprise=target_shift.end_time.isoformat(),
                day=target_shift.day.isoformat(),
            )
            if target_shift
            else None,
        )

    # -------------------- helpers --------------------

    def _resolve_time_window(
        self,
        quarry,
        date_str: str,
        enterprise_tz: ZoneInfo,
        shift_number: Optional[int],
        start_time: Optional[str],
        end_time: Optional[str],
    ):
        """Определяет временной диапазон по номеру смены или вручную заданным временам."""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError as e:
            raise ShiftConfigParseException(str(e))

        target_shift = None

        if shift_number is not None:
            shift_logic = ShiftLogic.factory(quarry.shift_config)
            shifts_for_date = shift_logic.for_date(date, enterprise_tz)

            if shift_number > len(shifts_for_date) or shift_number <= 0:
                raise ShiftConfigDataException(f"Shift number {shift_number} not found for date {date_str}")

            target_shift = shifts_for_date[shift_number - 1]
            start_time_utc = target_shift.begin_time.astimezone(ZoneInfo("UTC"))
            end_time_utc = target_shift.end_time.astimezone(ZoneInfo("UTC"))

        elif start_time and end_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            except ValueError as e:
                raise ShiftConfigParseException(str(e))

            if start_dt.tzinfo is None:
                start_dt = start_dt.replace(tzinfo=enterprise_tz)
            if end_dt.tzinfo is None:
                end_dt = end_dt.replace(tzinfo=enterprise_tz)

            start_time_utc = start_dt.astimezone(ZoneInfo("UTC"))
            end_time_utc = end_dt.astimezone(ZoneInfo("UTC"))

        else:
            raise ShiftConfigDataException("Must specify either shift_number or start_time/end_time")

        if start_time_utc >= end_time_utc:
            raise ShiftConfigDataException("start_time must be earlier than end_time")

        return start_time_utc, end_time_utc, target_shift
# endregion
