"""Chat API routes."""

import json
import time
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from ..models.schemas import (
    ChatCompletionRequest,
    ChatCompletion,
    ChatMessage,
)
from ..services.llm import create_client, is_vision_model
from ..services.streaming import SSEHandler

router = APIRouter()


def generate_id() -> str:
    """Generate completion ID."""
    return f"chatcmpl-{uuid.uuid().hex[:8]}"


def get_default_client() -> tuple:
    """Get default LLM client configuration."""
    import os

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    return base_url, "", model


@router.post("/completions")
async def chat_completions(request: ChatCompletionRequest) -> ChatCompletion:
    """OpenAI-compatible /v1/chat/completions endpoint."""
    base_url, api_key, default_model = get_default_client()
    model = request.model or default_model
    messages = [msg.model_dump() for msg in request.messages]

    client = create_client(base_url, api_key)
    try:
        response = await client.chat_completion(
            model=model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=False,
            tools=request.tools,
        )
        return ChatCompletion(
            id=response.get("id", generate_id()),
            created=response.get("created", int(time.time())),
            model=model,
            choices=[
                ChatChoice(
                    index=0,
                    message=ChatMessage(
                        role=c["message"].get("role", "assistant"),
                        content=c["message"].get("content", ""),
                    ),
                    finish_reason=c.get("finish_reason", "stop"),
                )
                for c in response.get("choices", [])
            ],
            usage=response.get(
                "usage",
                {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.aclose()


@router.post("/completions/stream")
async def chat_completions_stream(request: ChatCompletionRequest):
    """Streaming chat completion endpoint."""
    base_url, api_key, default_model = get_default_client()
    model = request.model or default_model
    messages = [msg.model_dump() for msg in request.messages]

    client = create_client(base_url, api_key)
    try:
        stream_generator = client.chat_completion(
            model=model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True,
        )

        async def event_stream():
            async for chunk in stream_generator:
                data = SSEHandler.format_chunk(
                    chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                )
                yield data
            yield SSEHandler.format_chunk("", done=True)

        return StreamingResponse(event_stream(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.aclose()
