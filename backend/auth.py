from fastapi import Header, HTTPException
import jwt
from utils.json_store import read_json
import os
from config import settings

JWT_SECRET = settings.JWT_SECRET
JWT_ALGO = settings.JWT_ALGO


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")

    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    users = read_json("users.json")
    user = next((u for u in users if u["id"] == payload["user_id"]), None)

    if not user or not user["active"]:
        raise HTTPException(status_code=403, detail="User suspended or not found")

    return user