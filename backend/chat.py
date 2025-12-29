from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth import get_current_user
from llm.orchestrator import route_message
from llm.portal_llm import process_meeting

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat(req: ChatRequest, user=Depends(get_current_user)):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Empty message")

    decision = route_message(req.message)

    if decision["route"] == "portal":
        portal_response = process_meeting(req.message)
        return {
            "route": "portal",
            "response": portal_response
        }

    if decision["route"] == "ticket":
        return {
            "route": "ticket",
            "response": "Please create a ticket from the Tickets section."
        }

    return {
        "route": decision["route"],
    }
