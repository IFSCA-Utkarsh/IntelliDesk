from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import re

# ================= AUTH =================
from auth import get_current_user

# ================= LLM =================
from llm.orchestrator import route_message
from llm.portal_llm import process_meeting

# ================= RULES =================
from rules.meeting_rules import create_meeting
from rules.ticket_rules import create_ticket

# ================= STORAGE =================
from utils.json_store import read_json, write_json

router = APIRouter()

# =====================================================
# CONSTANTS
# =====================================================

MEMORY_FILE = "chat_memory.json"
PENDING_FILE = "pending_actions.json"

MAX_HISTORY = 10
LLM_CONTEXT_LIMIT = 6
PENDING_TTL_MIN = 10

# =====================================================
# REQUEST MODEL
# =====================================================

class ChatRequest(BaseModel):
    message: str

# =====================================================
# SAFETY HELPERS
# =====================================================

def _safe_dict(val):
    return val if isinstance(val, dict) else {}

# =====================================================
# CHAT MEMORY (BACKWARD SAFE)
# =====================================================

def load_memory() -> dict:
    return _safe_dict(read_json(MEMORY_FILE))


def save_memory(user_id: str, role: str, content: str):
    memory = load_memory()
    history = memory.get(user_id, [])

    normalized = []
    for h in history:
        if isinstance(h, dict) and "role" in h and "content" in h:
            normalized.append(h)

    normalized.append({
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow().isoformat()
    })

    memory[user_id] = normalized[-MAX_HISTORY:]
    write_json(MEMORY_FILE, memory)


def get_context(user_id: str) -> str:
    memory = load_memory()
    history = memory.get(user_id, [])

    lines = []
    for h in history[-LLM_CONTEXT_LIMIT:]:
        if not isinstance(h, dict):
            continue
        role = h.get("role")
        content = h.get("content")
        if not role or not content:
            continue

        prefix = "User" if role == "user" else "Assistant"
        lines.append(f"{prefix}: {content}")

    return "\n".join(lines)

# =====================================================
# PENDING ACTIONS (STATE MACHINE)
# =====================================================

def load_pending_all() -> dict:
    return _safe_dict(read_json(PENDING_FILE))


def save_pending(user_id: str, data: dict):
    pending = load_pending_all()
    pending[user_id] = {
        "data": data,
        "ts": datetime.utcnow().isoformat()
    }
    write_json(PENDING_FILE, pending)


def clear_pending(user_id: str):
    pending = load_pending_all()
    pending.pop(user_id, None)
    write_json(PENDING_FILE, pending)


def load_pending(user_id: str):
    pending = load_pending_all()
    entry = pending.get(user_id)

    if not entry:
        return None

    try:
        created = datetime.fromisoformat(entry["ts"])
    except Exception:
        clear_pending(user_id)
        return None

    if datetime.utcnow() - created > timedelta(minutes=PENDING_TTL_MIN):
        clear_pending(user_id)
        return None

    return entry.get("data")

# =====================================================
# TIME EXTRACTION (11am, 2 baje, etc.)
# =====================================================

def extract_time(text: str):
    match = re.search(r"(\d{1,2})(?:\:(\d{2}))?\s*(am|pm)?", text.lower())
    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    mer = match.group(3)

    if mer == "pm" and hour < 12:
        hour += 12
    if mer == "am" and hour == 12:
        hour = 0

    return f"{hour:02d}:{minute:02d}"

# =====================================================
# CHAT ENDPOINT
# =====================================================

@router.post("/chat")
def chat(req: ChatRequest, user=Depends(get_current_user)):
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Empty message")

    save_memory(user["id"], "user", message)
    lower = message.lower()

    pending = load_pending(user["id"])

    # =================================================
    # CONTINUE INCOMPLETE MEETING FLOW
    # =================================================
    if pending and pending.get("type") == "meeting_incomplete":
        context = get_context(user["id"])
        result = process_meeting(message=message, context=context)

        if result["status"] == "incomplete":
            save_memory(user["id"], "assistant", result["question"])
            return {"route": "portal", "response": result["question"]}

        try:
            meeting = create_meeting(user, result["meeting"])
            clear_pending(user["id"])

            response = f"📅 Meeting booked at {meeting['start_time']}"
            save_memory(user["id"], "assistant", response)
            return {"route": "portal", "response": response}

        except ValueError as e:
            payload = e.args[0]
            if isinstance(payload, dict) and "suggestions" in payload:
                save_pending(user["id"], {
                    "type": "meeting_slot",
                    "meeting": result["meeting"],
                    "suggestions": payload["suggestions"]
                })

                response = (
                    "❌ No room available.\n"
                    "🕒 Suggested slots:\n" +
                    "\n".join(f"- {s['start_time']}" for s in payload["suggestions"])
                )
                save_memory(user["id"], "assistant", response)
                return {"route": "portal", "response": response}

    # =================================================
    # CONFIRM SLOT (yes, book 11am)
    # =================================================
    if pending and pending.get("type") == "meeting_slot":
        chosen_time = extract_time(lower)

        if chosen_time and any(
            s.get("start_time") == chosen_time for s in pending.get("suggestions", [])
        ):
            meeting_data = pending["meeting"].copy()
            meeting_data["start_time"] = chosen_time

            meeting = create_meeting(user, meeting_data)
            clear_pending(user["id"])

            response = f"✅ Meeting booked at {chosen_time}"
            save_memory(user["id"], "assistant", response)
            return {"route": "portal", "response": response}

        response = "Please choose one of the suggested time slots."
        save_memory(user["id"], "assistant", response)
        return {"route": "portal", "response": response}

    # =================================================
    # NORMAL ROUTING
    # =================================================
    decision = route_message(message)
    route = decision.get("route")
    context = get_context(user["id"])

    # ---------------- MEETING ----------------
    if route == "portal":
        result = process_meeting(message=message, context=context)

        if result["status"] == "incomplete":
            save_pending(user["id"], {
                "type": "meeting_incomplete",
                "missing": result["missing"]
            })
            save_memory(user["id"], "assistant", result["question"])
            return {"route": "portal", "response": result["question"]}

        try:
            meeting = create_meeting(user, result["meeting"])
            response = (
                f"📅 Meeting booked successfully\n"
                f"🏢 Room: {meeting['room']}\n"
                f"🕒 Time: {meeting['start_time']}"
            )
            save_memory(user["id"], "assistant", response)
            return {"route": "portal", "response": response}

        except ValueError as e:
            payload = e.args[0]
            if isinstance(payload, dict) and "suggestions" in payload:
                save_pending(user["id"], {
                    "type": "meeting_slot",
                    "meeting": result["meeting"],
                    "suggestions": payload["suggestions"]
                })

                response = (
                    "❌ No room available.\n"
                    "🕒 Suggested slots:\n" +
                    "\n".join(f"- {s['start_time']}" for s in payload["suggestions"])
                )

                save_memory(user["id"], "assistant", response)
                return {"route": "portal", "response": response}

            raise

    # ---------------- TICKET ----------------
    if route == "ticket":
        ticket = create_ticket(user, message)
        response = f"🎫 Ticket {ticket['id']} raised successfully."
        save_memory(user["id"], "assistant", response)
        return {"route": "ticket", "response": response}

    # ---------------- DEFAULT ----------------
    response = "Hello 👋 How can I help you today?"
    save_memory(user["id"], "assistant", response)
    return {"route": "reply", "response": response}

# =====================================================
# CHAT HISTORY
# =====================================================

@router.get("/chat/history")
def chat_history(user=Depends(get_current_user)):
    memory = load_memory()
    return {"history": memory.get(user["id"], [])[-5:]}