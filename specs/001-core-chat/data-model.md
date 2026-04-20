# Data Model: Core Chat Engine

## Entities

### Project

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Unique identifier |
| name | TEXT | NOT NULL | Project name |
| system_prompt | TEXT | DEFAULT '' | Custom system prompt |
| default_model | TEXT | DEFAULT 'llama3.2' | Default model to use |
| enabled_tools | TEXT | JSON array | List of enabled tool names |
| created_at | TIMESTAMP | NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOW() | Last update timestamp |

**Relationships**: Has many Conversations

---

### Conversation

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Unique identifier |
| project_id | INTEGER | FK → Project.id | Parent project |
| title | TEXT | NOT NULL | Conversation title |
| created_at | TIMESTAMP | NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOW() | Last update timestamp |

**Relationships**: Belongs to Project, Has many Messages

---

### Message

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Unique identifier |
| conversation_id | INTEGER | FK → Conversation.id | Parent conversation |
| role | TEXT | NOT NULL, IN(user,assistant,system,tool) | Message role |
| content | TEXT | NOT NULL | Message content |
| tool_calls | TEXT | NULLABLE, JSON | Array of tool calls |
| tool_results | TEXT | NULLABLE, JSON | Array of tool results |
| created_at | TIMESTAMP | NOW() | Creation timestamp |

**Relationships**: Belongs to Conversation

**State Transitions**:
- user → assistant (model response)
- assistant → tool (if tool_calls present)
- tool → assistant (tool result returned)

---

### Backend

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Unique identifier |
| name | TEXT | NOT NULL | Backend display name |
| base_url | TEXT | NOT NULL | API base URL |
| api_key | TEXT | ENCRYPTED | API key (encrypted) |
| models | TEXT | JSON array | Available models |
| is_default | BOOLEAN | DEFAULT FALSE | Default backend |
| created_at | TIMESTAMP | NOW() | Creation timestamp |

**Relationships**: Has many Projects (via default_model)

---

### FileAttachment

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Unique identifier |
| message_id | INTEGER | FK → Message.id | Parent message |
| filename | TEXT | NOT NULL | Original filename |
| content | BLOB | NOT NULL | File content |
| mime_type | TEXT | NOT NULL | MIME type |
| file_type | TEXT | IN(text,pdf,image) | File category |
| created_at | TIMESTAMP | NOW() | Upload timestamp |

**Relationships**: Belongs to Message

---

### TodoItem

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PK, AUTOINCREMENT | Unique identifier |
| project_id | INTEGER | FK → Project.id | Parent project |
| title | TEXT | NOT NULL | Todo title |
| completed | BOOLEAN | DEFAULT FALSE | Completion status |
| created_at | TIMESTAMP | NOW() | Creation timestamp |

---

## Validation Rules

| Entity | Rule |
|--------|------|
| Project.name | 1-100 characters, unique per user |
| Project.system_prompt | Max 10000 characters |
| Message.content | Max 100000 characters |
| Backend.base_url | Valid URL format |
| FileAttachment.size | Max 25MB |

---

## Indexes

- `idx_conversation_project` on Conversation(project_id)
- `idx_message_conversation` on Message(conversation_id)
- `idx_todo_project` on TodoItem(project_id)