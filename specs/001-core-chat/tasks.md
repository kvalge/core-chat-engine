---

description: Task list for Core Chat Engine implementation
---

# Tasks: Core Chat Engine

**Input**: Design documents from `/specs/001-core-chat/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend directory structure in backend/src/
- [ ] T002 Create frontend directory structure in frontend/src/
- [ ] T003 Initialize Python project with FastAPI in backend/
- [ ] T004 Initialize React 19 + TypeScript + Vite project in frontend/
- [ ] T005 [P] Configure SQLite database in backend/src/models/db.py
- [ ] T006 [P] Create environment template .env.example

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create database schema and migrations in backend/src/models/
- [ ] T008 [P] Implement Project entity in backend/src/models/entities.py
- [ ] T009 [P] Implement Conversation entity in backend/src/models/entities.py
- [ ] T010 [P] Implement Message entity in backend/src/models/entities.py
- [ ] T011 [P] Implement Backend entity in backend/src/models/entities.py
- [ ] T012 [P] Implement TodoItem entity in backend/src/models/entities.py
- [ ] T013 Create Pydantic schemas in backend/src/models/schemas.py
- [ ] T014 Setup FastAPI app in backend/src/main.py
- [ ] T015 Configure CORS and middleware in backend/src/main.py
- [ ] T016 Create API client service in backend/src/services/llm.py
- [ ] T017 Create SSE streaming handler in backend/src/services/streaming.py
- [ ] T018 Setup React routing in frontend/src/App.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Multi-Turn Chat Interface (Priority: P1) 🎯 MVP

**Goal**: Users can send messages and receive streaming responses in UI

**Independent Test**: Can be tested by sending a message and verifying streaming response appears in UI

### Implementation for User Story 1

- [ ] T019 [P] [US1] Create chat API route in backend/src/api/routes/chat.py
- [ ] T020 [P] [US1] Implement chat service in backend/src/services/chat.py
- [ ] T021 [P] [US1] Create Chat component in frontend/src/components/Chat.tsx
- [ ] T022 [P] [US1] Create Message component in frontend/src/components/Message.tsx
- [ ] T023 [US1] Implement message input in frontend/src/components/Input.tsx
- [ ] T024 [US1] Create chat state hook in frontend/src/hooks/useChat.ts
- [ ] T025 [US1] Create SSE client in frontend/src/services/sse.ts
- [ ] T026 [US1] Connect frontend to backend streaming in frontend/src/services/api.ts
- [ ] T027 [US1] Create ChatPage in frontend/src/pages/ChatPage.tsx

**Checkpoint**: User Story 1 should be fully functional - users can chat and receive streaming responses

---

## Phase 4: User Story 2 - OpenAI-Compatible API (Priority: P1)

**Goal**: External tools can integrate via /v1/chat/completions API

**Independent Test**: Can be tested by making a curl request to /v1/chat/completions and verifying response

### Implementation for User Story 2

- [ ] T028 [P] [US2] Implement OpenAI-compatible /v1/chat/completions endpoint in backend/src/api/routes/chat.py
- [ ] T029 [P] [US2] Add streaming support to chat endpoint in backend/src/api/routes/chat.py
- [ ] T030 [P] [US2] Create Ollama adapter in backend/src/services/ollama.py
- [ ] T031 [US2] Add request/response format transformation in backend/src/services/llm.py

**Checkpoint**: User Story 2 should be fully functional - API works with OpenAI-compatible requests

---

## Phase 5: User Story 3 - Tool Use Loop (Priority: P2)

**Goal**: LLM can call tools during conversation (date/time, web search, todo, calendar)

**Independent Test**: Can be tested by asking a question requiring a tool and verifying tool is called and result returned

### Implementation for User Story 3

- [ ] T032 [P] [US3] Create tool definitions in backend/src/services/tools.py
- [ ] T033 [P] [US3] Implement date/time tool in backend/src/services/tools.py
- [ ] T034 [P] [US3] Implement web search tool in backend/src/services/tools.py
- [ ] T035 [P] [US3] Implement todo list tool in backend/src/services/tools.py
- [ ] T036 [US3] Implement calendar events tool in backend/src/services/tools.py
- [ ] T037 [US3] Add tool call parsing to chat service in backend/src/services/chat.py
- [ ] T038 [US3] Implement tool execution loop in backend/src/services/chat.py

**Checkpoint**: User Story 3 should be fully functional - tools can be called and executed

---

## Phase 6: User Story 4 - Projects (Priority: P2)

**Goal**: Users can create and manage multiple projects with different configurations

**Independent Test**: Can be tested by creating two projects with different system prompts and verifying each uses its own configuration

### Implementation for User Story 4

- [ ] T039 [P] [US4] Create projects API routes in backend/src/api/routes/projects.py
- [ ] T040 [P] [US4] Implement project CRUD service in backend/src/services/project.py
- [ ] T041 [P] [US4] Create Sidebar component in frontend/src/components/Sidebar.tsx
- [ ] T042 [US4] Add project switching to chat state in frontend/src/hooks/useChat.ts
- [ ] T043 [US4] Add project management UI in frontend/src/pages/SettingsPage.tsx

**Checkpoint**: User Story 4 should be fully functional - multiple projects with independent configs

---

## Phase 7: User Story 5 - File Upload (Priority: P3)

**Goal**: Users can upload text, PDF, and images for analysis with vision models

**Independent Test**: Can be tested by uploading an image and verifying it's analyzed (with vision model) or rejected (with non-vision model)

### Implementation for User Story 5

- [ ] T044 [P] [US5] Implement file upload endpoint in backend/src/api/routes/upload.py
- [ ] T045 [P] [US5] Create FileAttachment entity in backend/src/models/entities.py
- [ ] T046 [P] [US5] Add vision model detection in backend/src/services/llm.py
- [ ] T047 [US5] Add file upload to chat service in backend/src/services/chat.py
- [ ] T048 [US5] Create FileUpload component in frontend/src/components/FileUpload.tsx
- [ ] T049 [US5] Add error handling for non-vision models in frontend/src/components/FileUpload.tsx

**Checkpoint**: User Story 5 should be fully functional - file upload works with vision model check

---

## Phase 8: User Story 6 - Backend Configuration UI (Priority: P3)

**Goal**: Users can configure API backends via UI (add/edit/remove, test connection)

**Independent Test**: Can be tested by adding a backend via UI and verifying test connection button shows success/failure

### Implementation for User Story 6

- [ ] T050 [P] [US6] Create backends API routes in backend/src/api/routes/backends.py
- [ ] T051 [P] [US6] Implement backend CRUD service in backend/src/services/backend.py
- [ ] T052 [P] [US6] Implement test connection functionality in backend/src/services/backend.py
- [ ] T053 [US6] Create BackendConfig component in frontend/src/components/BackendConfig.tsx
- [ ] T054 [US6] Add backend management to SettingsPage in frontend/src/pages/SettingsPage.tsx

**Checkpoint**: User Story 6 should be fully functional - backend configuration UI works

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T055 [P] Add error handling and logging across all services
- [ ] T056 [P] Performance optimization for streaming latency
- [ ] T057 Add database indexes in backend/src/models/db.py
- [ ] T058 Run quickstart.md validation
- [ ] T059 Final integration testing

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 (P1) is MVP - completes Chat Interface
  - US2 (P1) can run in parallel with US1 after Foundational
  - US3 (P2) depends on US1 completion
  - US4 (P2) depends on US1 completion
  - US5 (P3) depends on US1, US4
  - US6 (P3) can be done anytime after Foundational

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration

### Parallel Opportunities

- Phase 1 setup tasks marked [P] can run in parallel
- Phase 2 foundational tasks marked [P] can run in parallel
- US1 and US2 can start in parallel after Phase 2

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test chat interface independently
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Test → Deploy/Demo (MVP!)
3. Add US2 → Test → Deploy/Demo
4. Add US3 → Test → Deploy/Demo
5. Add US4 → Test → Deploy/Demo
6. Add US5 + US6 → Test → Deploy/Demo (Full!)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- No tests requested in spec - skip test tasks