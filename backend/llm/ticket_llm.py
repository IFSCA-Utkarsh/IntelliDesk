import json
from jsonschema import validate, ValidationError
from llm.client import ollama_generate

TICKET_MODEL = "ticket-model"

TICKET_SCHEMA = {
    "type": "object",
    "required": ["steps", "resolved"],
    "additionalProperties": False,
    "properties": {
        "steps": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        },
        "resolved": {"type": "boolean"}
    }
}

def troubleshoot(issue: str) -> dict:
    raw = ollama_generate(
        model=TICKET_MODEL,
        prompt=issue
    )

    try:
        parsed = json.loads(raw)
        validate(parsed, TICKET_SCHEMA)
        return parsed
    except (json.JSONDecodeError, ValidationError):
        return {
            "steps": [
                "Please restart your system.",
                "If the issue persists, contact IT support."
            ],
            "resolved": False
        }