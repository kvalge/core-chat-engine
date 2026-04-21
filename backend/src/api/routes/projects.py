"""Projects API routes."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.db import get_db
from ...models.entities import Project, Conversation, Message
from ...models.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ConversationCreate,
    ConversationResponse,
)

router = APIRouter()


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    """List all projects."""
    result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    projects = result.scalars().all()
    return [ProjectResponse.model_validate(p) for p in projects]


@router.post("/projects", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: AsyncSession = Depends(get_db)):
    """Create a new project."""
    db_project = Project(
        name=project.name,
        system_prompt=project.system_prompt,
        default_model=project.default_model,
        enabled_tools=project.enabled_tools,
    )
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return ProjectResponse.model_validate(db_project)


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Get a project by ID."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int, project_update: ProjectUpdate, db: AsyncSession = Depends(get_db)
):
    """Update a project."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project_update.name is not None:
        project.name = project_update.name
    if project_update.system_prompt is not None:
        project.system_prompt = project_update.system_prompt
    if project_update.default_model is not None:
        project.default_model = project_update.default_model
    if project_update.enabled_tools is not None:
        project.enabled_tools_list = project_update.enabled_tools

    await db.commit()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.delete("/projects/{project_id}")
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a project."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await db.delete(project)
    await db.commit()
    return {"deleted": True}


# Conversation endpoints
@router.get(
    "/projects/{project_id}/conversations", response_model=List[ConversationResponse]
)
async def list_conversations(project_id: int, db: AsyncSession = Depends(get_db)):
    """List conversations in a project."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.project_id == project_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()
    return [ConversationResponse.model_validate(c) for c in conversations]


@router.post(
    "/projects/{project_id}/conversations", response_model=ConversationResponse
)
async def create_conversation(
    project_id: int,
    conversation: ConversationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new conversation."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_conversation = Conversation(project_id=project_id, title=conversation.title)
    db.add(db_conversation)
    await db.commit()
    await db.refresh(db_conversation)
    return ConversationResponse.model_validate(db_conversation)


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: int, db: AsyncSession = Depends(get_db)):
    """Get a conversation with its messages."""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = messages_result.scalars().all()

    return {
        "conversation": ConversationResponse.model_validate(conversation),
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "tool_calls": m.tool_calls_list if m.tool_calls else None,
                "tool_results": m.tool_results_list if m.tool_results else None,
                "created_at": m.created_at,
            }
            for m in messages
        ],
    }
