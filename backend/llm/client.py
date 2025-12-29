import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def ollama_generate(model: str, prompt: str) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    if "response" not in data:
        raise ValueError("Invalid Ollama response")

    return data["response"]
