# backend/llm/orchestrator_llm.py

import json
from llm.client import ollama_generate

MODEL = "orchestrator-model"


def run_orchestrator(message: str) -> dict:
    """
    Intent router using CUSTOM Ollama model.
    Model already contains SYSTEM prompt.
    """

    raw = ollama_generate(
        model=MODEL,
        prompt=message,
    ).strip()

    try:
        parsed = json.loads(raw)
        return {
            "route": parsed["route"],
            "confidence": float(parsed["confidence"]),
        }
    except Exception:
        return {
            "route": "greeting_reply",
            "confidence": 0.0,
        }
