import logging
import os

from app.sim_engine.infra.logger.json_formatter import JsonFormatter

if os.getenv('APP_MODE') == 'dev':
    FORMATTER_ALIAS = 'json'
    LOG_LEVEL = logging.DEBUG
else:
    FORMATTER_ALIAS = 'json'
    LOG_LEVEL = logging.INFO

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s',
        },
        'json': {
            '()': JsonFormatter,
            'format': '%(asctime)s %(levelname)s %(name)s %(pathname)s %(lineno)s %(funcName)s %(message)s %(extra)s %(exc_info)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': FORMATTER_ALIAS,
            'stream': 'ext://sys.stdout',
        }
    },
    'loggers': {
        'app': {
            'level': logging.getLevelName(LOG_LEVEL),
            'handlers': ['console'],
            'propagate': True,
        },
    },
}
