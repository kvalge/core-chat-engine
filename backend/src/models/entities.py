"""Database entities."""

import json
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Boolean, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Project(Base):
    """Project entity - container for conversations."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, default="")
    default_model: Mapped[str] = mapped_column(String(50), default="llama3.2")
    enabled_tools: Mapped[str] = mapped_column(Text, default="[]")  # JSON array
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="project", cascade="all, delete-orphan"
    )

    @property
    def enabled_tools_list(self) -> list[str]:
        """Get enabled tools as list."""
        return json.loads(self.enabled_tools) if self.enabled_tools else []

    @enabled_tools_list.setter
    def enabled_tools_list(self, tools: list[str]) -> None:
        """Set enabled tools from list."""
        self.enabled_tools = json.dumps(tools)


class Conversation(Base):
    """Conversation entity - sequence of messages."""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    project: Mapped["Project"] = relationship("Project", back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    """Message entity - individual message in conversation."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # user, assistant, system, tool
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tool_calls: Mapped[Optional[str]] = mapped_column(Text, default=None)  # JSON array
    tool_results: Mapped[Optional[str]] = mapped_column(
        Text, default=None
    )  # JSON array
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )

    @property
    def tool_calls_list(self) -> list[dict]:
        """Get tool calls as list."""
        return json.loads(self.tool_calls) if self.tool_calls else []

    @tool_calls_list.setter
    def tool_calls_list(self, calls: list[dict]) -> None:
        """Set tool calls from list."""
        self.tool_calls = json.dumps(calls)

    @property
    def tool_results_list(self) -> list[dict]:
        """Get tool results as list."""
        return json.loads(self.tool_results) if self.tool_results else []

    @tool_results_list.setter
    def tool_results_list(self, results: list[dict]) -> None:
        """Set tool results from list."""
        self.tool_results = json.dumps(results)


class Backend(Base):
    """Backend entity - LLM API configuration."""

    __tablename__ = "backends"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    api_key: Mapped[Optional[str]] = mapped_column(String(500), default=None)
    models: Mapped[str] = mapped_column(Text, default="[]")  # JSON array
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    @property
    def models_list(self) -> list[str]:
        """Get models as list."""
        return json.loads(self.models) if self.models else []

    @models_list.setter
    def models_list(self, models: list[str]) -> None:
        """Set models from list."""
        self.models = json.dumps(models)


class TodoItem(Base):
    """Todo item for tool integration."""

    __tablename__ = "todo_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())


class FileAttachment(Base):
    """File attachment for uploads."""

    __tablename__ = "file_attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[bytes] = mapped_column(
        Text, nullable=False
    )  # Store as base64 or file path
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # text, pdf, image
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
