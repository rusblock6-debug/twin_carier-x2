import enum


class PayloadType(enum.StrEnum):
    GRAVEL = enum.auto()
    SAND = enum.auto()
    CLAY = enum.auto()
    WET_ORE = enum.auto()


class UnloadType(enum.StrEnum):
    HYDRAULIC = enum.auto()
    MECHANICAL = enum.auto()
    GRAVITY = enum.auto()


class TrailType(enum.StrEnum):
    COMMON = enum.auto()
    UNCOMMON = enum.auto()
    SPECIAL = enum.auto()
