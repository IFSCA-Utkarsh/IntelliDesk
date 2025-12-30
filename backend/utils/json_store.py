import json
import os
from lock import GLOBAL_LOCK

BASE_PATH = "storage"

def _path(name: str) -> str:
    return os.path.join(BASE_PATH, name)


def _default_for(filename: str):
    """
    Return correct default structure based on file type.
    """
    if filename.endswith(".json"):
        if filename in ("chat_memory.json",):
            return {}
        return []
    return {}


def read_json(filename: str):
    """
    Thread-safe, crash-proof JSON reader.
    - Handles missing file
    - Handles empty file
    - Handles corrupted JSON
    - Returns correct default type
    """
    with GLOBAL_LOCK:
        path = _path(filename)

        if not os.path.exists(path):
            return _default_for(filename)

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return _default_for(filename)
                return json.loads(content)
        except (json.JSONDecodeError, OSError):
            return _default_for(filename)


def write_json(filename: str, data):
    """
    Thread-safe, atomic JSON writer.
    """
    with GLOBAL_LOCK:
        path = _path(filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        os.replace(tmp, path)
