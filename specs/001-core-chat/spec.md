# Feature Specification: Core Chat Engine

**Feature Branch**: `001-core-chat`  
**Created**: 2026-04-20  
**Status**: Draft  
**Input**: User description: "Build the complete Core Chat Engine application with all features from the constitution: multi-turn chat with SSE streaming, OpenAI-compatible API, tool use loop, projects, file upload, and backend configuration UI."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Multi-Turn Chat Interface (Priority: P1)

As a user, I want to send messages in a chat interface and receive streaming responses from an LLM, so that I can have interactive conversations.

**Why this priority**: This is the core MVP - without chat, nothing else matters. All other features build on top of chat.

**Independent Test**: Can be fully tested by sending a message and verifying streaming response appears in UI. Delivers basic chat functionality.

**Acceptance Scenarios**:

1. **Given** a chat interface is open, **When** I type a message and press send, **Then** the message appears in the conversation history
2. **Given** I sent a message, **When** the LLM generates a response, **Then** the response streams in token-by-token (visible streaming)
3. **Given** I have multiple messages, **When** I view the conversation, **Then** I see the full message history in chronological order

---

### User Story 2 - OpenAI-Compatible API (Priority: P1)

As a developer, I want to integrate with the chat system via an OpenAI-compatible API, so that existing tools and applications can work with Core Chat Engine.

**Why this priority**: Enables external integration - critical for making the system useful beyond the web UI. Allows CLI tools, other apps to connect.

**Independent Test**: Can be tested by making a curl request to /v1/chat/completions and verifying JSON response. Delivers API compatibility.

**Acceptance Scenarios**:

1. **Given** a POST request to /v1/chat/completions with messages, **When** I include a valid API key, **Then** I receive a chat completion response
2. **Given** streaming is requested, **When** I call the API, **Then** responses stream via SSE
3. **Given** Ollama is running locally, **When** I call the API, **Then** the request is forwarded to Ollama (llama3.2 or mistral)

---

### User Story 3 - Tool Use Loop (Priority: P2)

As a user, I want the LLM to be able to call tools during conversation, so that I can get real-time information and perform actions.

**Why this priority**: Adds significant value - enables date/time queries, web search, todo lists, calendar without manual lookup.

**Independent Test**: Can be tested by asking a question requiring a tool and verifying tool is called and result returned. Delivers tool orchestration.

**Acceptance Scenarios**:

1. **Given** I ask "what time is it?", **When** the LLM calls the date/time tool, **Then** the current time is returned in the response
2. **Given** I ask a question requiring web search, **When** the LLM calls the web search tool, **Then** search results are incorporated into the response
3. **Given** I create a todo item, **When** I ask to list todos, **Then** my todo items are returned

---

### User Story 4 - Projects (Priority: P2)

As a user, I want to create multiple projects with different configurations, so that I can maintain separate conversations with different prompts and models.

**Why this priority**: Enables customization - different use cases need different system prompts, models, and tool configurations.

**Independent Test**: Can be tested by creating two projects with different system prompts and verifying each uses its own configuration. Delivers multi-project support.

**Acceptance Scenarios**:

1. **Given** no projects exist, **When** I create a new project, **Then** a default project is created with my configuration
2. **Given** a project exists, **When** I edit its system prompt, **Then** new chats in that project use the new prompt
3. **Given** multiple projects exist, **When** I switch between them, **Then** each maintains its own chat history

---

### User Story 5 - File Upload (Priority: P3)

As a user, I want to upload files for analysis, so that I can get help understanding documents and images.

**Why this priority**: Adds multi-modal capability - enables vision-capable models to analyze images and PDFs.

**Independent Test**: Can be tested by uploading an image and verifying it's analyzed. Delivers file upload for vision models.

**Acceptance Scenarios**:

