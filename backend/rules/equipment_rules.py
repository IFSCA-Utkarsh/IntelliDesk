import random
import string
from datetime import datetime, timedelta

def generate_secret_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def is_late(return_by: str):
    today = datetime.utcnow().date()
    due = datetime.strptime(return_by, "%Y-%m-%d").date()
    return today > due
