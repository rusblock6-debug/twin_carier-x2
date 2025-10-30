import logging
import logging.config

from app.sim_engine.infra.logger.config import LOGGING_CONFIG


class Logger:
    @staticmethod
    def init() -> None:
        logging.config.dictConfig(LOGGING_CONFIG)
