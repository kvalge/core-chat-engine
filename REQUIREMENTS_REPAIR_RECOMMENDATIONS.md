# Requirements repair recommendations

This document compares the current **Core Chat Engine** implementation against the original build specification and lists prioritized, actionable recommendations. It is based on a full read-through of the backend (`backend/src`), frontend (`frontend/src`), and supporting specs.

---

## Compliance with stack constraints (positive notes)

- **Forbidden SDKs:** No LangChain, LlamaIndex, or Vercel AI SDK usage was found in application code; HTTP is handled with **httpx** and JSON with the standard library / Pydantic, which matches the constraints.
- **Allowed stack:** FastAPI + SQLAlchemy async + React 18 + TypeScript + Vite are in place.

---

## 1. Multi-turn chat with streaming (SSE, hand-rolled)

| Gap | Evidence / location | Recommendation |
|-----|---------------------|------------------|
| **UI does not stream** | `frontend/src/components/Chat.tsx` posts to `/v1/chat/completions` with `stream: false` and expects a full JSON body. | Switch the chat UI to the existing streaming endpoint (`POST /v1/chat/completions/stream`) and append tokens as they arrive. Reuse or align with `frontend/src/services/api.ts` (`streamingChatCompletion`). |
| **SSE stream incomplete for tools** | `backend/src/api/routes/chat.py` only forwards `delta.content` from each chunk. OpenAI-compatible streams also emit `delta.tool_calls` (and finish reasons) which are dropped. | Extend the streaming forwarder to pass through **full choice deltas** (at least `content`, `tool_calls`, `role`, `finish_reason`) so a tool loop can run against streamed completions if desired. |
| **No `[DONE]` after stream** | `chat_completions_stream` ends with `format_chunk("", done=True)` but does not emit `data: [DONE]\n\n` (your `SSEHandler.generate_sse` does, but this path does not). Frontend parsers in `api.ts` / `sse.ts` treat `[DONE]` as end-of-stream. | Emit a final **`data: [DONE]\n\n`** (or align frontend to treat the current “empty delta + finish_reason” as terminal) for consistency with common OpenAI clients and your own frontend helpers. |
| **Multi-turn persistence in UI** | Chat state is only in React memory; projects/conversations APIs exist but are unused by `Chat.tsx`. | Load/save conversations via `/api/projects/.../conversations` and `/api/conversations/{id}` so turns survive reloads and match “multi-turn” product expectations. |

---

## 2. Dual provider support (OpenAI-compatible + Anthropic), switchable per conversation

| Gap | Evidence / location | Recommendation |
|-----|---------------------|------------------|
| **No Anthropic client** | `backend/src/services/llm.py` only implements **`/v1/chat/completions`** (OpenAI-style). | Add a separate **Anthropic Messages API** client (async httpx), same “no SDK” rule: build request bodies and parse SSE/JSON manually. Map Anthropic message/tool formats to your internal message model. |
| **Chat ignores configured backends** | `get_default_client()` in `backend/src/api/routes/chat.py` only reads **`OLLAMA_BASE_URL` / `OLLAMA_MODEL`**, not the `Backend` table. | Resolve **base URL, API key, and default model** from the selected backend (or default `Backend.is_default`). |
| **No `provider_type` on backend** | `backend/src/models/entities.py` — `Backend` has `name`, `base_url`, `api_key`, `models`, `is_default` only. | Add **`provider_type`** (e.g. `openai_compatible`, `anthropic`, `ollama`) and branch to the correct client and URL layout in one thin routing layer. |
| **Per-conversation provider switch** | `Conversation` has no `backend_id` or `provider_override`. | Add **`backend_id`** (FK to `backends`) and/or explicit provider fields on `Conversation`; expose in UI when starting or editing a chat. |
| **Ollama adapter unused** | `backend/src/services/ollama.py` defines `OllamaAdapter` (`/api/chat`, `/api/tags`) but routes use `LLMClient` (`.../chat/completions`). | Either: (a) route `provider_type=ollama` through `OllamaAdapter`, or (b) document and enforce that Ollama is only used via **OpenAI-compatible base URL** (e.g. `http://localhost:11434/v1`) and fix defaults accordingly (see section 7). |

---

## 3. Tool use loop (LLM-driven; date/time, web search, web fetch, todo, calendar)

