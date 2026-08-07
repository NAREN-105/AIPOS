"""
modules/system_monitor/monitor.py

Reports live CPU / RAM / disk usage. Implements IModule so it plugs into
the Core Engine without core/ knowing anything about psutil.

FR satisfied: "User can see real-time CPU/RAM usage"
NFR satisfied: "System Monitor must report stats without freezing the UI"
    (v1.0: fast synchronous reads via psutil; no blocking work is done
    inside handle_event beyond a cheap syscall-backed snapshot)
"""

from __future__ import annotations
import psutil

from core.contracts import IModule, Event
from shared.logger import get_logger

logger = get_logger("aipos.system_monitor")


class SystemMonitorModule(IModule):
    @property
    def name(self) -> str:
        return "system_monitor"

    def subscriptions(self) -> list[str]:
        return ["REQUEST_SYSTEM_STATS"]

    def handle_event(self, event: Event) -> Event | None:
        if event.type != "REQUEST_SYSTEM_STATS":
            return None

        stats = self._read_stats()
        logger.info(f"Reported system stats: {stats}")

        return Event(
            type="SYSTEM_STATS_RESULT",
            payload=stats,
            source=self.name,
        )

    @staticmethod
    def _read_stats() -> dict:
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "ram_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
        }
