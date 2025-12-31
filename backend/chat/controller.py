from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime

from auth import get_current_user
from chat.state_manager import (
    get_active_flows,
    create_flow,
    delete_flow,
    append_history,
    update_flow_data,
)
from chat.flow_router import route_new_message
from audit.logger import log_event

router = APIRouter(prefix="/api")


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
def chat(req: ChatRequest, request: Request, user=Depends(get_current_user)):
    message = (req.message or "").strip()
    if not message:
        raise HTTPException(
            status_code=400,
            detail="message is required"
        )

    request_id = f"req-{uuid4().hex[:8]}"
    user_id = user["id"]

    # 1️⃣ Check active flows (multiple allowed)
    flows = get_active_flows(user_id)

    if flows:
        # Pick the most recent active flow
        flow = flows[-1]

        append_history(flow["flow_id"], "user", message)

        response = route_new_message(flow, request_id)

        return response

    # 2️⃣ No active flow → run orchestrator ONCE
    flow = create_flow(user_id, message, request_id)

    if flow is None:
        # Greeting / low confidence
        return {
            "flow_id": None,
            "type": "greeting",
            "step": None,
            "response": "Hello 👋 How can I help you today?",
            "summary": None,
        }

    append_history(flow["flow_id"], "user", message)

    response = route_new_message(flow, request_id)
    return response