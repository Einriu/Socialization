"""文件上传、解析、切分与关联业务逻辑。"""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.models.p1 import Document, DocumentChunk, DocumentLink, DocumentVersion, ProcessingJob
from app.models.person import Person
from app.models.topic import Topic
from app.parsers.base import parse_file
from app.parsers.chunking import chunk_text
from app.repositories.base import BaseRepository
from app.schemas.p1 import DocumentLinksUpdate
from app.services.ai_media_service import AUDIO_EXTS, IMAGE_EXTS, ocr_media, transcribe_media


class DocumentRepository(BaseRepository[Document]):
    model = Document


_EXT_MIME = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".html": "text/html",
    ".htm": "text/html",
    ".csv": "text/csv",
    ".json": "application/json",
}


def _uploads_dir() -> Path:
    path = Path(get_settings().data_dir) / "uploads"
    path.mkdir(parents=True, exist_ok=True)
    return path


class DocumentService:
    """文件服务。"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.documents = DocumentRepository(db)

    def _load(self, document_id: uuid.UUID) -> Document:
        document = self.db.execute(
            select(Document).where(
                Document.id == document_id, Document.deleted_at.is_(None)
            )
        ).scalar_one_or_none()
        if document is None:
            raise AppError("NOT_FOUND", status_code=404)
        return document

    def upload(self, filename: str, data: bytes) -> Document:
        """保存原始文件；相同 sha256 且已解析完成时去重返回。"""
        sha256 = hashlib.sha256(data).hexdigest()
        existing = self.db.execute(
            select(Document).where(
                Document.sha256 == sha256,
                Document.deleted_at.is_(None),
                Document.status == "completed",
            )
        ).scalar_one_or_none()
        if existing is not None:
            return existing

        ext = Path(filename).suffix.lower()
        stored_name = f"{uuid.uuid4().hex}{ext}"
        file_path = _uploads_dir() / stored_name
        file_path.write_bytes(data)

        document = Document(
            filename=filename,
            file_path=str(file_path),
            file_size=len(data),
            mime_type=_EXT_MIME.get(ext),
            sha256=sha256,
            status="pending",
        )
        self.documents.create(document)
        self.db.add(
            DocumentVersion(
                document_id=document.id,
                version=document.parse_version,
                file_path=str(file_path),
                file_size=len(data),
                sha256=sha256,
            )
        )
        self.db.flush()
        return document

    def process(self, document_id: uuid.UUID) -> Document:
        """解析文件并切块；解析失败保留状态与错误信息。"""
        document = self._load(document_id)
        document.status = "processing"
        job = ProcessingJob(document_id=document_id, job_type="parse", status="running")
        self.db.add(job)
        self.db.flush()
        try:
            parsed = parse_file(Path(document.file_path))
            if parsed.error:
                raise RuntimeError(parsed.error)
            if not parsed.text.strip():
                ext = Path(document.file_path).suffix.lower()
                if ext in IMAGE_EXTS:
                    text = ocr_media(self.db, Path(document.file_path))
                elif ext in AUDIO_EXTS:
                    text = transcribe_media(self.db, Path(document.file_path))
                else:
                    text = None
                if text:
                    parsed.text = text
            self._replace_chunks(document, parsed)
            document.status = "completed"
            document.error_message = None
            job.status = "completed"
        except Exception as exc:  # noqa: BLE001 - 解析失败记录错误
            document.status = "failed"
            document.error_message = str(exc)[:500]
            job.status = "failed"
            job.error_message = str(exc)[:500]
        from app.models.base import utcnow

        job.finished_at = utcnow()
        self.db.flush()
        return document

    def _replace_chunks(self, document: Document, parsed: object) -> None:
        for old in self.db.execute(
            select(DocumentChunk).where(DocumentChunk.document_id == document.id)
        ).scalars():
            self.db.delete(old)
        self.db.flush()
        chunks = chunk_text(parsed.text)
        embeddings: list[list[float]] | None = None
        if chunks:
            from app.services.embedding_service import embed_texts

            embeddings = embed_texts(self.db, chunks[:64])
        for index, content in enumerate(chunks):
            self.db.add(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=content,
                    token_count=max(1, len(content) // 4),
                    embedding=embeddings[index] if embeddings is not None else None,
                    metadata={"chunk_size": len(content)},
                )
            )
        self.db.flush()
        self._rebuild_fts(document.id)

    def _rebuild_fts(self, document_id: uuid.UUID) -> None:
        """重建该文件的 FTS 索引（代码手动维护，避免触发器 rowid 问题）。"""
        self.db.execute(
            text("DELETE FROM fts_documents WHERE document_id = :did"),
            {"did": str(document_id)},
        )
        chunks = self.db.execute(
            select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        ).scalars()
        for chunk in chunks:
            self.db.execute(
                text(
                    "INSERT INTO fts_documents(content, document_id, chunk_index, id) "
                    "VALUES (:content, :did, :index, :id)"
                ),
                {
                    "content": chunk.content,
                    "did": str(document_id),
                    "index": chunk.chunk_index,
                    "id": str(chunk.id),
                },
            )

    def list_documents(
        self,
        page: int,
        page_size: int,
        person_id: uuid.UUID | None,
        topic_id: uuid.UUID | None,
    ) -> tuple[list[Document], int]:
        stmt = select(Document).where(Document.deleted_at.is_(None))
        if person_id is not None:
            stmt = stmt.join(DocumentLink).where(DocumentLink.person_id == person_id)
        if topic_id is not None:
            stmt = stmt.join(DocumentLink).where(DocumentLink.topic_id == topic_id)
        total = self.db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
        rows = (
            self.db.execute(
                stmt.order_by(Document.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .scalars()
            .all()
        )
        return list(rows), int(total)

    def get_document(self, document_id: uuid.UUID) -> Document:
        return self._load(document_id)

    def list_chunks(
        self, document_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[DocumentChunk], int]:
        self._load(document_id)
        stmt = select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        total = self.db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
        rows = (
            self.db.execute(
                stmt.order_by(DocumentChunk.chunk_index.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .scalars()
            .all()
        )
        return list(rows), int(total)

    def delete_document(self, document_id: uuid.UUID) -> None:
        if not self.documents.soft_delete(document_id):
            raise AppError("NOT_FOUND", status_code=404)

    def set_links(
        self, document_id: uuid.UUID, data: DocumentLinksUpdate
    ) -> Document:
        self._load(document_id)
        for row in self.db.execute(
            select(DocumentLink).where(DocumentLink.document_id == document_id)
        ).scalars():
            if row.conversation_id is None:
                self.db.delete(row)
        if data.person_id is not None:
            if self.db.get(Person, data.person_id) is None:
                raise AppError("NOT_FOUND", "人物不存在", status_code=404)
            self.db.add(DocumentLink(document_id=document_id, person_id=data.person_id))
        if data.topic_id is not None:
            if self.db.get(Topic, data.topic_id) is None:
                raise AppError("NOT_FOUND", "话题不存在", status_code=404)
            self.db.add(DocumentLink(document_id=document_id, topic_id=data.topic_id))
        self.db.flush()
        self.db.expire_all()
        return self._load(document_id)

    def linked_document_ids(
        self, person_ids: list[uuid.UUID], topic_ids: list[uuid.UUID]
    ) -> list[uuid.UUID]:
        if not person_ids and not topic_ids:
            return []
        stmt = select(DocumentLink.document_id).where(
            (DocumentLink.person_id.in_(person_ids))
            | (DocumentLink.topic_id.in_(topic_ids))
        )
        return list(self.db.execute(stmt).scalars())
