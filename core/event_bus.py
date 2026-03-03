"""
Simple event bus for decoupled gameplay notifications.
"""
from collections import defaultdict


class EventBus:
    """Publish/subscribe event bus."""

    def __init__(self):
        self._handlers = defaultdict(list)

    def subscribe(self, event_name, handler):
        self._handlers[event_name].append(handler)

    def emit(self, event_name, **payload):
        for handler in self._handlers.get(event_name, []):
            handler(**payload)
