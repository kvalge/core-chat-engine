"""File upload API routes."""

import base64
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.db import get_db
from ..models.entities import FileAttachment, Message
from ..services.llm import is_vision_model

router = APIRouter()

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB

ALLOWED_TYPES = {
    "text/plain": "text",
    "application/pdf": "pdf",
    "image/jpeg": "image",
    "image/png": "image",
    "image/gif": "image",
    "image/webp": "image",
}


@router.post("/upload")
async def upload_file(
    conversation_id: int,
    message_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload a file for a conversation."""
    # Read file content
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 25MB)")

    # Determine file type
    mime_type = file.content_type or "application/octet-stream"
    file_type = ALLOWED_TYPES.get(mime_type, "text")
    if not file_type:
        raise HTTPException(
            status_code=400, detail=f"Unsupported file type: {mime_type}"
        )

    # Verify message exists
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Create attachment
    attachment = FileAttachment(
        message_id=message_id,
        filename=file.filename or "unknown",
        content=base64.b64encode(content).decode(),
        mime_type=mime_type,
        file_type=file_type,
    )
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)

    return {
        "id": attachment.id,
        "filename": attachment.filename,
        "mime_type": attachment.mime_type,
        "size": len(content),
    }


@router.get("/upload/{attachment_id}")
async def get_upload(
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get file attachment."""
    result = await db.execute(
        select(FileAttachment).where(FileAttachment.id == attachment_id)
    )
    attachment = result.scalar_one_or_none()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    return {
        "id": attachment.id,
        "filename": attachment.filename,
        "mime_type": attachment.mime_type,
        "file_type": attachment.file_type,
    }


def validate_vision_request(model: str) -> Optional[str]:
    """Validate if model supports vision. Return error message if not."""
    if not is_vision_model(model):
        return f"Model '{model}' does not support vision. Upload an image with a vision-capable model like llama3.2-vision or llava."
    return None


def get_file_content(attachment: FileAttachment) -> dict:
    """Get file content for LLM."""
    if attachment.file_type == "image":
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:{attachment.mime_type};base64,{attachment.content}"
            },
        }
    elif attachment.file_type == "text":
        return {
            "type": "text",
            "text": base64.b64decode(attachment.content).decode("utf-8"),
        }
    elif attachment.file_type == "pdf":
        return {
            "type": "text",
            "text": f"[PDF: {attachment.filename}]",
        }
    return {"type": "text", "text": f"[File: {attachment.filename}]"}
