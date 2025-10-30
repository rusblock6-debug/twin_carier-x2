import datetime
import json
import logging


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_object = {
            'timestamp': datetime.datetime.fromtimestamp(record.created, datetime.UTC).isoformat() + 'Z',
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
            'filename': record.filename,
            'lineno': record.lineno,
        }

        if record.args and isinstance(record.args, dict):
            # log_object['data'] = json.dumps(record.args, ensure_ascii=False)
            # log_object['data'] = record.args
            log_object.update(record.args)

        return json.dumps(log_object, ensure_ascii=False)
