import json
from llm.client import ollama_generate

MODEL = "ticket-model"


def run_ticket_llm(message: str) -> dict:
    """
    Calls the custom ticket-model.
    The model already contains its SYSTEM prompt.
    Always returns valid JSON.
    """

    try:
        raw = ollama_generate(
            model=MODEL,
            prompt=message
        )

        raw = raw.strip()
        return json.loads(raw)

    except Exception:
        # Absolute safety fallback — never crash chat flow
        return {
            "steps": [],
            "resolved": False
        }
