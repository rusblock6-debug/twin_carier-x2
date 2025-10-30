import os

__all__ = (
    'COMMON_SHIFT_CONFIG',
    'THREEFOLD_SHIFT_CONFIG',
    'STORED_RESULTS_NUMBER',
)


COMMON_SHIFT_CONFIG = [
    {
        'begin_offset': 480,
        'end_offset': 1200
    },
    {
        'begin_offset': 1200,
        'end_offset': 1920
    }
]
"""08-20 / 20-08"""


THREEFOLD_SHIFT_CONFIG = [
    {
        'begin_offset': 0,
        'end_offset': 480
    },
    {
        'begin_offset': 480,
        'end_offset': 960
    },
    {
        'begin_offset': 960,
        'end_offset': 1440
    }
]
"""00-08 / 08-16 / 16-00"""


STORED_RESULTS_NUMBER = int(os.getenv('STORED_RESULTS_NUMBER', 1))
"""Количество детально хранимых симуляций на каждый Сценарий"""
