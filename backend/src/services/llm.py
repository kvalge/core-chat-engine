"""LLM API client service - hand-rolled without SDKs."""

import json
import os
from typing import AsyncGenerator, Optional

import httpx


class LLMClient:
    """Hand-rolled OpenAI-compatible API client."""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """Initialize the client."""
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.client = httpx.AsyncClient(timeout=120.0)

    async def chat_completion(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
        tools: Optional[list[dict]] = None,
    ) -> dict | AsyncGenerator[dict, None]:
        """Send chat completion request."""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        if tools:
            payload["tools"] = tools

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        if stream:
            return self._stream_response(url, headers, payload)
        else:
            response = await self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    async def _stream_response(
        self, url: str, headers: dict, payload: dict
    ) -> AsyncGenerator[dict, None]:
        """Handle streaming response."""
        payload["stream"] = True
        async with self.client.stream(
            "POST", url, json=payload, headers=headers
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        continue

    async def list_models(self) -> list[str]:
        """List available models."""
        url = f"{self.base_url}/models"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = await self.client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return [m["id"] for m in data.get("data", [])]
        return []

    async def close(self) -> None:
        """Close the client."""
        await self.client.aclose()


def create_client(base_url: str, api_key: Optional[str] = None) -> LLMClient:
    """Factory function to create LLM client."""
    return LLMClient(base_url, api_key)


# Vision-capable models ( Ollama )
VISION_MODELS = {"llama3.2-vision", "llama3.2", "llava"}


def is_vision_model(model: str) -> bool:
    """Check if a model supports vision."""
    model_lower = model.lower()
    return any(vm in model_lower for vm in VISION_MODELS)
