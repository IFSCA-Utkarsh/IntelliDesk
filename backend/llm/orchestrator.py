import json
from jsonschema import validate, ValidationError
from llm.client import ollama_generate

# -------------------------------------------------
# MODEL
# -------------------------------------------------

ORCHESTRATOR_MODEL = "orchestrator-model"

# -------------------------------------------------
# SCHEMA
# -------------------------------------------------

ORCHESTRATOR_SCHEMA = {
    "type": "object",
    "required": ["route", "confidence"],
    "additionalProperties": False,
    "properties": {
        "route": {
            "type": "string",
            "enum": ["portal", "equipment", "ticket", "reply", "fallback"]
        },
        "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
        }
    }
}

CONFIDENCE_THRESHOLD = 0.6

# -------------------------------------------------
# HARD OVERRIDES (AUTHORITATIVE)
# -------------------------------------------------

def hard_route_override(message: str):
    msg = message.lower().strip()

    # ---- greetings ----
    if msg in {"hi", "hello", "hey", "good morning", "good evening"}:
        return {"route": "reply", "confidence": 1.0}

    # ---- meetings ----
    if any(k in msg for k in [
        "meeting",
        "meeting room",
        "book meeting",
        "schedule meeting",
        "reserve room",
        "conference room",
        "reschedule meeting",
        "cancel meeting"
    ]):
        return {"route": "portal", "confidence": 1.0}

    # ---- equipment ----
    if any(k in msg for k in [
        "laptop",
        "monitor",
        "keyboard",
        "mouse",
        "equipment",
        "return laptop",
        "return equipment",
        "need laptop",
        "assign laptop"
    ]):
        return {"route": "equipment", "confidence": 1.0}

    # ---- tickets ----
    if any(k in msg for k in [
        "not working",
        "issue",
        "problem",
        "error",
        "wifi",
        "network",
        "slow",
        "crash",
        "failed",
        "system issue",
        "system issues"
    ]):
        return {"route": "ticket", "confidence": 1.0}

    return None

# -------------------------------------------------
# LLM ROUTING (SECONDARY)
# -------------------------------------------------

def llm_route(message: str) -> dict:
    prompt = f"""
You are a STRICT intent router for IntelliDesk.

Jobs:
- portal → meeting scheduling / room booking
- equipment → physical equipment requests or returns
- ticket → technical problems or system issues
- reply → greetings or small talk
- fallback → unclear intent

Return ONLY valid JSON.

Schema:
{json.dumps(ORCHESTRATOR_SCHEMA, indent=2)}

User message:
{message}
"""

    raw = ollama_generate(
        model=ORCHESTRATOR_MODEL,
        prompt=prompt
    )

    try:
        parsed = json.loads(raw)
        validate(parsed, ORCHESTRATOR_SCHEMA)
        return parsed
    except (json.JSONDecodeError, ValidationError):
        return {"route": "fallback", "confidence": 0.0}

# -------------------------------------------------
# PUBLIC API
# -------------------------------------------------

def route_message(message: str) -> dict:
    """
    Routing priority:
    1. Hard deterministic rules (authoritative)
    2. LLM semantic routing
    3. Confidence gate
    """

    # 1️⃣ Hard override (NO LLM)
    override = hard_route_override(message)
    if override:
        return override

    # 2️⃣ LLM routing
    result = llm_route(message)

    # 3️⃣ Confidence gate
    if result["confidence"] < CONFIDENCE_THRESHOLD:
        return {"route": "fallback", "confidence": result["confidence"]}

    return result
