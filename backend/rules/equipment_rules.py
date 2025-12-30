import random
import string
from datetime import datetime, timedelta

# ---------------------------
# SECRET GENERATION
# ---------------------------

def generate_secret_code(length=6):
    return ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=length)
    )

# ---------------------------
# TIME HELPERS
# ---------------------------

def utcnow():
    return datetime.utcnow()

def secret_expired(secret_expires_at: str) -> bool:
    return utcnow() > datetime.fromisoformat(secret_expires_at)

def request_expired(requested_at: str, ttl_minutes: int = 40) -> bool:
    return utcnow() > (
        datetime.fromisoformat(requested_at) + timedelta(minutes=ttl_minutes)
    )
