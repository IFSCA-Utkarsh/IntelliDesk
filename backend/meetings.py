from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from auth import get_current_user
from utils.json_store import read_json, write_json
from rules.meeting_rules import find_room
from audit import log_event
from automation.meeting_automation import handle_meeting_automation

router = APIRouter(prefix="/meetings")

# ---------------- MODELS ----------------

class MeetingCreate(BaseModel):
    title: str
    date: str          # DD/MM
    start_time: str    # HH:MM
    duration: str      # HH:MM
    participants: int
    type: str          # online | offline

# ---------------- CREATE MEETING ----------------

@router.post("")
def create_meeting(req: MeetingCreate, user=Depends(get_current_user)):
    meetings = read_json("meetings.json")

    # Apply deterministic business rules
    room = find_room(req.dict(), meetings)
    if not room:
        raise HTTPException(
            status_code=409,
            detail="No room or WebEx available. Please reschedule."
        )

    meeting_id = f"MTG-{uuid4().hex[:8]}"

    record = {
        "id": meeting_id,
        "title": req.title,
        "date": req.date,
        "start_time": req.start_time,
        "duration": req.duration,
        "participants": req.participants,
        "type": req.type,
        "room": room["name"],
        "webex": room["webex"] if req.type == "online" else None,
        "created_by": user["id"]
    }

    # 1️⃣ Persist meeting FIRST (never automate before save)
    meetings.append(record)
    write_json("meetings.json", meetings)

    log_event(user["id"], "MEETING_CREATED", meeting_id)

    # 2️⃣ Run automation (WebEx + Gmail)
    users = read_json("users.json")
    creator = next(u for u in users if u["id"] == user["id"])
    user_email = creator["email"]

    handle_meeting_automation(record, user_email)

    # 3️⃣ Persist WebEx fields added by automation
    write_json("meetings.json", meetings)

    return record

# ---------------- LIST MEETINGS ----------------

@router.get("")
def list_meetings(user=Depends(get_current_user)):
    meetings = read_json("meetings.json")

    if user["role"] in {"admin", "superuser"}:
        return meetings

    return [m for m in meetings if m["created_by"] == user["id"]]
