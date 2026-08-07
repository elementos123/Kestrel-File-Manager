import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path.home() / ".kestrel" / "logs"
LOG_FILE = LOG_DIR / "kestrel.log"

_configured = False


def _configure_root():
    global _configured
    if _configured:
        return
    _configured = True

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger("kestrel")
    root.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
    ))
    root.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
    root.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    _configure_root()
    return logging.getLogger(f"kestrel.{name}")
