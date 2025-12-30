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
    prompt = f"""
You are an IT support assistant.

Your task:
- Provide step-by-step troubleshooting advice
- Mark resolved = true ONLY if the issue is fully solved

Return ONLY valid JSON.
No text. No explanation. No markdown.

JSON schema:
{json.dumps(TICKET_SCHEMA, indent=2)}

User issue:
{issue}
"""

    raw = ollama_generate(
        model=TICKET_MODEL,
        prompt=prompt
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