| Gap | Evidence / location | Recommendation |
|-----|---------------------|------------------|
| **No agent loop in API** | `chat.py` never passes **`tools`** from the request into streaming (non-stream path accepts `request.tools` but nothing executes tools). There is no loop: call model → if `tool_calls` → execute → append tool messages → recall model. | Implement a **single generic loop** in a service module: max turns, append assistant `tool_calls` and `tool` role messages per OpenAI semantics; stop when the model returns text without tools. No hardcoded “if user said X then tool Y”. |
| **`web_fetch` missing** | `backend/src/services/tools.py` — `get_tool_definitions()` has time, search, todo, calendar only. | Add **`web_fetch`** (httpx GET + readable text extraction / size limits / SSRF protections) and register it in definitions + `execute_tool`. |
| **Search / calendar are stubs** | `execute_web_search`, `execute_calendar_events` return placeholder JSON. | Wire optional env config (e.g. search API key, calendar ICS URL or provider) or clearly document MVP limits; still return structured results so the LLM can reason about “no results”. |
| **Project tool allowlist unused** | `Project.enabled_tools` exists but nothing filters `get_tool_definitions()` by project. | When building the `tools` array for a request, **filter** to `Project.enabled_tools_list` for the active project. |
| **Anthropic / Ollama tool shapes** | Tool execution assumes OpenAI-style `tool_calls` on the assistant message. | In the Anthropic and Ollama branches, normalize tool invocation and results into your internal representation before the next model call. |

---

## 4. Projects: custom system prompt, default model, per-project tool toggles

| Gap | Evidence / location | Recommendation |
|-----|---------------------|------------------|
| **UI does not edit project settings** | `Sidebar.tsx` only lists projects and creates by name; no screen for system prompt, default model, or tools. | Add a project settings panel (or modal) calling `PUT /api/projects/{id}` with `system_prompt`, `default_model`, `enabled_tools`. |
| **Chat ignores project context** | `Chat.tsx` never sends **system** message from `Project.system_prompt` or **`Project.default_model`**. | On send, prepend `system` from the active project and set `model` from project default unless the user overrides. |
| **Sidebar selection not wired** | `selectedProject` in `Sidebar.tsx` is local state and **not passed** to `App` / `Chat`. | Lift project (and conversation) state to `App.tsx` or use a small store/context so `Chat` uses the selected project. |
| **Likely DB serialization bug on create** | `projects.py` sets `enabled_tools=project.enabled_tools` on `Project` while the column is **JSON text** (`entities.py`). Passing a Python `list` may not persist as valid JSON without `json.dumps`. | Serialize with **`json.dumps`** (or use the `enabled_tools_list` setter) on create/update; same pattern for **`Backend.models`** in `backends.py` if lists are written raw to `Text` columns. |

---

## 5. File upload: text, PDF, images (vision-capable models only)

| Gap | Evidence / location | Recommendation |
|-----|---------------------|------------------|
| **Upload not integrated in chat** | `FileUpload.tsx` exists but **`Chat.tsx` does not import it**; no `conversation_id` / `message_id` flow. | After creating a user message row, render `FileUpload` with IDs; then build multimodal **`content`** for the LLM request. |
| **PDF not extracted** | `get_file_content()` in `upload.py` returns a **placeholder string** for PDFs, not extracted text. | Add an allowed PDF library (e.g. **pypdf** or **pdfplumber** per spec) and store extracted text (and optional size limits). |
| **Vision gating unused in upload path** | `validate_vision_request()` exists but upload route does not call it. | Before accepting **image** uploads (or before attaching to a message), require a **vision-capable model** for the target conversation; return 400 with a clear message. |
| **Message schema is text-only** | `schemas.py` — `ChatMessage.content` is **`str`**, not `str | list` (multimodal parts). | Extend chat schemas and `LLMClient` payload building to support **OpenAI-style multimodal** `content` arrays where needed. |
| **Attachment storage type** | `FileAttachment.content` is `Text` holding base64 text — workable but large; confirm SQLite limits. | Consider **filesystem/blob** storage for large files; keep DB metadata only. |

---

## 6. Backend configuration UI (CRUD + provider + test connection)

| Gap | Evidence / location | Recommendation |
|-----|---------------------|------------------|
| **No edit backend** | `BackendConfig.tsx` supports add, test, delete only. | Add **edit** (PUT) flow; optionally mask API key unless user enters a new one. |
| **No provider type in UI** | Matches missing backend field. | Add provider selector and validate **base URL** hints per provider. |
| **Test connection vs Ollama** | `test_backend` uses `LLMClient.list_models()` → **`GET {base}/models`**. Raw Ollama host (`http://localhost:11434`) uses **`/api/tags`**, not `/models`. | In `test_backend`, branch on **`provider_type`** (or probe both OpenAI-style `/v1/models` and Ollama `/api/tags` with clear success criteria). |
| **Default backend flag** | Backend model has `is_default` but UI does not set it when adding backends. | Expose “set as default” and ensure chat resolution uses it. |

