import json

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone, tzinfo
from typing import Any, Mapping, Sequence, Tuple

import jsonschema

from app.consts import COMMON_SHIFT_CONFIG, THREEFOLD_SHIFT_CONFIG

__all__ = (
    'SHIFT_OFFSETS_SCHEMA',
    'ShiftConfigException',
    'ShiftConfigParseException',
    'ShiftConfigSchemaException',
    'ShiftConfigDataException',
    'ShiftLogic',
    'ShiftOffsetsDTO',
    'ShiftDTO',
)


SHIFT_OFFSETS_SCHEMA = {
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    'type': 'array',
    'minItems': 1,
    'maxItems': 3,
    'items': {
        'type': 'object',
        'properties': {
            'begin_offset': {
                'type': 'integer'
            },
            'end_offset': {
                'type': 'integer'
            }
        },
        'required': ['begin_offset', 'end_offset'],
        'additionalProperties': False
    },
    'title': 'Configuration of the work shifts',
    'examples': [
        COMMON_SHIFT_CONFIG,
        THREEFOLD_SHIFT_CONFIG
    ]
}


class ShiftConfigException(Exception):
    """
    Базовое исключение для ошибок конфигурации смен.
    """

    def __init__(self, message: str, status_code=None):
        self.message = message
        self.status_code = status_code or 400
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class ShiftConfigParseException(ShiftConfigException):
    """Парсинговые ошибки (дата/время и т.п.)."""
    pass


class ShiftConfigSchemaException(ShiftConfigException):
    """Ошибки схемы/структуры (оставляем на будущее)."""
    pass


class ShiftConfigDataException(ShiftConfigException):
    """Ошибки данных (например 'Quarry not found', 'shift not found' и т.п.)."""
    pass


