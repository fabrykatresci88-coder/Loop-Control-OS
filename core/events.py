from __future__ import annotations

from collections import defaultdict
from threading import RLock
from typing import Any, Callable, DefaultDict, Dict, Set


EventCallback = Callable[[Any], None]


class EventBusError(Exception):
    """Base exception for all EventBus errors."""


class EventBus:
    """Lightweight in-process pub/sub event bus.

    This implementation is intentionally minimal and thread-safe. It
    supports multiple subscribers per event name and safely handles
    dynamic subscription changes while publishing.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._subscribers: DefaultDict[str, Set[EventCallback]] = defaultdict(set)

    def publish(self, event_name: str, data: Any = None) -> None:
        """Publish an event to all subscribers registered for the event."""
        with self._lock:
            callbacks = tuple(self._subscribers.get(event_name, set()))

        for callback in callbacks:
            callback(data)

    def subscribe(self, event_name: str, callback: EventCallback) -> None:
        """Subscribe a callback to a named event."""
        if not callable(callback):
            raise EventBusError("Callback must be callable.")

        with self._lock:
            self._subscribers[event_name].add(callback)

    def unsubscribe(self, event_name: str, callback: EventCallback) -> None:
        """Unsubscribe a callback from a named event."""
        with self._lock:
            callbacks = self._subscribers.get(event_name)
            if not callbacks or callback not in callbacks:
                raise EventBusError(
                    f"Callback not registered for event '{event_name}'."
                )
            callbacks.remove(callback)
            if not callbacks:
                self._subscribers.pop(event_name, None)

    def clear(self) -> None:
        """Remove all subscriptions from the event bus."""
        with self._lock:
            self._subscribers.clear()
