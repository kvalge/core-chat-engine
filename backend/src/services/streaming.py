"""SSE streaming handler - hand-rolled without SDKs."""
import json
from typing import AsyncGenerator

from ..models.schemas import StreamChunk


async def generate_sse(
    content: str, chunk_size: int = 5
) -> AsyncGenerator[str, None]:
    """Generate SSE stream from content."""
    for i in range(0, len(content), chunk_size):
        chunk = content[i : i + chunk_size]
        yield f"data: {json.dumps({'choices': [{'delta': {'content': chunk}}]})}\n\n"
        await _async_sleep(0.01)

    # Send done signal
    yield "data: {'choices': [{'delta': {}, 'finish_reason': 'stop'}]}\n\n"
    yield "data: [DONE]\n\n"


async def _async_sleep(delay: float) -> None:
    """Async sleep helper."""
    import asyncio

    await asyncio.sleep(delay)


class SSEHandler:
    """Handler for Server-Sent Events streaming."""

    @staticmethod
    async def stream_response(
        content: str, chunk_size: int = 5
    ) -> AsyncGenerator[str, None]:
        """Stream response content as SSE."""
        async for chunk in generate_sse(content, chunk_size):
            yield chunk

    @staticmethod
    def format_chunk(content: str, done: bool = False) -> str:
        """Format a chunk for SSE."""
        if done:
            return f"data: {json.dumps({'choices': [{'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
        return f"data: {json.dumps({'choices': [{'delta': {'content': content}}])}\n\n"

    @staticmethod
    def format_error(error: str) -> str:
        """Format an error for SSE."""
        return f"data: {json.dumps({'error': {'message': error}})}\n\n"