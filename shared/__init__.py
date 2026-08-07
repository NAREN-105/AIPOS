"""
shared/
Foundational utilities with zero risk of crashing the app or coupling
modules together. Imported directly everywhere (core/, modules/) —
does NOT go through the event bus (Task 3, section 3.8).
"""

from shared.logger import get_logger
from shared.config import Config

__all__ = ["get_logger", "Config"]
