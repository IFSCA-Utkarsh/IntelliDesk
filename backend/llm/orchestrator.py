import json
from jsonschema import validate, ValidationError
from llm.client import ollama_generate

ORCHESTRATOR_MODEL = "orchestrator-model"

ORCHESTRATOR_SCHEMA = {
    "type": "object",
    "required": ["route", "confidence"],
    "additionalProperties": False,
    "properties": {
        "route": {
            "type": "string",
            "enum": ["portal", "ticket", "reply", "split", "fallback"]
        },
    }
}

CONFIDENCE_THRESHOLD = 0.6

def route_message(message: str) -> dict:
    raw = ollama_generate(
        model=ORCHESTRATOR_MODEL,
        prompt=message
    )

    try:
        parsed = json.loads(raw)
        validate(parsed, ORCHESTRATOR_SCHEMA)
    except (json.JSONDecodeError, ValidationError):
        return {"route": "fallback"}

    if parsed["confidence"] < CONFIDENCE_THRESHOLD:
        return {"route": "fallback"}

    return parsed
