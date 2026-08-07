"""
core/event_bus.py

The Core Engine. This is the ONLY thing modules are allowed to talk to
directly. Modules never call each other's code directly (Task 3, 3.5).

Responsibilities:
1. Let modules register (subscribe to event types).
2. Route published events to the right subscriber(s).
3. Catch and isolate failures inside a module so one crashing module
   does not take down the whole application (fault isolation).
"""

from __future__ import annotations
from collections import defaultdict
from typing import Optional

from core.contracts import IModule, Event


class EventBus:
    def __init__(self, logger=None):
        self._subscribers: dict[str, list[IModule]] = defaultdict(list)
        self._modules: dict[str, IModule] = {}
        self._logger = logger

    def register(self, module: IModule) -> None:
        """Register a module and wire up its declared subscriptions."""
        if module.name in self._modules:
            raise ValueError(f"Module '{module.name}' is already registered")

        self._modules[module.name] = module
        for event_type in module.subscriptions():
            self._subscribers[event_type].append(module)

        self._log(f"Registered module '{module.name}' "
                   f"(subscribes to: {module.subscriptions()})")

    def publish(self, event: Event) -> list[Event]:
        """
        Route an event to every module subscribed to its type.
        Returns a list of response events (from modules that returned one).

        Fault isolation: if a subscriber raises an exception, it is caught
        here, logged, and does NOT propagate to the publisher or to other
        subscribers. One broken module cannot crash the rest of AIPOS.
        """
        self._log(f"Event published: type={event.type} source={event.source} "
                   f"id={event.event_id}")

        responses: list[Event] = []
        subscribers = self._subscribers.get(event.type, [])

        if not subscribers:
            self._log(f"No subscribers for event type '{event.type}'", level="warning")
            return responses

        for module in subscribers:
            try:
                result = module.handle_event(event)
                if result is not None:
                    responses.append(result)
            except Exception as exc:  # noqa: BLE001 - intentional, this IS the isolation boundary
                self._log(
                    f"Module '{module.name}' raised an exception while handling "
                    f"event '{event.type}': {exc!r}. Isolated — app continues running.",
                    level="error",
                )
                responses.append(
                    Event(
                        type="MODULE_ERROR",
                        payload={"module": module.name, "error": str(exc), "original_event": event.type},
                        source="core.event_bus",
                    )
                )
        return responses

    def get_module(self, name: str) -> Optional[IModule]:
        return self._modules.get(name)

    def _log(self, message: str, level: str = "info") -> None:
        if self._logger is not None:
            getattr(self._logger, level, self._logger.info)(message)
