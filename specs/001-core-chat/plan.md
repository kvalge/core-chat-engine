# Implementation Plan: Core Chat Engine

**Branch**: `001-core-chat` | **Date**: 2026-04-21 | **Spec**: `specs/001-core-chat/spec.md`
**Input**: Feature specification from `/specs/001-core-chat/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build a complete Core Chat Engine web application with:
- Python FastAPI backend with full type annotations
- React 19 + TypeScript + Vite frontend
- Multi-turn chat with SSE streaming (hand-rolled)
- OpenAI-compatible /v1/chat/completions API (works with Ollama)
- LLM-driven tool use loop (date/time, web search, todo, calendar)
- Projects with custom prompts, models, and tool config
- File upload (text, PDF, images with vision support)
- Backend configuration UI

## Technical Context

**Language/Version**: Python 3.11+, TypeScript 5.4+  
**Primary Dependencies**: FastAPI (backend), React 19, TypeScript, Vite (frontend)  
**Storage**: SQLite (chat history, projects, backends)  
**Testing**: pytest (backend), Vitest (frontend)  
**Target Platform**: Linux server/local  
**Project Type**: web-service + frontend  
**Performance Goals**: <5s response time, streaming latency <500ms  
**Constraints**: No SDKs (hand-rolled), full type annotations, SSE streaming  
**Scale**: Single-user local application

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. No SDK Abstraction | PASS | Hand-rolled HTTP for API, streaming, tools |
| II. OpenAI Compatibility | PASS | /v1/chat/completions endpoint |
| III. LLM-Driven Tool Orchestration | PASS | Tool loop driven by LLM |
| IV. Type Safety | PASS | Full type annotations required |
| V. Project Isolation | PASS | Per-project config |
| VI. Multi-Modal File Upload | PASS | With vision model check |

## Project Structure

### Documentation (this feature)

```text
specs/001-core-chat/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── api.md          # API contracts
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Backend (Python FastAPI)
backend/
├── src/
│   ├── api/
│   │   └── routes/
│   │       ├── chat.py        # /v1/chat/completions
│   │       ├── projects.py    # CRUD for projects
│   │       └── backends.py   # CRUD for backends
│   ├── services/
│   │   ├── llm.py           # OpenAI API client (hand-rolled)
│   │   ├── streaming.py      # SSE handler (hand-rolled)
│   │   ├── tools.py         # Tool definitions & execution
│   │   └── ollama.py       # Ollama client
│   ├── models/
│   │   ├── schemas.py       # Pydantic models
│   │   ├── db.py           # SQLite connection
│   │   └── entities.py     # Database entities
│   └── main.py             # FastAPI app
└── tests/
    ├── unit/
    └── integration/

# Frontend (React + TypeScript + Vite)
frontend/
├── src/
│   ├── components/
│   │   ├── Chat.tsx        # Chat interface
��   │   ├── Message.tsx     # Message display
│   │   ├── Input.tsx       # Message input
│   │   ├── Sidebar.tsx     # Projects sidebar
│   │   ├── BackendConfig.tsx # Backend management
│   │   └── FileUpload.tsx   # File upload
│   ├── pages/
│   │   ├── ChatPage.tsx
│   │   └── SettingsPage.tsx
│   ├── services/
│   │   ├── api.ts         # API client
│   │   └── sse.ts        # SSE client
│   ├── hooks/
│   │   └── useChat.ts    # Chat state hook
│   └── App.tsx
└── tests/
    └── unit/

# Root
.env.example              # Environment template
README.md
requirements.txt         # Python dependencies
package.json             # Node dependencies
```

**Structure Decision**: Full-stack web application with separate backend/frontend directories. Backend is Python FastAPI with SQLite storage. Frontend is React + TypeScript + Vite.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| No violations | - | - |

---

## Phase 0: Research Summary

### Key Technical Decisions

| Decision | Rationale | Alternatives Considered |
|----------|----------|------------------------|
| FastAPI for backend | Async support, SSE native, type annotations | Aiohttp, Flask |
| SQLite for storage | Simple, single-file, no setup | PostgreSQL, JSON files |
| React 19 + Vite | Modern, fast, good TS support | Next.js, plain React |
| Hand-rolled HTTP | Constitution I - No SDKs | openai-python, httpx |
| SSE for streaming | Standard, native browser support | WebSockets |

### Ollama Integration

- Base URL: http://localhost:11434 (default)
- Models: llama3.2, mistral
- API: /api/chat (not /v1/chat)
- Request format differs from OpenAI

### Tool Definitions

| Tool | Function | Description |
|------|----------|-------------|
| get_current_time | datetime | Returns current date and time |
| web_search | search | Performs web search |
| todo_list | todos | Manages todo items |
| calendar_events | calendar | Lists calendar events |

---

## Phase 1: Data Model

### Entities

**Project**
- id: INTEGER PRIMARY KEY
- name: TEXT NOT NULL
- system_prompt: TEXT
- default_model: TEXT
- enabled_tools: TEXT (JSON array)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

**Conversation**
- id: INTEGER PRIMARY KEY
- project_id: INTEGER FK
- title: TEXT
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

**Message**
- id: INTEGER PRIMARY KEY
- conversation_id: INTEGER FK
- role: TEXT (user/assistant/system)
- content: TEXT
- tool_calls: TEXT (JSON array)
- tool_results: TEXT (JSON array)
- created_at: TIMESTAMP

**Backend**
- id: INTEGER PRIMARY KEY
- name: TEXT NOT NULL
- base_url: TEXT
- api_key: TEXT (encrypted)
- models: TEXT (JSON array)
- is_default: BOOLEAN
- created_at: TIMESTAMP

### API Contracts

See `contracts/api.md` for full OpenAI-compatible API specification.

### Quickstart

See `quickstart.md` for setup instructions.

---

## Notes

- All backend code requires full type annotations (Constitution IV)
- No external SDKs for API communication (Constitution I)
- Tool orchestration driven by LLM responses, not hardcoded (Constitution III)
- File uploads with vision model check (Constitution VI)