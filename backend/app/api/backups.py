"""备份、恢复与导入导出 API。"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Response, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.services.backup_service import (
    create_backup,
    download_backup,
    export_conversation_markdown,
    export_json,
    export_person_markdown,
    export_topic_markdown,
    import_json,
    import_persons_csv_from_bytes,
    list_backups,
    markdown_response,
    restore_backup,
)

router = APIRouter()


@router.get("/backups")
def list_backup_records(db: Session = Depends(get_db)) -> dict:
    records = list_backups(db)
    return success_response(
        [
            {
                "id": str(record.id),
                "filename": record.filename,
                "size_bytes": record.size_bytes,
                "status": record.status,
                "created_at": record.created_at.isoformat(),
            }
            for record in records
        ]
    )


@router.post("/backups")
def create_backup_record() -> dict:
    return success_response(create_backup())


@router.post("/backups/{backup_id}/restore")
def restore_backup_record(
    backup_id: uuid.UUID, confirm: bool = Query(False)
) -> dict:
    return success_response(restore_backup(backup_id, confirm))


@router.get("/backups/{backup_id}/download")
def download_backup_file(backup_id: uuid.UUID) -> FileResponse:
    return download_backup(backup_id)


@router.get("/export/json")
def export_all_json() -> dict:
    return success_response(export_json())


@router.post("/import")
def import_all_json(payload: dict) -> dict:
    counts = import_json(payload)
    return success_response({"imported": counts})


@router.post("/import/persons-csv")
async def import_persons_csv(file: UploadFile, db: Session = Depends(get_db)) -> dict:
    data = await file.read()
    counts = import_persons_csv_from_bytes(db, data)
    return success_response(counts)


@router.get("/export/persons/{person_id}.md")
def export_person_md(person_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    content = export_person_markdown(db, person_id)
    return markdown_response(content, f"person-{person_id}.md")


@router.get("/export/topics/{topic_id}.md")
def export_topic_md(topic_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    content = export_topic_markdown(db, topic_id)
    return markdown_response(content, f"topic-{topic_id}.md")


@router.get("/export/conversations/{conversation_id}.md")
def export_conversation_md(
    conversation_id: uuid.UUID, db: Session = Depends(get_db)
) -> Response:
    content = export_conversation_markdown(db, conversation_id)
    return markdown_response(content, f"conversation-{conversation_id}.md")
