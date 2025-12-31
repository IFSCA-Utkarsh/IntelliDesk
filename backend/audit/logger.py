# backend/audit/logger.py

from datetime import datetime
import json
import os
from threading import Lock
from typing import Optional, Dict, Any

AUDIT_DIR = "backend/storage"
AUDIT_FILE = os.path.join(AUDIT_DIR, "audit.log")

_lock = Lock()


def log_event(
    *,
    request_id: str,
    actor_id: str,
    actor_role: str,        # user | admin | superuser | system
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    before: Optional[Dict[str, Any]] = None,
    after: Optional[Dict[str, Any]] = None,
):
    os.makedirs(AUDIT_DIR, exist_ok=True)

    record = {
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "request_id": request_id,
        "actor": {
            "id": actor_id,
            "role": actor_role,
        },
        "action": action,
        "entity": {
            "type": entity_type,
            "id": entity_id,
        },
        "before": before,
        "after": after,
    }

    line = json.dumps(record, separators=(",", ":"), sort_keys=True)

    with _lock:
        with open(AUDIT_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
