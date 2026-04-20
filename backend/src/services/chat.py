"""Chat service for handling conversations."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.entities import Project, Conversation, Message


class ChatService:
    """Service for chat operations."""

    def __init__(self, db: AsyncSession):
        """Initialize chat service."""
        self.db = db

    async def get_or_create_project(self, name: str = "Default") -> Project:
        """Get or create a project."""
        result = await self.db.execute(select(Project).order_by(Project.id))
        project = result.scalar_one_or_none()
        if not project:
            project = Project(name=name)
            self.db.add(project)
            await self.db.commit()
            await self.db.refresh(project)
        return project

    async def create_conversation(
        self, project_id: int, title: str = "New Chat"
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(project_id=project_id, title=title)
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        tool_calls: Optional[list] = None,
        tool_results: Optional[list] = None,
    ) -> Message:
        """Add a message to a conversation."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_results=tool_results,
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_conversation_messages(self, conversation_id: int) -> list[Message]:
        """Get all messages in a conversation."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        return list(result.scalars().all())

    async def update_conversation_title(self, conversation_id: int, title: str) -> None:
        """Update conversation title."""
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            conversation.title = title
            await self.db.commit()
