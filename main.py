"""
main.py

AIPOS v1.0 entry point. This is the ONLY file that is allowed to know
about every layer at once (core/, shared/, modules/) — it's the wiring
point ("composition root") where concrete modules get registered onto
the abstract event bus.

Run:
    python main.py
"""

from core.event_bus import EventBus
from core.contracts import Event
from shared.logger import get_logger
from modules.system_monitor import SystemMonitorModule
from modules.ai_chat import AIChatModule

logger = get_logger("aipos.main")


def build_app() -> EventBus:
    bus = EventBus(logger=logger)
    bus.register(SystemMonitorModule())
    bus.register(AIChatModule(bus))
    return bus


def run_cli() -> None:
    bus = build_app()
    print("=" * 60)
    print(" AIPOS v1.0 — AI-Powered OS Assistant (CLI demo)")
    print(" Modules loaded: system_monitor, ai_chat")
    print(" Type a message ('quit' to exit). Try: 'how's my system doing?'")
    print("=" * 60)

    while True:
        try:
            text = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting AIPOS.")
            break

        if text.lower() in ("quit", "exit"):
            print("Exiting AIPOS.")
            break

        responses = bus.publish(Event(type="USER_MESSAGE", payload={"text": text}, source="cli"))
        reply = next((r for r in responses if r.type == "AI_REPLY"), None)
        if reply:
            print(f"AIPOS: {reply.payload['text']}")
        else:
            print("AIPOS: (no response)")


if __name__ == "__main__":
    run_cli()
