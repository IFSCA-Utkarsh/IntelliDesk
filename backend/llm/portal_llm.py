# backend/llm/portal_llm.py

import json
from llm.client import ollama_generate

MODEL = "portal-model"


def run_portal_llm(flow: dict) -> dict:
    """
    Portal Management LLM.
    Custom Ollama model with embedded SYSTEM prompt.
    """

    parts = []

    # Mandatory context (first)
    parts.append(f'intent: "{flow["type"]}"')
    parts.append(f'current_date: "{flow["current_date"]}"')

    # Conversation history
    for h in flow["history"]:
        role = h["role"].upper()
        parts.append(f"{role}: {h['content']}")

    prompt = "\n".join(parts)

    raw = ollama_generate(
        model=MODEL,
        prompt=prompt,
    ).strip()

    try:
        return json.loads(raw)
    except Exception:
        return {
            "status": "incomplete",
            "question": "Please repeat that clearly."
        }
