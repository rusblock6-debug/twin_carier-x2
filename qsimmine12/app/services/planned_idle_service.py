import os
from abc import ABC, abstractmethod
from datetime import datetime, time
from typing import Any, Sequence, Dict, List, Type
from zoneinfo import ZoneInfo

from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.abstract.dao import AbstractDAO
from app.models import PlannedIdle, Quarry
from app.shift import ShiftLogic


# region DAO
class PlannedIdleDAO(AbstractDAO[PlannedIdle]):
    @property
    def _model(self) -> Type[PlannedIdle]:
        return PlannedIdle

    def fetch_filtered(
            self,
            start_time_utc: datetime,
            end_time_utc: datetime,
            quarry_id: int,
    ) -> Sequence[PlannedIdle]:
        stmt = (
            select(self._model)
            .where(
                self._model.quarry_id == quarry_id,
                self._model.start_time < end_time_utc,
                start_time_utc < self._model.end_time,
            )
            .order_by(self._model.id.asc())
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
class AbstractPlannedIdleService(ABC):
    def __init__(self, db_session: Session):
        self._dao = PlannedIdleDAO(db_session)
        self._db = db_session

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def _delete_schedule_items(self, obj_data: Dict[str, Any], model, enterprise_tz: ZoneInfo) -> int:
        quarry_id = obj_data.get('quarry_id')
        date_str = obj_data.get('startDate')
        work_shift_info = obj_data.get('workShift')

        if not all([quarry_id, date_str, work_shift_info]):
            raise ValueError("Missing quarry_id, startDate, or workShift in obj_data for deletion")

        quarry = self._db.get(Quarry, quarry_id)
        if not quarry or not quarry.shift_config:
            raise ValueError(f"Quarry {quarry_id} not found or has no shift_config")

        filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        shift_logic = ShiftLogic.factory(quarry.shift_config)

        target_begin_offset = work_shift_info.get('begin_offset')
        target_end_offset = work_shift_info.get('end_offset')

        if target_begin_offset is None or target_end_offset is None:
            raise ValueError("workShift missing begin_offset or end_offset")

        shifts_for_date = shift_logic.for_date(filter_date, enterprise_tz)

        target_shift = None
        for shift in shifts_for_date:
            if (shift.begin_offset.total_seconds() // 60 == target_begin_offset and
                    shift.end_offset.total_seconds() // 60 == target_end_offset):
                target_shift = shift
                break

        if not target_shift:
            raise ValueError(
                f"Shift with begin_offset {target_begin_offset} and end_offset {target_end_offset} not found for date {date_str}")

        shift_start_enterprise = target_shift.begin_time
        shift_end_enterprise = target_shift.end_time

        shift_start_utc = shift_start_enterprise.astimezone(ZoneInfo('UTC'))
        shift_end_utc = shift_end_enterprise.astimezone(ZoneInfo('UTC'))

        deleted = self._db.execute(
            delete(model).where(
                model.quarry_id == quarry_id,
                model.start_time < shift_end_utc,
                shift_start_utc < model.end_time
            )
        ).rowcount
        return deleted


class DeletePlannedIdleService(AbstractPlannedIdleService):
    def __call__(self, obj_data: Dict[str, Any], model, schedule_type: str):
        enterprise_tz = ZoneInfo(os.getenv('TZ', 'UTC'))
        try:
            deleted_count = self._delete_schedule_items(obj_data, model, enterprise_tz)
            self._db.commit()
            return JSONResponse({
                'success': True,
                'deleted_count': deleted_count,
                'message': f'Успешно удалено {deleted_count} записей {schedule_type}'
            })
        except Exception as e:
            self._db.rollback()
            return JSONResponse({'success': False, 'error': f'Error deleting {schedule_type} records: {str(e)}'},
                                status_code=500)


class CreatePlannedIdleService(AbstractPlannedIdleService):
    def __call__(self, obj_data: Dict[str, Any], model, schedule_type: str) -> JSONResponse:
        enterprise_tz = ZoneInfo(os.getenv('TZ', 'UTC'))

        try:
            deleted_count = self._delete_schedule_items(obj_data, model, enterprise_tz)

            created_ids: List[int] = []

            equipment_timelines = obj_data.get('equipmentTimelines', [])

            for eq_timeline in equipment_timelines:
                if not eq_timeline.get('items'):
                    continue

                vehicle_type = eq_timeline.get('equipmentType')
                vehicle_id = eq_timeline.get('equipmentId')

                for item in eq_timeline.get('items', []):
                    schedule_obj = model()
                    schedule_obj.quarry_id = obj_data['quarry_id']
                    schedule_obj.vehicle_type = vehicle_type
                    schedule_obj.vehicle_id = vehicle_id

                    start_time = datetime.fromisoformat(item['start'].replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(item['end'].replace('Z', '+00:00'))

                    schedule_obj.start_time = start_time
                    schedule_obj.end_time = end_time

                    self._db.add(schedule_obj)
                    created_ids.append(schedule_obj.id)

            self._db.commit()

            return JSONResponse({
                'success': True,
                'ids': created_ids,
                'count': len(created_ids),
                'deleted_count': deleted_count
            })

        except Exception as e:
            self._db.rollback()
            return JSONResponse({'success': False, 'error': f'Error processing {schedule_type} records: {str(e)}'},
                                status_code=500)


class BulkDeletePlannedIdleService(AbstractPlannedIdleService):
    def __call__(self, ids: List[int]) -> None:
        self._dao.delete_where_in(ids)
# endregion
