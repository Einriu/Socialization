"""人物关系业务逻辑。"""

from __future__ import annotations

import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.p2 import PersonRelationship
from app.models.person import Person


def list_relationships(db: Session, person_id: uuid.UUID) -> list[dict]:
    person = db.get(Person, person_id)
    if person is None or person.deleted_at is not None:
        raise AppError("NOT_FOUND", status_code=404)
    rows = db.execute(
        select(PersonRelationship).where(
            or_(
                PersonRelationship.person_a_id == person_id,
                PersonRelationship.person_b_id == person_id,
            )
        )
    ).scalars()
    result: list[dict] = []
    for row in rows:
        other_id = row.person_b_id if row.person_a_id == person_id else row.person_a_id
        other = db.get(Person, other_id)
        result.append(
            {
                "id": str(row.id),
                "other_person_id": str(other_id),
                "other_person_name": other.name if other else "未知",
                "relation_type": row.relation_type,
                "note": row.note,
            }
        )
    return result


def create_relationship(
    db: Session,
    person_id: uuid.UUID,
    other_person_id: uuid.UUID,
    relation_type: str,
    note: str | None,
) -> dict:
    person = db.get(Person, person_id)
    other = db.get(Person, other_person_id)
    if person is None or person.deleted_at is not None:
        raise AppError("NOT_FOUND", "人物不存在", status_code=404)
    if other is None or other.deleted_at is not None:
        raise AppError("NOT_FOUND", "关联人物不存在", status_code=404)
    if person_id == other_person_id:
        raise AppError("CONFLICT", "不能与自己建立关系", status_code=409)
    duplicate = db.execute(
        select(PersonRelationship).where(
            or_(
                (PersonRelationship.person_a_id == person_id)
                & (PersonRelationship.person_b_id == other_person_id),
                (PersonRelationship.person_a_id == other_person_id)
                & (PersonRelationship.person_b_id == person_id),
            )
        )
    ).scalar_one_or_none()
    if duplicate is not None:
        raise AppError("CONFLICT", "关系已存在", status_code=409)
    row = PersonRelationship(
        person_a_id=person_id,
        person_b_id=other_person_id,
        relation_type=relation_type,
        note=note,
    )
    db.add(row)
    db.flush()
    return {
        "id": str(row.id),
        "other_person_id": str(other_person_id),
        "other_person_name": other.name,
        "relation_type": relation_type,
        "note": note,
    }


def delete_relationship(db: Session, relationship_id: uuid.UUID) -> None:
    row = db.get(PersonRelationship, relationship_id)
    if row is None:
        raise AppError("NOT_FOUND", status_code=404)
    db.delete(row)
    db.flush()