1. **Given** I upload an image file, **When** using a vision-capable model, **Then** the image is described in the response
2. **Given** I upload a PDF, **When** the model processes it, **Then** I can ask questions about the content
3. **Given** I upload an image with a non-vision model, **Then** I receive a clear error explaining vision is not supported

---

### User Story 6 - Backend Configuration UI (Priority: P3)

As an administrator, I want to configure API backends via a UI, so that I can manage which LLM providers are available.

**Why this priority**: Enables runtime configuration - users can add/remove/modify backends without code changes.

**Independent Test**: Can be tested by adding a new backend via UI and verifying it's usable. Delivers backend management.

**Acceptance Scenarios**:

1. **Given** the backend config page, **When** I add a new backend with name, base URL, and API key, **Then** it appears in the backend list
2. **Given** a backend exists, **When** I click "test connection", **Then** I see success or error message
3. **Given** a backend is no longer needed, **When** I remove it, **Then** it's no longer available for use

---

### Edge Cases

- What happens when the LLM API is unavailable? (Show error, allow retry)
- How does the system handle very long messages? (Truncate or paginate)
- What happens if the stream is interrupted? (Allow resume or restart)
- How are messages stored if the app is closed? (Persisted to SQLite)
- What happens with invalid API keys? (Return 401 with clear error)

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a chat interface where users can send messages and receive streaming responses
- **FR-002**: System MUST implement OpenAI-compatible /v1/chat/completions endpoint with support for streaming
- **FR-003**: System MUST forward requests to Ollama (llama3.2, mistral) or any OpenAI-compatible provider
- **FR-004**: System MUST support tool calling loop driven by LLM responses (date/time, web search, todo list, calendar)
- **FR-005**: System MUST allow users to create and manage multiple projects with custom system prompts
- **FR-006**: System MUST allow per-project default model selection
- **FR-007**: System MUST allow per-project tool enable/disable configuration
- **FR-008**: System MUST support file uploads (text, PDF, images)
- **FR-009**: System MUST only attempt image analysis with vision-capable models and return clear error otherwise
- **FR-010**: System MUST provide UI for adding/editing/removing API backends
- **FR-011**: System MUST provide test connection button for each backend
- **FR-012**: System MUST store API keys server-side (not client-side)
- **FR-013**: System MUST use SSE for streaming responses
- **FR-014**: System MUST persist chat history to SQLite database
- **FR-015**: System MUST persist project configurations to SQLite database

### Key Entities *(include if feature involves data)*

- **ChatMessage**: A single message in a conversation (role, content, timestamp, attachments)
- **Conversation**: A sequence of messages (project_id, created_at, title)
- **Project**: A container for conversations (name, system_prompt, default_model, enabled_tools)
- **Backend**: An LLM API configuration (name, base_url, api_key, models)
- **Tool**: A callable function (name, description, enabled)
- **FileAttachment**: An uploaded file (filename, content, mime_type, project_id)

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can send a message and receive a streaming response within 5 seconds of submission
- **SC-002**: The OpenAI-compatible API responds correctly to standard /v1/chat/completions requests
- **SC-003**: Tool calls are correctly parsed from LLM responses and executed
- **SC-004**: 100% of uploaded images are correctly rejected when using non-vision models
- **SC-005**: Each project maintains independent chat history and configuration
- **SC-006**: Backend configuration changes take effect without application restart
- **SC-007**: Test connection button provides accurate success/failure feedback
- **SC-008**: Chat history persists across application restarts

---

## Assumptions

- Single-user local application - no authentication required
- SQLite database for local storage of chat history and configuration
- Ollama running locally for local LLM support (llama3.2, mistral)
- Local-only deployment (not cloud-hosted)
- No mobile support required for v1
- No user registration or profile management needed

---

## Notes

This is a comprehensive full-stack application. Per Constitution v1.0.0:
- No SDKs (LangChain, LlamaIndex, Vercel AI SDK) - hand-rolled implementation
- Full type annotations required on Python backend
- SSE for streaming (no third-party streaming libraries)