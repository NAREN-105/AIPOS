from core.event_bus import EventBus
from core.contracts import IModule, Event


class EchoModule(IModule):
    """Minimal test double implementing IModule."""

    @property
    def name(self) -> str:
        return "echo"

    def subscriptions(self) -> list[str]:
        return ["PING"]

    def handle_event(self, event: Event):
        return Event(type="PONG", payload={"echo": event.payload}, source=self.name)


class CrashingModule(IModule):
    """A module that always raises, used to test fault isolation."""

    @property
    def name(self) -> str:
        return "crasher"

    def subscriptions(self) -> list[str]:
        return ["BOOM"]

    def handle_event(self, event: Event):
        raise RuntimeError("simulated crash")


def test_register_and_publish_routes_to_correct_subscriber():
    bus = EventBus()
    bus.register(EchoModule())

    responses = bus.publish(Event(type="PING", payload={"x": 1}, source="test"))

    assert len(responses) == 1
    assert responses[0].type == "PONG"
    assert responses[0].payload == {"echo": {"x": 1}}


def test_publish_with_no_subscribers_returns_empty_list():
    bus = EventBus()
    responses = bus.publish(Event(type="NOBODY_LISTENS", source="test"))
    assert responses == []


def test_duplicate_module_registration_raises():
    bus = EventBus()
    bus.register(EchoModule())

    try:
        bus.register(EchoModule())
        assert False, "expected ValueError for duplicate registration"
    except ValueError:
        pass


def test_two_modules_can_subscribe_to_different_events_independently():
    bus = EventBus()
    bus.register(EchoModule())
    bus.register(CrashingModule())

    # Only EchoModule should react to PING
    responses = bus.publish(Event(type="PING", source="test"))
    assert len(responses) == 1
    assert responses[0].source == "echo"
