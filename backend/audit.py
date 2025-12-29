from datetime import datetime
from lock import GLOBAL_LOCK


AUDIT_FILE = "backend/storage/audit.log"

def log_event(actor_id: str, action: str, details: str):
    with GLOBAL_LOCK:
        with open(AUDIT_FILE, "a", encoding="utf-8") as f:
            ts = datetime.utcnow().isoformat()
            f.write(f"{ts} | {actor_id} | {action} | {details}\n")