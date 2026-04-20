"""Ollama adapter - handles Ollama-specific API differences."""

import json
from typing import AsyncGenerator, Optional

import httpx


class OllamaAdapter:
    """Adapter for Ollama API."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=120.0)

    async def chat(
        self,
        model: str,
        messages: list[dict],
        stream: bool = False,
        tools: Optional[list[dict]] = None,
    ) -> dict | AsyncGenerator[dict, None]:
        """Send chat request to Ollama."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }
        if tools:
            payload["tools"] = tools

        url = f"{self.base_url}/api/chat"

        if stream:
            return self._stream_response(url, payload)
        else:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

    async def _stream_response(
        self, url: str, payload: dict
    ) -> AsyncGenerator[dict, None]:
        """Handle streaming response from Ollama."""
        payload["stream"] = True
        async with self.client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue

    async def list_models(self) -> list[str]:
        """List available models."""
        url = f"{self.base_url}/api/tags"
        try:
            response = await self.client.get(url)
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []

    async def close(self) -> None:
        await self.client.aclose()


def transform_to_ollama(messages: list[dict]) -> list[dict]:
    """Transform OpenAI-format messages to Ollama format."""
    ollama_messages = []
    for msg in messages:
        ollama_msg = {
            "role": msg.get("role", "user"),
            "content": msg.get("content", ""),
        }
        # Handle tool calls - Ollama doesn't support them natively
        if msg.get("tool_calls"):
            # Convert to content
            tool_calls = msg["tool_calls"]
            ollama_msg["content"] += f"\n\nTool calls: {json.dumps(tool_calls)}"
        ollama_messages.append(ollama_msg)
    return ollama_messages


def transform_from_ollama(response: dict) -> dict:
    """Transform Ollama response to OpenAI format."""
    message = response.get("message", {})
    return {
        "id": f"chatcmpl-{response.get('created', 0)}",
        "object": "chat.completion",
        "created": response.get("created", 0),
        "model": response.get("model", ""),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": message.get("role", "assistant"),
                    "content": message.get("content", ""),
                },
                "finish_reason": response.get("done", False) and "stop" or None,
            }
        ],
        "usage": {
            "prompt_tokens": response.get("prompt_eval_count", 0),
            "completion_tokens": response.get("eval_count", 0),
            "total_tokens": response.get("prompt_eval_count", 0)
            + response.get("eval_count", 0),
        },
    }


# Known Ollama models
OLLAMA_MODELS = {
    "llama3.2": {"vision": False, "size": "3B"},
    "llama3.2:70b": {"vision": False, "size": "70B"},
    "llama3.2-vision": {"vision": True, "size": "7B"},
    "mistral": {"vision": False, "size": "7B"},
    "mixtral": {"vision": False, "size": "47B"},
    "llava": {"vision": True, "size": "7B"},
    "phi3": {"vision": False, "size": "3.8B"},
}


def is_ollama_model(model: str) -> bool:
    """Check if a model name looks like an Ollama model."""
    model_lower = model.lower()
    return any(
        m in model_lower for m in ["llama", "mistral", "mixtral", "llava", "phi"]
    )


def has_vision(model: str) -> bool:
    """Check if an Ollama model supports vision."""
    for name, info in OLLAMA_MODELS.items():
        if name in model.lower():
            return info.get("vision", False)
    return False
