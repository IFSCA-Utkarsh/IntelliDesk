from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from auth import get_current_user
from utils.json_store import read_json, write_json
from audit import log_event
from rules.equipment_rules import generate_secret_code, is_late
from automation.equipment_automation import send_equipment_submission_reminder

router = APIRouter(prefix="/equipment")

# ---------------- MODELS ----------------

class EquipmentRequest(BaseModel):
    meeting_id: str
    name: str
    return_by: str  # YYYY-MM-DD

class EquipmentApprove(BaseModel):
    equipment_id: str
    secret_code: str

class EquipmentReturn(BaseModel):
    equipment_id: str

# ---------------- USER ----------------

@router.post("/request")
def request_equipment(req: EquipmentRequest, user=Depends(get_current_user)):
    equipment = read_json("equipment.json")

    equipment_id = f"EQ-{uuid4().hex[:6]}"
    secret = generate_secret_code()

    record = {
        "equipment_id": equipment_id,
        "name": req.name,
        "status": "pending",
        "meeting_id": req.meeting_id,
        "assigned_to": user["id"],
        "return_by": req.return_by,
        "secret_code": secret
    }

    # 1️⃣ Persist request
    equipment.append(record)
    write_json("equipment.json", equipment)

    log_event(user["id"], "EQUIPMENT_REQUESTED", equipment_id)

    # 2️⃣ Send submission reminder email
    user_email = user["email"]
    send_equipment_submission_reminder(user_email, record)

    return {
        "equipment_id": equipment_id,
        "status": "pending",
        "secret_code": secret
    }

@router.post("/return")
def return_equipment(req: EquipmentReturn, user=Depends(get_current_user)):
    equipment = read_json("equipment.json")

    item = next(
        (e for e in equipment
         if e["equipment_id"] == req.equipment_id
         and e["assigned_to"] == user["id"]
         and e["status"] == "assigned"),
        None
    )

    if not item:
        raise HTTPException(status_code=404, detail="Equipment not found or not assigned")

    item["status"] = "returned"
    item["returned_at"] = datetime.utcnow().isoformat()

    write_json("equipment.json", equipment)
    log_event(user["id"], "EQUIPMENT_RETURNED", req.equipment_id)

    return {"status": "returned"}

# ---------------- ADMIN ----------------

@router.get("/pending")
def pending_requests(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    equipment = read_json("equipment.json")
    return [e for e in equipment if e["status"] == "pending"]

@router.post("/approve")
def approve_equipment(req: EquipmentApprove, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    equipment = read_json("equipment.json")

    item = next(
        (e for e in equipment
         if e["equipment_id"] == req.equipment_id
         and e["status"] == "pending"),
        None
    )

    if not item:
        raise HTTPException(status_code=404, detail="Pending equipment not found")

    if item["secret_code"] != req.secret_code:
        raise HTTPException(status_code=401, detail="Invalid secret code")

    item["status"] = "assigned"
    item["approved_by"] = user["id"]
    item["approved_at"] = datetime.utcnow().isoformat()

    write_json("equipment.json", equipment)
    log_event(user["id"], "EQUIPMENT_APPROVED", req.equipment_id)

    return {"status": "assigned"}

@router.post("/verify-return/{equipment_id}")
def verify_return(equipment_id: str, user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    equipment = read_json("equipment.json")

    item = next(
        (e for e in equipment
         if e["equipment_id"] == equipment_id
         and e["status"] == "returned"),
        None
    )

    if not item:
        raise HTTPException(status_code=404, detail="Returned equipment not found")

    late = is_late(item["return_by"])

    item["status"] = "available"
    item["verified_by"] = user["id"]

    write_json("equipment.json", equipment)

    log_event(
        user["id"],
        "EQUIPMENT_LATE_RETURN" if late else "EQUIPMENT_RETURN_VERIFIED",
        equipment_id
    )

    return {
        "status": "available",
        "late": late
    }


# ---------------- LIST EQUIPMENT ----------------

@router.get("")
def list_equipment(user=Depends(get_current_user)):
    equipment = read_json("equipment.json")

    # Admin & Superuser can see everything
    if user["role"] in {"admin", "superuser"}:
        return equipment

    # Normal users only see their own equipment
    return [
        e for e in equipment
        if e.get("assigned_to") == user["id"]
    ]
