"""Track recently opened files (not folders)."""

import json
import os
from pathlib import Path

_FILE = str(Path.home() / ".file_explorer_recent_files.json")
_MAX  = 30


def load_recent_files() -> list[str]:
    try:
        with open(_FILE, "r", encoding="utf-8") as f:
            return [p for p in json.load(f) if os.path.isfile(p)][:_MAX]
    except Exception:
        return []


def push_recent_file(path: str) -> None:
    if not os.path.isfile(path):
        return
    entries = load_recent_files()
    if path in entries:
        entries.remove(path)
    entries.insert(0, path)
    try:
        with open(_FILE, "w", encoding="utf-8") as f:
            json.dump(entries[:_MAX], f, indent=2)
    except Exception:
        pass


def clear_recent_files() -> None:
    try:
        with open(_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    except Exception:
        pass