---

## 7. API keys server-side, not exposed to the browser

| Gap | Evidence / location | Recommendation |
|-----|---------------------|------------------|
| **Keys returned in API responses** | `BackendResponse` inherits **`api_key`** from `BackendBase` (`schemas.py`); list/get backend routes return it. | Use a **redacted** response model for GET/list (e.g. `api_key_set: bool` or `api_key_last4`); only accept full key on create/update POST body; never echo full key back. |
| **Plaintext at rest** | `cryptography` is in **`requirements.txt`** but unused in codebase. | Encrypt `Backend.api_key` at rest with a server-side master key from env (Fernet or similar), or integrate OS secret store for production. |

---

## 8. Local LLM via Ollama (llama3.2 and mistral)

| Gap | Evidence / location | Recommendation |
|-----|---------------------|------------------|
| **Default URL may be wrong for `LLMClient`** | `LLMClient` posts to **`{base_url}/chat/completions`**. Ollama’s OpenAI-compatible surface is typically **`{host}/v1/chat/completions`**. Default `OLLAMA_BASE_URL` of `http://localhost:11434` would call **`/chat/completions`**, which is wrong unless the user appends `/v1`. | Set default to **`http://localhost:11434/v1`** or normalize in `create_client` when `provider_type=ollama`. Alternatively, use **`OllamaAdapter`** for native `/api/chat`. |
| **Mistral explicitly** | Defaults mention `llama3.2`; mistral appears in `OLLAMA_MODELS` but not as default. | Document and/or offer **mistral** as a preset model name in UI and sample configs. |

---

## 9. Code defects that block or undermine the above

| Issue | Location | Recommendation |
|-------|----------|----------------|
| **Missing import (runtime error)** | `backend/src/api/routes/chat.py` uses **`ChatChoice`** in `chat_completions` but the import block only includes `ChatCompletionRequest`, `ChatCompletion`, `ChatMessage`. | Add `ChatChoice` to imports from `schemas` (or run mypy/ruff to catch this). |
| **Unused / misleading dependency** | `sse-starlette` in `requirements.txt` while SSE is hand-rolled in `streaming.py` / routes. | Remove if unused, or adopt it consistently—avoid two competing patterns. |
| **`upload.py` MIME fallback** | Unknown MIME maps to **`file_type = "text"`** via `.get(..., "text")`, so `if not file_type` is dead code and unsafe types may be treated as text. | Reject unknown MIME types explicitly. |

---

## Suggested implementation order

1. **Fix broken imports and persistence bugs** (`ChatChoice` import; JSON serialization for `Project.enabled_tools` / `Backend.models`; Ollama base URL).
2. **Wire UI to backend reality:** project + conversation IDs, streaming endpoint, redacted API keys.
3. **Central “chat orchestration” service:** resolve backend + provider → build messages (system from project) → tool loop → optional streaming pass-through.
4. **Anthropic + provider_type + per-conversation backend selection.**
5. **Multimodal messages + PDF extraction + vision gating + FileUpload in Chat.**

---

## Traceability matrix (spec → primary code areas)

| Spec item | Main files to touch |
|-----------|---------------------|
| SSE streaming | `backend/src/api/routes/chat.py`, `backend/src/services/streaming.py`, `frontend/src/components/Chat.tsx`, `frontend/src/services/api.ts` |
| OpenAI-compatible + Anthropic | `backend/src/services/llm.py` (new module e.g. `anthropic_client.py`), `backend/src/api/routes/chat.py`, `backend/src/models/entities.py`, `backend/src/models/schemas.py` |
| Tool loop | New `backend/src/services/agent_loop.py` (or extend `chat.py`), `backend/src/services/tools.py`, `backend/src/services/project.py` (optional) |
| Projects | `frontend/src/components/Sidebar.tsx`, `frontend/src/App.tsx`, `frontend/src/components/Chat.tsx`, `backend/src/api/routes/projects.py` |
| Uploads | `frontend/src/components/Chat.tsx`, `frontend/src/components/FileUpload.tsx`, `backend/src/api/routes/upload.py`, `backend/src/services/llm.py`, `backend/src/models/schemas.py` |
| Backend UI | `frontend/src/components/BackendConfig.tsx`, `backend/src/api/routes/backends.py`, `backend/src/models/schemas.py` |
| Ollama | `backend/src/api/routes/chat.py`, `backend/src/services/ollama.py`, `backend/src/services/llm.py` |

This should be sufficient for a structured repair sprint without expanding scope into new frameworks beyond what the original input allowed.
