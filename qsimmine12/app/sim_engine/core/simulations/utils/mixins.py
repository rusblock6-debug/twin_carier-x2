import enum
from dataclasses import fields
from typing import Any


class DataclassEnumSerializerMixin:
    def to_dict(self) -> dict:
        def serialize(field_value: Any):
            if isinstance(field_value, enum.Enum):
                return str(field_value)
            return field_value

        result = {}
        for field in fields(self):
            value = getattr(self, field.name)
            result[field.name] = serialize(value)

        return result
