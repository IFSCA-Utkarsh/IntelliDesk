from fastapi import APIRouter, Depends, HTTPException, Response
from auth import get_current_user
from utils.json_store import read_json, write_json
from audit import log_event
import os

router = APIRouter(prefix="/admin")

# ---------------- ADMIN ----------------

@router.get("/overview")
def admin_overview(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    return {
        "meetings": read_json("meetings.json"),
        "tickets": read_json("tickets.json"),
        "equipment": read_json("equipment.json")
    }

# ---------------- SUPERUSER ----------------

@router.get("/all-data")
def all_data(user=Depends(get_current_user)):
    if user["role"] != "superuser":
        raise HTTPException(status_code=403, detail="Superuser only")

    return {
        "users": read_json("users.json"),
        "meetings": read_json("meetings.json"),
        "tickets": read_json("tickets.json"),
        "equipment": read_json("equipment.json")
    }

@router.post("/user/suspend/{user_id}")
def suspend_user(user_id: str, user=Depends(get_current_user)):
    if user["role"] != "superuser":
        raise HTTPException(status_code=403, detail="Superuser only")

    users = read_json("users.json")
    target = next((u for u in users if u["id"] == user_id), None)

    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    target["active"] = False
    write_json("users.json", users)

    log_event(user["id"], "USER_SUSPENDED", user_id)
    return {"status": "suspended"}

@router.post("/user/unsuspend/{user_id}")
def unsuspend_user(user_id: str, user=Depends(get_current_user)):
    if user["role"] != "superuser":
        raise HTTPException(status_code=403, detail="Superuser only")

    users = read_json("users.json")
    target = next((u for u in users if u["id"] == user_id), None)

    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    target["active"] = True
    write_json("users.json", users)

    log_event(user["id"], "USER_UNSUSPENDED", user_id)
    return {"status": "unsuspended"}

@router.get("/audit-log")
def get_audit_log(user=Depends(get_current_user)):
    if user["role"] != "superuser":
        raise HTTPException(status_code=403, detail="Superuser only")

    path = "backend/storage/audit.log"
    if not os.path.exists(path):
        return Response("", media_type="text/plain")

    with open(path, "r", encoding="utf-8") as f:
        return Response(f.read(), media_type="text/plain")
