"""文件资料库 API。"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Response, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.models.p1 import Document, DocumentChunk, DocumentLink
from app.schemas.common import Page
from app.schemas.p1 import DocumentChunkRead, DocumentLinksUpdate, DocumentRead
from app.services.document_service import DocumentService

router = APIRouter()


def _document_read(db: Session, document: Document) -> DocumentRead:
    chunk_count = len(
        db.execute(
            select(DocumentChunk.id).where(DocumentChunk.document_id == document.id)
        ).all()
    )
    links = db.execute(
        select(DocumentLink).where(DocumentLink.document_id == document.id)
    ).scalars()
    person_ids = [link.person_id for link in links if link.person_id]
    topic_ids = [link.topic_id for link in links if link.topic_id]
    return DocumentRead.model_validate(document).model_copy(
        update={
            "chunk_count": chunk_count,
            "person_ids": person_ids,
            "topic_ids": topic_ids,
        }
    )


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile,
    db: Session = Depends(get_db),
) -> dict:
    data = await file.read()
    document = DocumentService(db).upload(file.filename or "unnamed", data)
    if document.status == "pending":
        document = DocumentService(db).process(document.id)
    return success_response(_document_read(db, document))


@router.get("/documents")
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    person_id: uuid.UUID | None = None,
    topic_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
) -> dict:
    items, total = DocumentService(db).list_documents(
        page, page_size, person_id, topic_id
    )
    payload = Page[DocumentRead](
        items=[_document_read(db, item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return success_response(payload)


@router.get("/documents/{document_id}")
def get_document(document_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    document = DocumentService(db).get_document(document_id)
    return success_response(_document_read(db, document))


@router.delete("/documents/{document_id}")
def delete_document(document_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    DocumentService(db).delete_document(document_id)
    return Response(status_code=204)


@router.post("/documents/{document_id}/process")
def process_document(document_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    document = DocumentService(db).process(document_id)
    return success_response(_document_read(db, document))


@router.post("/documents/{document_id}/reprocess")
def reprocess_document(document_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    document = DocumentService(db).process(document_id)
    return success_response(_document_read(db, document))


@router.get("/documents/{document_id}/chunks")
def list_chunks(
    document_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    items, total = DocumentService(db).list_chunks(document_id, page, page_size)
    payload = Page[DocumentChunkRead](
        items=[DocumentChunkRead.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return success_response(payload)


@router.put("/documents/{document_id}/links")
def set_document_links(
    document_id: uuid.UUID,
    data: DocumentLinksUpdate,
    db: Session = Depends(get_db),
) -> dict:
    document = DocumentService(db).set_links(document_id, data)
    return success_response(_document_read(db, document))
