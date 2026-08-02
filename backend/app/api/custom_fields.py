"""自定义字段 API。"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.schemas.p1 import (
    CustomFieldCreate,
    CustomFieldRead,
    CustomFieldUpdate,
    CustomFieldValueUpdate,
)
from app.services.custom_field_service import CustomFieldService

router = APIRouter()


@router.get("/custom-fields")
def list_custom_fields(db: Session = Depends(get_db)) -> dict:
    fields = CustomFieldService(db).list_fields()
    return success_response([CustomFieldRead.model_validate(item) for item in fields])


@router.post("/custom-fields")
def create_custom_field(data: CustomFieldCreate, db: Session = Depends(get_db)) -> dict:
    field = CustomFieldService(db).create_field(data)
    return success_response(CustomFieldRead.model_validate(field))


@router.patch("/custom-fields/{field_id}")
def update_custom_field(
    field_id: uuid.UUID, data: CustomFieldUpdate, db: Session = Depends(get_db)
) -> dict:
    field = CustomFieldService(db).update_field(field_id, data)
    return success_response(CustomFieldRead.model_validate(field))


@router.delete("/custom-fields/{field_id}")
def delete_custom_field(field_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    CustomFieldService(db).delete_field(field_id)
    return Response(status_code=204)


@router.get("/persons/{person_id}/custom-values")
def get_custom_values(person_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    return success_response(CustomFieldService(db).get_values(person_id))


@router.put("/persons/{person_id}/custom-values")
def set_custom_values(
    person_id: uuid.UUID,
    data: CustomFieldValueUpdate,
    db: Session = Depends(get_db),
) -> dict:
    values = CustomFieldService(db).set_values(person_id, data.values)
    return success_response(values)
