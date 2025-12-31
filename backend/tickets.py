from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from auth import get_current_user
from utils.json_store import read_json, write_json
from audit import log_event
from llm.ticket_llm import troubleshoot
from rules.ticket_rules import assign_admin

router = APIRouter(prefix="/tickets")

# ---------------- MODELS ----------------

class TicketCreate(BaseModel):
    issue: str

class TicketReply(BaseModel):
    ticket_id: str
    message: str

# ---------------- USER ----------------

@router.post("")
def create_ticket(req: TicketCreate, user=Depends(get_current_user)):
    tickets = read_json("tickets.json")

    ticket_id = f"TCK-{uuid4().hex[:8]}"
    record = {
        "id": ticket_id,
        "issue": req.issue,
        "status": "open",
        "created_by": user["id"],
        "attempts": 0,
        "assigned_admin": None,
        "history": []
    }

    tickets.append(record)
    write_json("tickets.json", tickets)

    log_event(user["id"], "TICKET_CREATED", ticket_id)

    return record

@router.post("/ai")
def ai_troubleshoot(req: TicketReply, user=Depends(get_current_user)):
    tickets = read_json("tickets.json")

    ticket = next((t for t in tickets if t["id"] == req.ticket_id), None)
    if not ticket or ticket["created_by"] != user["id"]:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket["attempts"] >= 2:
        raise HTTPException(status_code=409, detail="AI attempts exhausted")

    result = troubleshoot(ticket["issue"])
    ticket["attempts"] += 1
    ticket["history"].append({"ai": result})

    if result["resolved"]:
        ticket["status"] = "resolved"

    write_json("tickets.json", tickets)
    log_event(user["id"], "TICKET_AI_ATTEMPT", ticket["id"])

    return result

# ---------------- ESCALATION ----------------

@router.post("/escalate/{ticket_id}")
def escalate(ticket_id: str, user=Depends(get_current_user)):
    tickets = read_json("tickets.json")
    users = read_json("users.json")

    ticket = next((t for t in tickets if t["id"] == ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    admins = [u for u in users if u["role"] == "admin" and u["active"]]
    admin_id = assign_admin(tickets, admins)

    if not admin_id:
        raise HTTPException(status_code=503, detail="No admin available")

    ticket["assigned_admin"] = admin_id
    ticket["status"] = "escalated"

    write_json("tickets.json", tickets)
    log_event(user["id"], "TICKET_ESCALATED", ticket_id)

    return {"assigned_admin": admin_id}

# ---------------- ADMIN ----------------

@router.get("")
def list_tickets(user=Depends(get_current_user)):
    tickets = read_json("tickets.json")

    if user["role"] == "admin":
        return [t for t in tickets if t["assigned_admin"] == user["id"]]

    if user["role"] == "superuser":
        return tickets

    return [t for t in tickets if t["created_by"] == user["id"]]

@router.post("/close/{ticket_id}")
def close_ticket(ticket_id: str, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    tickets = read_json("tickets.json")
    users = read_json("users.json")

    ticket = next((t for t in tickets if t["id"] == ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket["status"] = "closed"

    # Suspend user
    ticket_owner = next(u for u in users if u["id"] == ticket["created_by"])
    ticket_owner["active"] = False

    write_json("tickets.json", tickets)
    write_json("users.json", users)

    log_event(user["id"], "TICKET_CLOSED_AND_USER_SUSPENDED", ticket_id)

    return {"status": "closed", "user_suspended": True}

def run_ticket_llm(flow: dict) -> dict:
    """
    Temporary stub for ticket LLM.
    Will be replaced with full troubleshooting logic.
    """

    return {
        "steps": [
            "Please restart your system and try again."
        ],
        "resolved": False
    }