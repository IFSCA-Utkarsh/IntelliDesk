import json
from jsonschema import validate, ValidationError
from llm.client import ollama_generate

PORTAL_MODEL = "portal-model"

PORTAL_SCHEMA_COMPLETE = {
    "type": "object",
    "required": ["status", "meeting"],
    "additionalProperties": False,
    "properties": {
        "status": {"type": "string", "enum": ["complete"]},
        "meeting": {
            "type": "object",
            "required": [
                "title",
                "date",
                "start_time",
                "duration",
                "participants",
                "type"
            ],
            "additionalProperties": False,
            "properties": {
                "title": {"type": "string"},
                "date": {"type": "string"},
                "start_time": {"type": "string"},
                "duration": {"type": "string"},
                "participants": {"type": "integer", "minimum": 1},
                "type": {"type": "string", "enum": ["online", "offline"]}
            }
        }
    }
}

PORTAL_SCHEMA_INCOMPLETE = {
    "type": "object",
    "required": ["status", "missing", "question"],
    "additionalProperties": False,
    "properties": {
        "status": {"type": "string", "enum": ["incomplete"]},
        "missing": {"type": "string"},
        "question": {"type": "string"}
    }
}

def process_meeting(message: str) -> dict:
    raw = ollama_generate(
        model=PORTAL_MODEL,
        prompt=message
    )

    try:
        parsed = json.loads(raw)

        if parsed.get("status") == "complete":
            validate(parsed, PORTAL_SCHEMA_COMPLETE)
            return parsed

        if parsed.get("status") == "incomplete":
            validate(parsed, PORTAL_SCHEMA_INCOMPLETE)
            return parsed

    except (json.JSONDecodeError, ValidationError):
        pass

    # HARD FAIL SAFE
    return {
        "status": "incomplete",
        "missing": "details",
        "question": "Could you please provide the meeting details again?"
    }
