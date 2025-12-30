from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from auth import get_current_user
from utils.json_store import read_json, write_json
from audit import log_event
from rules.equipment_rules import secret_expired, request_expired

router = APIRouter(prefix="/equipment")

# ----------------------------------------
# ADMIN APPROVE USING SECRET CODE ONLY
# ----------------------------------------

@router.post("/approve")
def approve_equipment_by_secret(
    payload: dict,
    user=Depends(get_current_user)
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    secret_code = payload.get("secret_code")
    if not secret_code:
        raise HTTPException(status_code=400, detail="Secret code required")

    equipment = read_json("equipment.json")
    now = datetime.utcnow()

    # 🔍 Find matching pending request
    item = next(
        (
            e for e in equipment
            if e.get("status") == "pending_approval"
            and e.get("secret_code") == secret_code
        ),
        None
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="No pending equipment found for this secret"
        )

    # ⏱️ Hard expiry (40 min)
    if request_expired(item["requested_at"]):
        item.update({
            "status": "available",
            "requested_by": None,
            "secret_code": None,
            "secret_expires_at": None,
            "requested_at": None
        })

        write_json("equipment.json", equipment)

        raise HTTPException(
            status_code=410,
            detail="Request expired"
        )

    # ⏳ Secret expiry (20 min)
    if secret_expired(item["secret_expires_at"]):
        raise HTTPException(
            status_code=410,
            detail="Secret expired"
        )

    # ✅ APPROVE & ASSIGN
    item.update({
        "status": "assigned",
        "assigned_to": item["requested_by"],
        "approved_by": user["id"],
        "approved_at": now.isoformat(),
        "secret_code": None,
        "secret_expires_at": None
    })

    write_json("equipment.json", equipment)

    log_event(
        user["id"],
        "EQUIPMENT_APPROVED",
        item["equipment_id"]
    )

    return {
        "status": "assigned",
        "equipment_id": item["equipment_id"],
        "assigned_to": item["assigned_to"]
    }
