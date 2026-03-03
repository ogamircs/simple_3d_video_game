"""
Gameplay telemetry logging hooks.
"""
import logging
from config import TELEMETRY_LOG_PATH, TELEMETRY_ENABLED


class Telemetry:
    """Structured-ish logger for gameplay events."""

    def __init__(self):
        self.logger = logging.getLogger('gameplay')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.FileHandler(TELEMETRY_LOG_PATH, encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log(self, event_name, **fields):
        if not TELEMETRY_ENABLED:
            return
        payload = ' '.join([f'{k}={v}' for k, v in fields.items()])
        self.logger.info('%s %s', event_name, payload)
