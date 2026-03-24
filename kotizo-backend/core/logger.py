import logging
import json
from datetime import datetime, timezone

class KotizoJsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'module': record.module,
            'message': record.getMessage(),
        }
        if isinstance(record.msg, dict):
            log.update(record.msg)
        return json.dumps(log, ensure_ascii=False)