# Research: Core Chat Engine

## Phase 0 Findings

### Technology Decisions

| Decision | Rationale | Alternatives Considered |
|----------|----------|------------------------|
| FastAPI for backend | Native async, built-in SSE support, automatic OpenAPI docs, type annotations | Flask (no async), Aiohttp (low-level) |
| SQLite for storage | Zero-config, single file, ACID compliant, good Python support | PostgreSQL (needs server), JSON (no query), in-memory (lost on restart) |
| React 19 + Vite | Fast HMR, excellent TypeScript support, modern hooks | Next.js (too heavy), plain React (more setup) |
| Raw httpx for HTTP | Constitution requirement - no SDKs | urllib (clunky), requests (sync) |
| SSE for streaming | Native browser support, simple, works with FastAPI | WebSockets (more complex), polling (inefficient) |

### Ollama Specifics

Ollama differs from OpenAI API:

1. **Base URL**: `http://localhost:11434` (configurable)
2. **Endpoint**: `/api/chat` not `/v1/chat/completions`
3. **Request format**: Different JSON structure
4. **Stream**: Same SSE format
5. **No tool_calling**: Ollama models don't support tool calls natively

**Solution**: Implement abstraction layer that transforms requests between OpenAI format and Ollama format.

### Hand-Rolled Streaming

```python
# SSE format example
data: {"choices":[{"delta":{"content":"Hello"}}}

# In FastAPI
from fastapi.responses import StreamingResponse

async def generate():
    for chunk in stream:
        yield f"data: {json.dumps(chunk)}\n\n"
```

### Tool Call Extraction

Tool calls come from LLM as JSON in the response. Need to:
1. Parse `tool_calls` from assistant message
2. Execute tool function
3. Return result as `tool` role message
4. Loop until no more tool calls

---

## Questions Resolved

### Q1: How to handle Ollama tool calls?
**Answer**: Ollama doesn't support tool calls. Fall back to regular completion and use a different approach: ask user to confirm before executing tools.

### Q2: File upload size limits?
**Answer**: 10MB limit for images, 25MB for PDFs. Use streaming upload.

---

## Implementation Notes

- All database operations via SQLAlchemy with async support
- API keys encrypted at rest using Fernet
- CORS enabled for frontend on same origin
- No authentication (single-user local app)