from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import Any, Dict, List, Sequence, Type
from zoneinfo import ZoneInfo

from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.abstract.dao import AbstractDAO
from app.forms import BlastingSchema
from app.models import Blasting, Quarry


# region DTO
class BlastingDTO(BaseModel):
    id: int
    geojson_data: Dict[str, Any]
    start_time: datetime
    end_time: datetime
    quarry_id: int
    created_at: datetime
    updated_at: datetime
    date: datetime


# endregion


# region DAO
class BlastingDAO(AbstractDAO[Blasting]):
    @property
    def _model(self) -> Type[Blasting]:
        return Blasting

    def fetch_blasting_for_date(self, quarry_id: int, blasting_date: date) -> Sequence[Blasting]:
        start_of_day = datetime.combine(blasting_date, datetime.min.time())
        end_of_day = datetime.combine(blasting_date, datetime.max.time())

        stmt = (
            select(self._model)
            .where(
                self._model.quarry_id == quarry_id,
                start_of_day <= self._model.start_time,
                self._model.end_time <= end_of_day,
            )
            .order_by(self._model.start_time)
        )

        return self._db.execute(stmt).scalars().all()

    def delete(self, quarry_id: int, start: datetime, end: datetime) -> int:
        return self._db.execute(
            delete(self._model).where(
                self._model.quarry_id == quarry_id,
                start <= self._model.end_time,
                self._model.start_time <= end,
            )
        ).rowcount()


# endregion

# region Service
class AbstractBlastingService(ABC):
    def __init__(self, db_session: Session):
        self._dao = BlastingDAO(db_session)
        self._db = db_session

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Any:
        raise NotImplementedError()


class CreateBlastingService(AbstractBlastingService):
    def __call__(self, schema: BlastingSchema) -> JSONResponse:
        quarry: Quarry | None = self._db.get(Quarry, schema.quarry_id)
        if not quarry:
            raise Exception('Quarry not found')
        enterprise_tz = ZoneInfo(quarry.timezone)

        records = []
        unique_existing_records_ids = set()
        existing_records = self._dao.fetch_blasting_for_date(schema.quarry_id, schema.start_date.date())

        for i, item in enumerate(schema.timeline_items):
            exists = False
            for record in existing_records:
                exists = all([
                    record.start_time == item.start_utc(enterprise_tz),
                    record.end_time == item.end_utc(enterprise_tz),
                ])
                if exists:
                    unique_existing_records_ids.add(record.id)
                    break

            if exists:
                continue

            schedule_obj = Blasting()
            schedule_obj.quarry_id = schema.quarry_id
            schedule_obj.start_time = item.start
            schedule_obj.end_time = item.end

            geojson = item.to_geojson(i)

            schedule_obj.geojson_data = geojson
            records.append(schedule_obj)

        created_ids = self._dao.insert(records)

        to_delete = []
        for record in existing_records:
            if record.id not in unique_existing_records_ids:
                to_delete.append(record.id)

        if len(to_delete) > 0:
            self._dao.delete_where_in(to_delete)

        return JSONResponse({
            'success': True,
            'ids': created_ids,
            'count': len(created_ids),
            'deleted_count': len(to_delete),
        })


class BulkDeleteBlastingService(AbstractBlastingService):
    def __call__(self, ids: List[int]) -> None:
        self._dao.delete_where_in(ids)


class DeleteBlastingService(AbstractBlastingService):
    def __call__(self, schema: BlastingSchema) -> int:
        count = 0

        for item in schema.timeline_items:
            count += self._dao.delete(
                schema.quarry_id,
                item.start,
                item.end,
            )

        return count

# endregion
