"""间隔复习业务逻辑。"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.p2 import ReviewTask, TopicLearningRecord
from app.models.topic import Topic

INTERVALS = {"忘记": 1, "模糊": 3, "掌握": 7, "非常熟练": 30}


def list_due_reviews(db: Session) -> list[dict]:
    now = datetime.now(UTC)
    rows = db.execute(
        select(ReviewTask, Topic)
        .join(Topic, Topic.id == ReviewTask.topic_id)
        .where(ReviewTask.due_at <= now, Topic.deleted_at.is_(None))
        .order_by(ReviewTask.due_at.asc())
    ).all()
    return [
        {
            "id": str(task.id),
            "topic_id": str(topic.id),
            "topic_name": topic.name,
            "due_at": task.due_at.isoformat(),
            "interval_days": task.interval_days,
        }
        for task, topic in rows
    ]


def list_reviews(db: Session) -> list[dict]:
    rows = db.execute(
        select(ReviewTask, Topic)
        .join(Topic, Topic.id == ReviewTask.topic_id)
        .order_by(ReviewTask.due_at.desc())
    ).all()
    return [
        {
            "id": str(task.id),
            "topic_id": str(topic.id),
            "topic_name": topic.name,
            "due_at": task.due_at.isoformat(),
            "last_reviewed_at": task.last_reviewed_at.isoformat()
            if task.last_reviewed_at
            else None,
        }
        for task, topic in rows
    ]


def ensure_task_for_topic(db: Session, topic_id: uuid.UUID) -> None:
    """话题学习/更新时确保存在复习任务。"""
    existing = db.execute(
        select(ReviewTask).where(ReviewTask.topic_id == topic_id)
    ).scalar_one_or_none()
    if existing is None:
        db.add(ReviewTask(topic_id=topic_id, due_at=datetime.now(UTC) + timedelta(days=1)))
        db.flush()


def answer_review(db: Session, task_id: uuid.UUID, rating: str) -> dict:
    task = db.get(ReviewTask, task_id)
    if task is None:
        raise AppError("NOT_FOUND", status_code=404)
    days = INTERVALS.get(rating)
    if days is None:
        raise AppError("VALIDATION_ERROR", f"未知的复习反馈：{rating}", status_code=400)
    now = datetime.now(UTC)
    task.last_reviewed_at = now
    task.interval_days = days
    task.due_at = now + timedelta(days=days)
    topic = db.get(Topic, task.topic_id)
    if topic is not None:
        topic.last_reviewed_at = now
        db.add(
            TopicLearningRecord(
                topic_id=task.topic_id,
                learned_at=now,
                mastery_level=topic.mastery_level,
                note=f"复习反馈：{rating}",
            )
        )
    db.flush()
    return {"next_due_at": task.due_at.isoformat(), "interval_days": days}