class ShiftLogic:

    def __init__(self, offsets_tuple: Tuple['ShiftOffsetsDTO', ...]) -> None:
        self.offsets_tuple = offsets_tuple

    @classmethod
    def factory(cls, shift_config: str | Mapping | Sequence) -> 'ShiftLogic':
        if isinstance(shift_config, str):
            try:
                _shift_config = json.loads(shift_config)
            except TypeError as exc:
                raise ShiftConfigParseException('Improper type of json string') from exc
            except json.JSONDecodeError as exc:
                raise ShiftConfigParseException('Improper content of json string') from exc

        elif isinstance(shift_config, Mapping):
            _shift_config = [shift_config]

        elif isinstance(shift_config, Sequence):
            _shift_config = shift_config

        else:
            raise ShiftConfigParseException('Improper type of shift config data')

        cls.validate_shift_config(_shift_config)

        offsets_tuple = tuple(
            ShiftOffsetsDTO(
                timedelta(minutes=shift_offsets['begin_offset']),
                timedelta(minutes=shift_offsets['end_offset'])
            )
            for shift_offsets in _shift_config
        )
        return cls(offsets_tuple)

    @classmethod
    def validate_shift_config(cls, shift_config: Any) -> None:
        try:
            jsonschema.validate(shift_config, SHIFT_OFFSETS_SCHEMA)
        except jsonschema.ValidationError as exc:
            raise ShiftConfigSchemaException('Improper shift config json schema') from exc

        for i, shift_offsets in enumerate(shift_config):
            if shift_offsets['begin_offset'] >= shift_offsets['end_offset']:
                raise ShiftConfigDataException('Shifts must have positive duration')
            if i > 0 and shift_offsets['begin_offset'] != shift_config[i-1]['end_offset']:
                raise ShiftConfigDataException('Shifts must be in continuous sequence and in ascending order')
        if shift_config[-1]['end_offset'] - shift_config[0]['begin_offset'] != 1440:
            raise ShiftConfigDataException('Total shifts duration must be exaclty 24 hours')

    def for_date(self, day: date, tzinfo: tzinfo | None = None) -> list['ShiftDTO']:
        if tzinfo is None:
            tzinfo = timezone.utc
        result = []
        day_start = datetime.combine(day, time.min, tzinfo)
        for i, offsets in enumerate(self.offsets_tuple, 1):
            result.append(ShiftDTO(
                day=day,
                begin_time=day_start + offsets.begin_offset,
                end_time=day_start + offsets.end_offset,
                number=i,
                length=offsets.end_offset - offsets.begin_offset,
                begin_offset=offsets.begin_offset,
                end_offset=offsets.end_offset,
            ))
        return result

    def for_datetime(self, moment: datetime) -> 'ShiftDTO':
        day = moment.date()
        day_td = timedelta(days=1)
        days_in_scope = (day-day_td, day, day+day_td)
        for day in days_in_scope:
            day_start = datetime.combine(day, time.min, moment.tzinfo)
            for i, offsets in enumerate(self.offsets_tuple, 1):
                begin_time = day_start + offsets.begin_offset
                end_time = day_start + offsets.end_offset
                if begin_time <= moment < end_time:
                    return ShiftDTO(
                        day=day,
                        begin_time=begin_time,
                        end_time=end_time,
                        number=i,
                        length=offsets.end_offset - offsets.begin_offset,
                        begin_offset=offsets.begin_offset,
                        end_offset=offsets.end_offset,
                    )
        raise ShiftConfigDataException('Somehow it is improper shift config data')

    def for_range(self, start: datetime, stop: datetime) -> list['ShiftDTO']:
        start_shift = self.for_datetime(start)
        end_shift = self.for_datetime(stop)

        cur_day = start_shift.day
        cur_number = start_shift.number
        result = [start_shift]
        shifts_per_day = len(self.offsets_tuple)

        while cur_day != end_shift.day or cur_number != end_shift.number:
            if cur_number >= shifts_per_day:
                cur_number = 1
                cur_day += timedelta(days=1)
            else:
                cur_number += 1

            cur_day_start = datetime.combine(cur_day, time.min, start.tzinfo)
            cur_config = self.offsets_tuple[cur_number-1]
            result.append(ShiftDTO(
                day=cur_day,
                begin_time=cur_day_start + cur_config.begin_offset,
                end_time=cur_day_start + cur_config.end_offset,
                number=cur_number,
                length=cur_config.end_offset - cur_config.begin_offset,
                begin_offset=cur_config.begin_offset,
                end_offset=cur_config.end_offset,
            ))

        return result

    def prev_from(self, shift: 'ShiftDTO') -> 'ShiftDTO':
        if shift.number <= 1:
            prev_number = len(self.offsets_tuple)
            prev_day = shift.day - timedelta(days=1)
        else:
            prev_number = shift.number - 1
            prev_day = shift.day
        prev_day_start = datetime.combine(prev_day, time.min, shift.begin_time.tzinfo)
        offsets = self.offsets_tuple[prev_number - 1]
        return ShiftDTO(
            day=prev_day,
            begin_time=prev_day_start + offsets.begin_offset,
            end_time=prev_day_start + offsets.end_offset,
            number=prev_number,
            length=offsets.end_offset - offsets.begin_offset,
            begin_offset=offsets.begin_offset,
            end_offset=offsets.end_offset,
        )

    def next_from(self, shift: 'ShiftDTO') -> 'ShiftDTO':
        if shift.number >= len(self.offsets_tuple):
            next_number = 1
            next_day = shift.day + timedelta(days=1)
        else:
            next_number = shift.number + 1
            next_day = shift.day
        next_day_start = datetime.combine(next_day, time.min, shift.begin_time.tzinfo)
        offsets = self.offsets_tuple[next_number - 1]
        return ShiftDTO(
            day=next_day,
            begin_time=next_day_start + offsets.begin_offset,
            end_time=next_day_start + offsets.end_offset,
            number=next_number,
            length=offsets.end_offset - offsets.begin_offset,
            begin_offset=offsets.begin_offset,
            end_offset=offsets.end_offset,
        )


@dataclass(frozen=True, slots=True)
class ShiftOffsetsDTO:
    begin_offset: timedelta
    end_offset: timedelta


@dataclass(frozen=True, slots=True)
class ShiftDTO:
    day: date
    begin_time: datetime
    end_time: datetime
    number: int
    length: timedelta
    begin_offset: timedelta
    end_offset: timedelta
