from __future__ import annotations
import os
from datetime import datetime, date
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Optional

from pydantic import BaseModel

# region DTO
class StartEndTimeDTO(BaseModel):
    """
    DTO содержит времена в UTC.
    """
    start_time: datetime
    end_time: datetime
# endregion

# region Service
class StartEndTimeGenerateService:
    """
    Генерирует начало/конец рабочего дня в часовом поясе предприятия и возвращает их в UTC.
    По умолчанию берёт таймзону из окружения TZ, иначе 'UTC'.
    """

    def __init__(self, tz_name: Optional[str] = None, start_hour: int = 10, end_hour: int = 18):
        """
        :param tz_name: имя таймзоны (например, 'Europe/Berlin'). Если None — используется переменная окружения TZ или 'UTC'.
        :param start_hour: час начала рабочего дня в локальном времени предприятия.
        :param end_hour: час конца рабочего дня в локальном времени предприятия.
        """
        self.tz_name = tz_name or os.getenv("TZ", "UTC")
        self.tz = self._load_zone(self.tz_name)
        self.start_hour = int(start_hour)
        self.end_hour = int(end_hour)

    @staticmethod
    def _load_zone(name: str) -> ZoneInfo:
        try:
            return ZoneInfo(name)
        except ZoneInfoNotFoundError:
            return ZoneInfo("UTC")

    def _current_date_in_enterprise_tz(self) -> date:
        now = datetime.now(self.tz)
        return now.date()

    def _generate_time_in_enterprise_tz(self, on_date: date, hour: int) -> datetime:
        return datetime(on_date.year, on_date.month, on_date.day, hour, 0, 0, tzinfo=self.tz)

    @staticmethod
    def _to_utc(dt: datetime) -> datetime:
        return dt.astimezone(ZoneInfo("UTC"))

    def __call__(self) -> StartEndTimeDTO:
        on_date = self._current_date_in_enterprise_tz()

        start_local = self._generate_time_in_enterprise_tz(on_date, self.start_hour)
        end_local = self._generate_time_in_enterprise_tz(on_date, self.end_hour)

        start_utc = self._to_utc(start_local)
        end_utc = self._to_utc(end_local)

        return StartEndTimeDTO(start_time=start_utc, end_time=end_utc)
# endregion