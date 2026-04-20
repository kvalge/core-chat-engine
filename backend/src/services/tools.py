"""Tool definitions and execution for tool use loop."""

import json
from datetime import datetime
from typing import Any, Callable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.entities import TodoItem, Project


# Tool definitions following OpenAI tool schema
def get_tool_definitions() -> list[dict]:
    """Get tool definitions for the LLM."""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "Get the current date and time. Use this when the user asks about the current time.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for information. Use this when you need to find current information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query",
                        }
                    },
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "todo_list",
                "description": "Manage todo items. Use this to add, list, or complete todos.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["add", "list", "complete"],
                            "description": "Action to perform",
                        },
                        "title": {
                            "type": "string",
                            "description": "Todo title (required for add/complete)",
                        },
                    },
                    "required": ["action"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "calendar_events",
                "description": "Get calendar events. Use this when the user asks about events or schedule.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Number of days to look ahead",
                            "default": 7,
                        }
                    },
                    "required": [],
                },
            },
        },
    ]


async def execute_tool(
    tool_name: str,
    arguments: dict,
    db: AsyncSession,
    project_id: int,
) -> str:
    """Execute a tool and return the result."""
    if tool_name == "get_current_time":
        return execute_get_current_time()
    elif tool_name == "web_search":
        return await execute_web_search(arguments.get("query", ""))
    elif tool_name == "todo_list":
        return await execute_todo_list(
            arguments.get("action", "list"),
            arguments.get("title"),
            db,
            project_id,
        )
    elif tool_name == "calendar_events":
        return execute_calendar_events(arguments.get("days", 7))
    else:
        return f"Unknown tool: {tool_name}"


def execute_get_current_time() -> str:
    """Execute get_current_time tool."""
    now = datetime.now()
    return json.dumps(
        {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "timezone": "UTC+3",
        }
    )


async def execute_web_search(query: str) -> str:
    """Execute web_search tool."""
    # Placeholder - in production, integrate with search API
    return json.dumps(
        {
            "query": query,
            "results": [],
            "message": "Web search not configured. Set up a search API key to enable.",
        }
    )


async def execute_todo_list(
    action: str,
    title: Optional[str],
    db: AsyncSession,
    project_id: int,
) -> str:
    """Execute todo_list tool."""
    if action == "add":
        if not title:
            return json.dumps({"error": "Title is required for adding a todo"})
        todo = TodoItem(project_id=project_id, title=title)
        db.add(todo)
        await db.commit()
        await db.refresh(todo)
        return json.dumps({"success": True, "todo_id": todo.id})

    elif action == "list":
        result = await db.execute(
            select(TodoItem)
            .where(TodoItem.project_id == project_id)
            .order_by(TodoItem.created_at.desc())
        )
        todos = result.scalars().all()
        return json.dumps(
            {
                "todos": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "completed": t.completed,
                        "created_at": t.created_at.isoformat(),
                    }
                    for t in todos
                ]
            }
        )

    elif action == "complete":
        if not title:
            return json.dumps({"error": "Title is required for completing a todo"})
        result = await db.execute(
            select(TodoItem)
            .where(TodoItem.project_id == project_id)
            .where(TodoItem.title == title)
        )
        todo = result.scalar_one_or_none()
        if todo:
            todo.completed = True
            await db.commit()
            return json.dumps({"success": True, "todo_id": todo.id})
        return json.dumps({"error": "Todo not found"})

    return json.dumps({"error": f"Unknown action: {action}"})


def execute_calendar_events(days: int) -> str:
    """Execute calendar_events tool."""
    # Placeholder - in production, integrate with calendar API
    return json.dumps(
        {
            "days": days,
            "events": [],
            "message": "Calendar not configured. Connect a calendar service to enable.",
        }
    )


def parse_tool_calls(tool_calls: list[dict]) -> list[tuple[str, dict]]:
    """Parse tool calls from LLM response."""
    results = []
    for tc in tool_calls:
        if isinstance(tc, dict):
            func = tc.get("function", {})
            name = func.get("name", "")
            args_str = func.get("arguments", "{}")
            try:
                args = json.loads(args_str) if isinstance(args_str, str) else args_str
            except json.JSONDecodeError:
                args = {}
            results.append((name, args))
    return results
