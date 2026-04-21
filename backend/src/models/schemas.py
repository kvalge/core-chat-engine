"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Project Schemas
class ProjectBase(BaseModel):
    """Base project schema."""

    name: str = Field(..., min_length=1, max_length=100)
    system_prompt: str = ""
    default_model: str = "llama3.2"
    enabled_tools: list[str] = []


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""

    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    system_prompt: Optional[str] = None
    default_model: Optional[str] = None
    enabled_tools: Optional[list[str]] = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Conversation Schemas
class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""

    project_id: int
    title: str = Field(..., min_length=1, max_length=200)


class ConversationResponse(BaseModel):
    """Schema for conversation response."""

    id: int
    project_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Message Schemas
class MessageCreate(BaseModel):
    """Schema for creating a message."""

    conversation_id: int
    role: str = Field(..., pattern="^(user|assistant|system|tool)$")
    content: str
    tool_calls: Optional[list[dict]] = None
    tool_results: Optional[list[dict]] = None


class MessageResponse(BaseModel):
    """Schema for message response."""

    id: int
    conversation_id: int
    role: str
    content: str
    tool_calls: Optional[list[dict]] = None
    tool_results: Optional[list[dict]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# Backend Schemas
class BackendBase(BaseModel):
    """Base backend schema."""

    name: str = Field(..., min_length=1, max_length=100)
    base_url: str = Field(..., min_length=1)
    api_key: Optional[str] = None
    models: list[str] = []
    is_default: bool = False


class BackendCreate(BackendBase):
    """Schema for creating a backend."""

    pass


class BackendUpdate(BaseModel):
    """Schema for updating a backend."""

    name: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    models: Optional[list[str]] = None
    is_default: Optional[bool] = None


class BackendResponse(BaseModel):
    """Schema for backend response - api_key is redacted."""

    id: int
    name: str
    base_url: str
    api_key_set: bool = False  # Redacted: true if key is set
    models: list[str] = []
    is_default: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_entity(cls, entity: "Backend") -> "BackendResponse":
        """Create response from entity, redacting api_key."""
        return cls(
            id=entity.id,
            name=entity.name,
            base_url=entity.base_url,
            api_key_set=bool(entity.api_key),
            models=entity.models_list,
            is_default=entity.is_default,
            created_at=entity.created_at,
        )


class BackendTestResponse(BaseModel):
    """Schema for backend test response."""

    success: bool
    message: str
    models: list[str] = []


# Todo Schemas
class TodoCreate(BaseModel):
    """Schema for creating a todo."""

    project_id: int
    title: str = Field(..., min_length=1, max_length=200)
    completed: bool = False


class TodoUpdate(BaseModel):
    """Schema for updating a todo."""

    title: Optional[str] = None
    completed: Optional[bool] = None


class TodoResponse(BaseModel):
    """Schema for todo response."""

    id: int
    project_id: int
    title: str
    completed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# File Upload Schemas
class FileUploadResponse(BaseModel):
    """Schema for file upload response."""

    id: int
    filename: str
    mime_type: str
    size: int

    model_config = {"from_attributes": True}


# Chat Schemas - OpenAI Compatible
class ChatMessage(BaseModel):
    """Chat message."""

    role: str = Field(..., pattern="^(system|user|assistant|tool)$")
    content: str


class ChatTool(BaseModel):
    """Tool definition."""

    type: str = "function"
    function: dict


class ChatCompletionRequest(BaseModel):
    """Chat completion request."""

    model: str
    messages: list[ChatMessage]
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(2048, ge=1, le=4096)
    stream: Optional[bool] = False
    tools: Optional[list[dict]] = None


class ChatMessageDelta(BaseModel):
    """Chat message delta for streaming."""

    role: Optional[str] = None
    content: Optional[str] = None


class ChatChoiceDelta(BaseModel):
    """Chat choice delta for streaming."""

    index: int
    delta: ChatMessageDelta
    finish_reason: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    """Chat completion chunk for streaming."""

    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: list[ChatChoiceDelta]


class ChatChoice(BaseModel):
    """Chat choice."""

    index: int
    message: ChatMessage
    finish_reason: str


class ChatCompletion(BaseModel):
    """Chat completion response."""

    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatChoice]
    usage: dict


class StreamChunk(BaseModel):
    """Streaming chunk for SSE."""

    data: Optional[dict] = None
    done: bool = False
    error: Optional[str] = None
