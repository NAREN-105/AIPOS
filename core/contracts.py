"""
core/contracts.py

Defines the contract every feature module must implement to plug into
the Core Engine's event bus, and the Event object modules communicate with.

Why this file exists (ADR-003):
    core/ must be able to talk to "something that implements IModule"
    without ever importing a concrete module (ai_chat, system_monitor, ...).
    This is the Dependency Inversion Principle ("depend on abstractions,
    not concrete implementations") — it's what lets new modules be added
    later without ever touching core/'s code.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
import uuid


@dataclass
class Event:
    """
    The message format that flows through the event bus.

    type       : string name of the event, e.g. "REQUEST_CPU_USAGE"
    payload    : arbitrary data attached to the event
    source     : name of the module that published the event
    event_id   : unique id, useful for tracing/logging
    timestamp  : when the event was created (UTC)
    reply_to   : optional event type the receiver should publish back,
                 used for simple request/response flows over the bus
    """
    type: str
    payload: dict = field(default_factory=dict)
    source: str = "unknown"
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reply_to: Optional[str] = None


class IModule(ABC):
    """
    Every feature module (ai_chat, system_monitor, future modules...)
    must implement this interface. core/ only ever depends on THIS
    abstract class, never on a concrete module.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique module name, used for logging and event routing."""
        raise NotImplementedError

    @abstractmethod
    def handle_event(self, event: Event) -> Optional[Event]:
        """
        Handle an incoming event and optionally return a response Event.
        Must NOT raise uncaught exceptions that crash the whole app —
        the event bus wraps this call, but modules should still fail
        gracefully where possible (fault isolation, ADR-003).
        """
        raise NotImplementedError

    def subscriptions(self) -> list[str]:
        """
        List of event types this module wants to receive.
        Default: subscribe to nothing until overridden.
        """
        return []
