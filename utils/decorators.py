import functools
from pathlib import Path

try:
    from loggers.logger import logger
except ImportError as ie:
    exit(f"{ie} :: {Path(__file__).resolve()}")


class Utils:
    @staticmethod
    def exception(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"exception in '{func.__name__}' => {e}")
                return False

        return wrapper

    @staticmethod
    def async_exception(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"exception in '{func.__name__}' => {e}")
                return False
        return wrapper


utils: Utils = Utils()
