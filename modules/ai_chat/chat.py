"""
modules/ai_chat/chat.py

Rule-based chat module for v1.0 (no external LLM/API key required, so
the project runs offline out of the box — matches the "trust/privacy
risk" you flagged in Task 1: nothing leaves the machine in v1.0).

This module also demonstrates the exact end-to-end flow designed in
Task 3, section 3.5: "How's my system doing?" -> AI Chat publishes
REQUEST_SYSTEM_STATS -> Core Engine routes it -> System Monitor
responds -> Core Engine routes the result back -> AI Chat replies.

AI Chat never imports System Monitor directly. It only knows the
EventBus (core/), which is an allowed dependency direction.
"""

from __future__ import annotations

from core.contracts import IModule, Event
from core.event_bus import EventBus
from shared.logger import get_logger

logger = get_logger("aipos.ai_chat")

_SYSTEM_KEYWORDS = ("system", "cpu", "ram", "memory", "disk", "performance")


class AIChatModule(IModule):
    def __init__(self, bus: EventBus):
        # Allowed: modules/ -> depends on -> core/ (EventBus)
        self._bus = bus

    @property
    def name(self) -> str:
        return "ai_chat"

    def subscriptions(self) -> list[str]:
        return ["USER_MESSAGE"]

    def handle_event(self, event: Event) -> Event | None:
        if event.type != "USER_MESSAGE":
            return None

        message = str(event.payload.get("text", "")).strip()
        reply = self._build_reply(message)
        logger.info(f"USER_MESSAGE='{message}' -> reply='{reply}'")

        return Event(
            type="AI_REPLY",
            payload={"text": reply, "in_reply_to": message},
            source=self.name,
        )

    def _build_reply(self, message: str) -> str:
        if not message:
            return "I didn't catch that — ask me something."

        lowered = message.lower()

        if any(word in lowered for word in _SYSTEM_KEYWORDS):
            return self._reply_with_system_stats()

        if "hello" in lowered or "hi" in lowered:
            return "Hey! I'm AIPOS. Ask me how your system is doing."

        return (
            "I'm a rule-based v1.0 assistant — I can currently report live "
            "system stats. Try asking: 'how's my system doing?'"
        )

    def _reply_with_system_stats(self) -> str:
        # Cross-module communication happens ONLY through the event bus —
        # AI Chat never imports SystemMonitorModule directly.
        request = Event(type="REQUEST_SYSTEM_STATS", source=self.name)
        responses = self._bus.publish(request)

        result = next((r for r in responses if r.type == "SYSTEM_STATS_RESULT"), None)
        if result is None:
            # Fault isolation in action: System Monitor is unavailable/crashed,
            # AI Chat degrades gracefully instead of crashing.
            return "I couldn't fetch system stats right now — the monitor may be unavailable."

        stats = result.payload
        return (
            f"CPU: {stats['cpu_percent']}% | "
            f"RAM: {stats['ram_percent']}% | "
            f"Disk: {stats['disk_percent']}%"
        )
