"""人物、事实、重要日期、待跟进与时间线 API。"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.schemas.common import Page
from app.schemas.person import (
    FollowUpCreate,
    FollowUpRead,
    FollowUpUpdate,
    ImportantDateCreate,
    ImportantDateRead,
    ImportantDateUpdate,
    PersonCreate,
    PersonFactCreate,
    PersonFactRead,
    PersonFactUpdate,
    PersonRead,
    PersonUpdate,
    TimelineItem,
)
from app.schemas.tag import PersonTagsUpdate
from app.services.person_service import PersonService
from app.services.social_service import generate_briefing

router = APIRouter()


@router.get("/persons")
def list_persons(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = None,
    tag_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
) -> dict:
    items, total = PersonService(db).list_persons(page, page_size, q, tag_id)
    payload = Page[PersonRead](
        items=[PersonRead.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return success_response(payload)


@router.post("/persons")
def create_person(data: PersonCreate, db: Session = Depends(get_db)) -> dict:
    person = PersonService(db).create_person(data)
    return success_response(PersonRead.model_validate(person))


@router.get("/persons/{person_id}")
def get_person(person_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    person = PersonService(db).get_person(person_id)
    return success_response(PersonRead.model_validate(person))


@router.patch("/persons/{person_id}")
def update_person(
    person_id: uuid.UUID, data: PersonUpdate, db: Session = Depends(get_db)
) -> dict:
    person = PersonService(db).update_person(person_id, data)
    return success_response(PersonRead.model_validate(person))


@router.delete("/persons/{person_id}")
def delete_person(person_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    PersonService(db).delete_person(person_id)
    return Response(status_code=204)


@router.delete("/persons/{person_id}/permanent")
def permanent_delete_person(
    person_id: uuid.UUID,
    confirm: bool = Query(False),
    db: Session = Depends(get_db),
) -> Response:
    PersonService(db).permanent_delete_person(person_id, confirm)
    return Response(status_code=204)


@router.put("/persons/{person_id}/tags")
def set_person_tags(
    person_id: uuid.UUID, data: PersonTagsUpdate, db: Session = Depends(get_db)
) -> dict:
    person = PersonService(db).set_person_tags(person_id, data.tag_ids)
    return success_response(PersonRead.model_validate(person))


@router.get("/persons/{person_id}/timeline")
def get_timeline(
    person_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    items, total = PersonService(db).get_timeline(person_id, page, page_size)
    payload = Page[TimelineItem](items=items, total=total, page=page, page_size=page_size)
    return success_response(payload)


@router.get("/persons/{person_id}/facts")
def list_facts(
    person_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    items, total = PersonService(db).list_facts(person_id, page, page_size)
    payload = Page[PersonFactRead](
        items=[PersonFactRead.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return success_response(payload)


@router.post("/persons/{person_id}/facts")
def create_fact(
    person_id: uuid.UUID, data: PersonFactCreate, db: Session = Depends(get_db)
) -> dict:
    fact = PersonService(db).create_fact(person_id, data)
    return success_response(PersonFactRead.model_validate(fact))


@router.patch("/person-facts/{fact_id}")
def update_fact(
    fact_id: uuid.UUID, data: PersonFactUpdate, db: Session = Depends(get_db)
) -> dict:
    fact = PersonService(db).update_fact(fact_id, data)
    return success_response(PersonFactRead.model_validate(fact))


@router.delete("/person-facts/{fact_id}")
def delete_fact(fact_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    PersonService(db).delete_fact(fact_id)
    return Response(status_code=204)


@router.get("/persons/{person_id}/dates")
def list_dates(
    person_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    items, total = PersonService(db).list_dates(person_id, page, page_size)
    payload = Page[ImportantDateRead](
        items=[ImportantDateRead.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return success_response(payload)


@router.post("/persons/{person_id}/dates")
def create_date(
    person_id: uuid.UUID, data: ImportantDateCreate, db: Session = Depends(get_db)
) -> dict:
    item = PersonService(db).create_date(person_id, data)
    return success_response(ImportantDateRead.model_validate(item))


@router.patch("/important-dates/{date_id}")
def update_date(
    date_id: uuid.UUID, data: ImportantDateUpdate, db: Session = Depends(get_db)
) -> dict:
    item = PersonService(db).update_date(date_id, data)
    return success_response(ImportantDateRead.model_validate(item))


@router.delete("/important-dates/{date_id}")
def delete_date(date_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    PersonService(db).delete_date(date_id)
    return Response(status_code=204)


@router.get("/persons/{person_id}/follow-ups")
def list_follow_ups(
    person_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    completed: bool | None = None,
    db: Session = Depends(get_db),
) -> dict:
    items, total = PersonService(db).list_follow_ups(
        person_id, page, page_size, completed
    )
    payload = Page[FollowUpRead](
        items=[FollowUpRead.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return success_response(payload)


@router.post("/persons/{person_id}/briefing")
async def briefing(person_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    text = await generate_briefing(db, person_id)
    return success_response({"briefing": text})


@router.post("/persons/{person_id}/follow-ups")
def create_follow_up(
    person_id: uuid.UUID, data: FollowUpCreate, db: Session = Depends(get_db)
) -> dict:
    item = PersonService(db).create_follow_up(person_id, data)
    return success_response(FollowUpRead.model_validate(item))


@router.patch("/follow-up-tasks/{task_id}")
def update_follow_up(
    task_id: uuid.UUID, data: FollowUpUpdate, db: Session = Depends(get_db)
) -> dict:
    item = PersonService(db).update_follow_up(task_id, data)
    return success_response(FollowUpRead.model_validate(item))


@router.delete("/follow-up-tasks/{task_id}")
def delete_follow_up(task_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    PersonService(db).delete_follow_up(task_id)
    return Response(status_code=204)
