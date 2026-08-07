"""
shared/logger.py

A single, simple logger used by every layer (core/, shared/, modules/).
Deliberately NOT event-driven — logging a line is low-risk and would
gain nothing from going through the bus (see Task 3, 3.8).
"""

import logging
import sys
from pathlib import Path

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOG_FILE = _LOG_DIR / "aipos.log"
_configured = False


def get_logger(name: str = "aipos") -> logging.Logger:
    global _configured
    logger = logging.getLogger(name)

    if not _configured:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        root = logging.getLogger("aipos")
        root.setLevel(logging.INFO)
        root.addHandler(file_handler)
        root.addHandler(console_handler)
        root.propagate = False

        _configured = True

    return logger
