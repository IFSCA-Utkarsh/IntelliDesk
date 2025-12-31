import requests

OLLAMA_URL = "http://localhost:11434"

def ollama_generate(*, model: str, prompt: str = None, messages: list = None):
    if messages is not None:
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        url = f"{OLLAMA_URL}/api/chat"
    else:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        url = f"{OLLAMA_URL}/api/generate"

    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    if "message" in data:
        return data["message"]["content"]
    return data.get("response", "")
