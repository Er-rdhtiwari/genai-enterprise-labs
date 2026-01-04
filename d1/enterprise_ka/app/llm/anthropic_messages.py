import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.llm.base import LLMClient

class AnthropicMessagesClient(LLMClient):
    def __init__(self, api_key: str, model: str, base_url: str = "https://api.anthropic.com"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=0.5, max=4))
    async def generate(self, system: str, user: str) -> str:
        url = f"{self.base_url}/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 700,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            # Claude returns a list of content blocks
            return "".join(block.get("text", "") for block in data.get("content", []))
