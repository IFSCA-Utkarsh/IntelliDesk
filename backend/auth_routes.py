from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
from utils.json_store import read_json
from config import settings

JWT_SECRET = settings.JWT_SECRET
JWT_ALGO = settings.JWT_ALGO
JWT_EXP_MINUTES = 720

router = APIRouter(prefix="/auth")

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(req: LoginRequest):
    users = read_json("users.json")

    user = next(
        (u for u in users
         if u["username"] == req.username
         and u["password"] == req.password),
        None
    )

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user["active"]:
        raise HTTPException(status_code=403, detail="User suspended")

    payload = {
        "user_id": user["id"],
        "role": user["role"],
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

    return {
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"]
        }
    }
