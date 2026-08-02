"""长期记忆与仪表盘统计。"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.interaction import Interaction
from app.models.p1 import Document
from app.models.p2 import MemoryItem
from app.models.person import FollowUpTask, Person
from app.models.topic import Topic
from app.schemas.p2 import MemoryCreate, MemoryUpdate
from app.services.review_service import list_due_reviews
from app.services.social_service import _chat


def list_memory(db: Session) -> list[MemoryItem]:
    return list(
        db.execute(
            select(MemoryItem).order_by(MemoryItem.created_at.desc()).limit(100)
        ).scalars()
    )


def create_memory(db: Session, data: MemoryCreate) -> MemoryItem:
    item = MemoryItem(**data.model_dump())
    db.add(item)
    db.flush()
    return item


def update_memory(db: Session, item_id: uuid.UUID, data: MemoryUpdate) -> MemoryItem:
    item = db.get(MemoryItem, item_id)
    if item is None:
        raise AppError("NOT_FOUND", status_code=404)
    values = data.model_dump(exclude_unset=True)
    for key, value in values.items():
        setattr(item, key, value)
    db.flush()
    return item


def accepted_memory_lines(db: Session) -> list[str]:
    rows = db.execute(
        select(MemoryItem).where(MemoryItem.status == "accepted")
    ).scalars()
    return [f"- {item.content}" for item in rows]


def dashboard(db: Session) -> dict:
    persons = int(
        db.execute(
            select(func.count()).select_from(Person).where(Person.deleted_at.is_(None))
        ).scalar_one()
    )
    interactions = int(
        db.execute(
            select(func.count())
            .select_from(Interaction)
            .where(Interaction.deleted_at.is_(None))
        ).scalar_one()
    )
    topics = int(
        db.execute(
            select(func.count()).select_from(Topic).where(Topic.deleted_at.is_(None))
        ).scalar_one()
    )
    documents = int(
        db.execute(
            select(func.count())
            .select_from(Document)
            .where(Document.deleted_at.is_(None))
        ).scalar_one()
    )
    followup_rows = db.execute(
        select(FollowUpTask, Person.name)
        .join(Person, Person.id == FollowUpTask.person_id)
        .where(
            FollowUpTask.deleted_at.is_(None),
            FollowUpTask.completed.is_(False),
            FollowUpTask.person_id.is_not(None),
        )
        .order_by(FollowUpTask.created_at.desc())
        .limit(10)
    ).all()
    recent = db.execute(
        select(Interaction)
        .where(Interaction.deleted_at.is_(None))
        .order_by(Interaction.occurred_at.desc())
        .limit(5)
    ).scalars()
    return {
        "persons": persons,
        "interactions": interactions,
        "topics": topics,
        "documents": documents,
        "due_followups": [
            {"id": str(task.id), "title": task.title, "person_name": name}
            for task, name in followup_rows
        ],
        "due_reviews": list_due_reviews(db),
        "recent_interactions": [
            {"id": str(item.id), "title": item.title, "occurred_at": item.occurred_at.isoformat()}
            for item in recent
        ],
    }


async def weekly_report(db: Session) -> str:
    week_start = datetime.now(UTC) - timedelta(days=7)
    rows = db.execute(
        select(Interaction)
        .where(Interaction.deleted_at.is_(None), Interaction.occurred_at >= week_start)
        .order_by(Interaction.occurred_at.desc())
    ).scalars()
    content = "\n".join(
        [
            f"- {item.occurred_at.isoformat()} {item.title}（{item.summary or ''}）"
            for item in rows
        ]
    ) or "（本周暂无互动）"
    return await _chat(db, "weekly_report", f"本周互动记录：\n{content}\n请生成本周成长报告。")
