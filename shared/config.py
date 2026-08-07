"""
shared/config.py

Minimal config manager for v1.0. Reads simple key=value settings from
config/settings.ini if present, otherwise falls back to sane defaults.
Kept intentionally small — v1.0 has no secrets/API keys to manage yet.
"""

from __future__ import annotations
import configparser
from pathlib import Path

_DEFAULTS = {
    "system_monitor": {"poll_interval_seconds": "2"},
    "ai_chat": {"mode": "rule_based"},
}

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "settings.ini"


class Config:
    def __init__(self, path: Path = _CONFIG_PATH):
        self._parser = configparser.ConfigParser()
        self._parser.read_dict(_DEFAULTS)
        if path.exists():
            self._parser.read(path)

    def get(self, section: str, key: str, fallback: str | None = None) -> str | None:
        return self._parser.get(section, key, fallback=fallback)

    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        return self._parser.getint(section, key, fallback=fallback)
