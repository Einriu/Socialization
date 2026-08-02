"""长期记忆与用户档案 API。"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.models.p2 import UserProfile
from app.schemas.p2 import MemoryCreate, MemoryUpdate, UserProfileUpdate
from app.services import memory_service

router = APIRouter()


@router.get("/memory")
def list_memory(db: Session = Depends(get_db)) -> dict:
    items = memory_service.list_memory(db)
    return success_response(
        [
            {
                "id": str(item.id),
                "kind": item.kind,
                "content": item.content,
                "status": item.status,
                "person_id": str(item.person_id) if item.person_id else None,
            }
            for item in items
        ]
    )


@router.post("/memory")
def create_memory(data: MemoryCreate, db: Session = Depends(get_db)) -> dict:
    item = memory_service.create_memory(db, data)
    return success_response(
        {"id": str(item.id), "kind": item.kind, "content": item.content, "status": item.status}
    )


@router.patch("/memory/{item_id}")
def update_memory(
    item_id: uuid.UUID, data: MemoryUpdate, db: Session = Depends(get_db)
) -> dict:
    item = memory_service.update_memory(db, item_id, data)
    return success_response(
        {"id": str(item.id), "kind": item.kind, "content": item.content, "status": item.status}
    )


@router.get("/profile")
def get_profile(db: Session = Depends(get_db)) -> dict:
    profile = db.execute(select(UserProfile).limit(1)).scalar_one_or_none()
    if profile is None:
        profile = UserProfile()
        db.add(profile)
        db.flush()
    return success_response(
        {
            "expression_preferences": profile.expression_preferences,
            "social_goals": profile.social_goals,
        }
    )


@router.patch("/profile")
def update_profile(data: UserProfileUpdate, db: Session = Depends(get_db)) -> dict:
    profile = db.execute(select(UserProfile).limit(1)).scalar_one_or_none()
    if profile is None:
        profile = UserProfile()
        db.add(profile)
    values = data.model_dump(exclude_unset=True)
    for key, value in values.items():
        setattr(profile, key, value)
    db.flush()
    return success_response(
        {
            "expression_preferences": profile.expression_preferences,
            "social_goals": profile.social_goals,
        }
    )
