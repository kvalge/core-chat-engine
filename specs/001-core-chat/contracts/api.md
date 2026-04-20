# API Contracts: Core Chat Engine

## OpenAI-Compatible API

### POST /v1/chat/completions

Create a chat completion.

**Request**:
```json
{
  "model": "llama3.2",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  "stream": false,
  "temperature": 0.7,
  "max_tokens": 2048,
  "tools": [...]
}
```

**Response** (non-streaming):
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1690000000,
  "model": "llama3.2",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 15,
    "total_tokens": 35
  }
}
```

**Response** (streaming):
```
data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1690000000,"model":"llama3.2","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}

data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1690000000,"model":"llama3.2","choices":[{"index":0,"delta":{"content":"!"},"finish_reason":null}]}

data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1690000000,"model":"llama3.2","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

---

## Internal API

### Projects

#### GET /api/projects
List all projects.

**Response**:
```json
[
  {
    "id": 1,
    "name": "Default Project",
    "system_prompt": "",
    "default_model": "llama3.2",
    "enabled_tools": ["date_time", "web_search"],
    "created_at": "2026-04-20T00:00:00Z"
  }
]
```

#### POST /api/projects
Create a new project.

**Request**:
```json
{
  "name": "My Project",
  "system_prompt": "You are a coding assistant.",
  "default_model": "llama3.2",
  "enabled_tools": ["date_time", "todo_list"]
}
```

#### PUT /api/projects/{id}
Update a project.

#### DELETE /api/projects/{id}
Delete a project.

---

### Conversations

#### GET /api/projects/{project_id}/conversations
List conversations in a project.

#### POST /api/projects/{project_id}/conversations
Create a new conversation.

#### GET /api/conversations/{id}
Get conversation with messages.

---

### Backends

#### GET /api/backends
List all backends.

#### POST /api/backends
Add a new backend.

**Request**:
```json
{
  "name": "Ollama Local",
  "base_url": "http://localhost:11434",
  "api_key": "",
  "models": ["llama3.2", "mistral"],
  "is_default": true
}
```

#### POST /api/backends/{id}/test
Test backend connection.

**Response**:
```json
{
  "success": true,
  "message": "Connection successful",
  "models": ["llama3.2", "mistral"]
}
```

---

### File Upload

#### POST /api/upload
Upload a file.

**Request**: multipart/form-data
- file: binary
- conversation_id: integer

**Response**:
```json
{
  "id": 1,
  "filename": "document.pdf",
  "mime_type": "application/pdf",
  "size": 1024
}
```

---

## SSE Streaming Endpoint

### GET /api/chat/stream

Connect to receive streaming responses.

**Query Parameters**:
- conversation_id: integer (required)

**Events**:
- message: New message chunk
- done: Stream complete
- error: Error occurred