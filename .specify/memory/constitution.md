# Core Chat Engine Constitution

## Core Principles

### I. No SDK Abstraction
All API communication, streaming, and tool orchestration MUST be implemented manually without third-party SDKs that abstract these concerns. Direct HTTP calls required.

### II. OpenAI Compatibility
System MUST implement OpenAI-compatible /v1/chat/completions endpoint. MUST support streaming (SSE), tool call parsing, and stop reasons. MUST work with Ollama (llama3.2, mistral) and any OpenAI-compatible provider.

### III. LLM-Driven Tool Orchestration
Tool calling loop MUST be driven by the LLM's responses, not hardcoded orchestration. System MUST support: date/time, web search, todo list, calendar tools.

### IV. Type Safety
Python backend MUST use full type annotations. All functions, classes, and API endpoints MUST have type hints.

### V. Project Isolation
Each project MUST support custom system prompts, default model selection, and per-project tool enable/disable. Configuration stored server-side with API keys.

### VI. Multi-Modal File Upload
System MUST support file uploads (text, PDF, images). Image analysis MUST only be attempted with vision-capable models. Non-vision models MUST return appropriate error.

## Technology Stack

Backend: Python FastAPI with async REST API. Frontend: React 19, TypeScript, Vite. Local LLM: Ollama (llama3.2, mistral). All streaming via Server-Sent Events (SSE), hand-rolled.

## Development Workflow

Feature development follows: Spec → Plan → Tasks → Implement → Checklist. All PRs must verify constitution compliance.

## Governance

Constitution supersedes all other practices. Amendments require documentation, approval, and migration plan. All PRs/reviews must verify compliance with No SDK Abstraction principle. Complexity must be justified.

**Version**: 1.0.0 | **Ratified**: 2026-04-20 | **Last Amended**: 2026-04-20