"""Recent folders history manager."""

import os
import json
from pathlib import Path

RECENT_FILE = str(Path.home() / ".file_explorer_recent.json")
MAX_RECENT  = 24


def load_recent() -> list[str]:
    try:
        with open(RECENT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [p for p in data if os.path.isdir(p)][:MAX_RECENT]
    except Exception:
        return []


def push_recent(path: str) -> list[str]:
    recent = load_recent()
    path   = os.path.normpath(path)
    if path in recent:
        recent.remove(path)
    recent.insert(0, path)
    recent = recent[:MAX_RECENT]
    try:
        with open(RECENT_FILE, "w", encoding="utf-8") as f:
            json.dump(recent, f, indent=2)
    except Exception:
        pass
    return recent


def clear_recent():
    try:
        with open(RECENT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    except Exception:
        pass
