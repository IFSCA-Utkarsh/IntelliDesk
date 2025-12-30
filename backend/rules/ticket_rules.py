from collections import defaultdict
from datetime import datetime
import uuid

from utils.json_store import read_json, write_json
from audit import log_event

# --------------------------------------------------
# ADMIN ASSIGNMENT (YOUR EXISTING LOGIC)
# --------------------------------------------------

def assign_admin(tickets, admins):
    counts = defaultdict(int)

    for t in tickets:
        if t.get("assigned_admin"):
            counts[t["assigned_admin"]] += 1

    admins_sorted = sorted(admins, key=lambda a: counts[a["id"]])
    return admins_sorted[0]["id"] if admins_sorted else None

# --------------------------------------------------
# PUBLIC API USED BY chat.py
# --------------------------------------------------

def create_ticket(user, issue: str):
    """
    Creates an IT ticket and assigns an admin.
    Called from chat.py when route == ticket
    """

    tickets = read_json("tickets.json")
    admins = read_json("users.json")

    admins = [u for u in admins if u.get("role") == "admin"]

    assigned_admin = assign_admin(tickets, admins)

    ticket = {
        "id": f"TCK-{uuid.uuid4().hex[:6]}",
        "issue": issue,
        "status": "open",
        "created_by": user["id"],
        "assigned_admin": assigned_admin,
        "created_at": datetime.utcnow().isoformat()
    }

    tickets.append(ticket)
    write_json("tickets.json", tickets)

    log_event(user["id"], "TICKET_CREATED", ticket["id"])

    return ticket
