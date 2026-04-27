import os
import requests
from dotenv import load_dotenv

load_dotenv()

# ── Model Configuration ───────────────────────────────────────────────────────
# Swap to any model slug from https://openrouter.ai/models
# Examples:
#   "mistralai/mistral-7b-instruct"       ← fast, free-tier friendly (default)
#   "openai/gpt-4o-mini"                  ← stronger, low cost
#   "meta-llama/llama-3-8b-instruct"      ← open-weight alternative
MODEL = "openrouter/free"
_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def call_llm(messages: list[dict], temperature: float = 0.3) -> str:
    """
    Send a messages list to OpenRouter and return the assistant's text reply.
    Raises on HTTP errors or missing API key.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your_key_here":
        raise EnvironmentError(
            "OPENROUTER_API_KEY is not set. Paste your key into .env"
        )

    response = requests.post(
        _API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "Moodwave",
        },
        json={
            "model": MODEL,
            "messages": messages,
            "temperature": temperature,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
