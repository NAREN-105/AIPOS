"""
core/
The innermost layer of AIPOS. Knows about NOTHING outside itself.

Contains:
- contracts.py  -> IModule interface (Dependency Inversion Principle)
- event_bus.py  -> Core Engine / message router

Rule (Dependency Rule, ADR-003):
    modules/ -> depends on -> core/
    core/    -> NEVER depends on -> modules/
"""

from core.contracts import IModule, Event
from core.event_bus import EventBus

__all__ = ["IModule", "Event", "EventBus"]
