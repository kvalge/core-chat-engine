"""Backends API routes."""

import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.db import get_db
from ..models.entities import Backend
from ..models.schemas import (
    BackendCreate,
    BackendUpdate,
    BackendResponse,
    BackendTestResponse,
)
from ..services.llm import create_client

router = APIRouter()


@router.get("/backends", response_model=List[BackendResponse])
async def list_backends(db: AsyncSession = Depends(get_db)):
    """List all backends."""
    result = await db.execute(select(Backend).order_by(Backend.created_at.desc()))
    backends = result.scalars().all()
    return [BackendResponse.model_validate(b) for b in backends]


@router.post("/backends", response_model=BackendResponse)
async def create_backend(backend: BackendCreate, db: AsyncSession = Depends(get_db)):
    """Create a new backend."""
    # Check if this should be default
    if backend.is_default:
        result = await db.execute(select(Backend).where(Backend.is_default == True))
        for b in result.scalars().all():
            b.is_default = False

    db_backend = Backend(
        name=backend.name,
        base_url=backend.base_url,
        api_key=backend.api_key,
        models=backend.models,
        is_default=backend.is_default,
    )
    db.add(db_backend)
    await db.commit()
    await db.refresh(db_backend)
    return BackendResponse.model_validate(db_backend)


@router.get("/backends/{backend_id}", response_model=BackendResponse)
async def get_backend(backend_id: int, db: AsyncSession = Depends(get_db)):
    """Get a backend by ID."""
    result = await db.execute(select(Backend).where(Backend.id == backend_id))
    backend = result.scalar_one_or_none()
    if not backend:
        raise HTTPException(status_code=404, detail="Backend not found")
    return BackendResponse.model_validate(backend)


@router.put("/backends/{backend_id}", response_model=BackendResponse)
async def update_backend(
    backend_id: int, backend_update: BackendUpdate, db: AsyncSession = Depends(get_db)
):
    """Update a backend."""
    result = await db.execute(select(Backend).where(Backend.id == backend_id))
    backend = result.scalar_one_or_none()
    if not backend:
        raise HTTPException(status_code=404, detail="Backend not found")

    if backend_update.name is not None:
        backend.name = backend_update.name
    if backend_update.base_url is not None:
        backend.base_url = backend_update.base_url
    if backend_update.api_key is not None:
        backend.api_key = backend_update.api_key
    if backend_update.models is not None:
        backend.models_list = backend_update.models
    if backend_update.is_default is not None:
        if backend_update.is_default:
            # Unset other defaults
            other_result = await db.execute(
                select(Backend)
                .where(Backend.is_default == True)
                .where(Backend.id != backend_id)
            )
            for b in other_result.scalars().all():
                b.is_default = False
        backend.is_default = backend_update.is_default

    await db.commit()
    await db.refresh(backend)
    return BackendResponse.model_validate(backend)


@router.delete("/backends/{backend_id}")
async def delete_backend(backend_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a backend."""
    result = await db.execute(select(Backend).where(Backend.id == backend_id))
    backend = result.scalar_one_or_none()
    if not backend:
        raise HTTPException(status_code=404, detail="Backend not found")

    await db.delete(backend)
    await db.commit()
    return {"deleted": True}


@router.post("/backends/{backend_id}/test", response_model=BackendTestResponse)
async def test_backend(backend_id: int, db: AsyncSession = Depends(get_db)):
    """Test backend connection."""
    result = await db.execute(select(Backend).where(Backend.id == backend_id))
    backend = result.scalar_one_or_none()
    if not backend:
        raise HTTPException(status_code=404, detail="Backend not found")

    client = create_client(backend.base_url, backend.api_key)
    try:
        models = await client.list_models()
        return BackendTestResponse(
            success=True, message="Connection successful", models=models
        )
    except Exception as e:
        return BackendTestResponse(success=False, message=str(e), models=[])
    finally:
        await client.aclose()
