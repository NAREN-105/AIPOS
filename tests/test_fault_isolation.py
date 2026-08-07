"""
tests/test_fault_isolation.py

This test PROVES the architectural claim from Task 3: if one module
crashes while handling an event, it does not crash the event bus or
any other module. This is what makes "modules never call each other
directly" worth doing.
"""

from core.event_bus import EventBus
from core.contracts import IModule, Event


class CrashingModule(IModule):
    @property
    def name(self) -> str:
        return "crasher"

    def subscriptions(self) -> list[str]:
        return ["TRIGGER"]

    def handle_event(self, event: Event):
        raise RuntimeError("simulated crash inside a module")


class HealthyModule(IModule):
    @property
    def name(self) -> str:
        return "healthy"

    def subscriptions(self) -> list[str]:
        return ["TRIGGER"]

    def handle_event(self, event: Event):
        return Event(type="HEALTHY_OK", source=self.name)


def test_crashing_module_does_not_raise_out_of_publish():
    """publish() must never let a module's exception escape."""
    bus = EventBus()
    bus.register(CrashingModule())

    # This must NOT raise — that's the whole point of fault isolation.
    responses = bus.publish(Event(type="TRIGGER", source="test"))

    error_events = [r for r in responses if r.type == "MODULE_ERROR"]
    assert len(error_events) == 1
    assert error_events[0].payload["module"] == "crasher"


def test_healthy_module_still_responds_when_another_subscriber_crashes():
    """A crash in one subscriber must not stop other subscribers from running."""
    bus = EventBus()
    bus.register(CrashingModule())
    bus.register(HealthyModule())

    responses = bus.publish(Event(type="TRIGGER", source="test"))

    ok_events = [r for r in responses if r.type == "HEALTHY_OK"]
    error_events = [r for r in responses if r.type == "MODULE_ERROR"]

    assert len(ok_events) == 1, "HealthyModule should still have run and responded"
    assert len(error_events) == 1, "CrashingModule's failure should be reported, not swallowed silently"


def test_ai_chat_degrades_gracefully_if_system_monitor_is_missing():
    """
    Real AIPOS scenario (Task 3, 3.5): AI Chat asks for system stats.
    If System Monitor isn't registered/crashes, AI Chat must not crash —
    it should degrade gracefully, per the technical risk identified in Task 1.
    """
    from modules.ai_chat import AIChatModule

    bus = EventBus()
    bus.register(AIChatModule(bus))  # System Monitor deliberately NOT registered

    responses = bus.publish(
        Event(type="USER_MESSAGE", payload={"text": "how's my system doing?"}, source="test")
    )

    reply = next(r for r in responses if r.type == "AI_REPLY")
    assert "couldn't fetch" in reply.payload["text"].lower()
