from datetime import datetime, timedelta

from app.sim_engine.core.simulations.utils.dependency_resolver import DependencyResolver as DR


def sim_current_timestamp() -> float:
    return sim_current_time().timestamp()


def sim_current_time() -> datetime:
    env = DR.env()
    return env.sim_data.start_time + timedelta(seconds=env.now)


def sim_end_time() -> datetime:
    env = DR.env()
    return env.sim_data.end_time


def sim_start_time() -> datetime:
    env = DR.env()
    return env.sim_data.start_time


def sim_duration() -> int:
    env = DR.env()
    return env.sim_data.duration


def safe_int(value, default=None):
    """Безопасное преобразование в int"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default