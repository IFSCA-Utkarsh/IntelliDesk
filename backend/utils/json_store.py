import json
import os
from lock import GLOBAL_LOCK

BASE_PATH = "storage"

def _path(name: str) -> str:
    return os.path.join(BASE_PATH, name)

def read_json(filename: str):
    with GLOBAL_LOCK:
        path = _path(filename)
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

def write_json(filename: str, data):
    with GLOBAL_LOCK:
        path = _path(filename)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)