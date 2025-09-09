import os, json, requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TIMEOUT = 120

class ChatCompletionsClient:
    """Minimal Chat Completions API client (OpenAI互換)"""
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def complete(self, prompt: str, expect_json: bool = True) -> str:
        url = f"{OPENAI_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        system = "You are a careful assistant. Respond in strict JSON if asked."
        user = f"Return ONLY valid JSON. No commentary. Prompt:\n{prompt}" if expect_json else prompt
        body = {
            "model": self.model,
            "messages": [{"role":"system","content":system},{"role":"user","content":user}],
        }
        # Some models don't support custom temperature
        if not self.model.startswith("gpt-5"):
            body["temperature"] = 0.2
        r = requests.post(url, headers=headers, json=body, timeout=TIMEOUT)
        if r.status_code == 429:
            print("429 body:", r.text)
            print("rate headers:", {k:v for k,v in r.headers.items() if k.lower().startswith("x-ratelimit")})
        elif r.status_code == 400:
            print("400 body:", r.text)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]
