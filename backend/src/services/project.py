"""Project service for project operations."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.entities import Project, Conversation, Message


class ProjectService:
    """Service for project operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_projects(self) -> list[Project]:
        """List all projects."""
        result = await self.db.execute(
            select(Project).order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_project(self, project_id: int) -> Optional[Project]:
        """Get a project by ID."""
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        return result.scalar_one_or_none()

    async def create_project(
        self,
        name: str,
        system_prompt: str = "",
        default_model: str = "llama3.2",
        enabled_tools: Optional[list[str]] = None,
    ) -> Project:
        """Create a new project."""
        project = Project(
            name=name,
            system_prompt=system_prompt,
            default_model=default_model,
            enabled_tools=enabled_tools or [],
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update_project(
        self,
        project_id: int,
        name: Optional[str] = None,
        system_prompt: Optional[str] = None,
        default_model: Optional[str] = None,
        enabled_tools: Optional[list[str]] = None,
    ) -> Project:
        """Update a project."""
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        if name is not None:
            project.name = name
        if system_prompt is not None:
            project.system_prompt = system_prompt
        if default_model is not None:
            project.default_model = default_model
        if enabled_tools is not None:
            project.enabled_tools_list = enabled_tools

        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete_project(self, project_id: int) -> None:
        """Delete a project."""
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if project:
            await self.db.delete(project)
            await self.db.commit()

    async def get_or_create_default(self) -> Project:
        """Get or create the default project."""
        result = await self.db.execute(select(Project).order_by(Project.id))
        project = result.scalar_one_or_none()
        if not project:
            project = await self.create_project("Default")
        return project
