import functools
import logging
import traceback


class RunSimulationError(Exception):
    pass


def catch_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            tb_str = traceback.format_exc()

            logger = logging.getLogger('catch_errors_decorator')
            logger.error(tb_str)

            raise RunSimulationError(e)

    return wrapper