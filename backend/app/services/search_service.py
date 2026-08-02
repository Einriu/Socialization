"""全局搜索：FTS5（笔记/文件）+ LIKE（人物/话题/互动）。"""

from __future__ import annotations

from sqlalchemy import or_, select, text
from sqlalchemy.orm import Session

from app.models.interaction import Interaction
from app.models.p1 import Document, DocumentChunk
from app.models.person import Person
from app.models.topic import Topic, TopicNote


def search(db: Session, q: str, limit: int = 20) -> dict:
    pattern = f"%{q.strip()}%"
    persons = [
        {"id": str(p.id), "name": p.name, "type": "person"}
        for p in db.execute(
            select(Person).where(
                Person.deleted_at.is_(None),
                or_(
                    Person.name.ilike(pattern),
                    Person.nickname.ilike(pattern),
                    Person.organization.ilike(pattern),
                    Person.occupation.ilike(pattern),
                ),
            )
            .limit(limit)
        ).scalars()
    ]
    topics = [
        {"id": str(t.id), "name": t.name, "type": "topic"}
        for t in db.execute(
            select(Topic).where(
                Topic.deleted_at.is_(None),
                or_(Topic.name.ilike(pattern), Topic.description.ilike(pattern)),
            )
            .limit(limit)
        ).scalars()
    ]
    interactions = [
        {"id": str(i.id), "title": i.title, "type": "interaction"}
        for i in db.execute(
            select(Interaction).where(
                Interaction.deleted_at.is_(None),
                or_(Interaction.title.ilike(pattern), Interaction.summary.ilike(pattern)),
            )
            .limit(limit)
        ).scalars()
    ]
    notes: list[dict] = []
    documents: list[dict] = []
    try:
        terms = [t for t in q.replace("，", " ").split() if t]
        match = " OR ".join(f'"{t}"*' for t in terms[:8]) if terms else q
        note_rows = db.execute(
            text(
                "SELECT id, bm25(fts_notes) AS rank FROM fts_notes "
                "WHERE fts_notes MATCH :q ORDER BY rank LIMIT :limit"
            ),
            {"q": match, "limit": limit},
        )
        for row in note_rows:
            topic = db.get(Topic, uuid_from_row(row[0]))
            if topic is not None:
                notes.append({"id": str(topic.id), "name": topic.name, "type": "note"})
        doc_rows = db.execute(
            text(
                "SELECT id, bm25(fts_documents) AS rank FROM fts_documents "
                "WHERE fts_documents MATCH :q ORDER BY rank LIMIT :limit"
            ),
            {"q": match, "limit": limit},
        )
        for row in doc_rows:
            documents.append({"id": str(row[0]), "name": "文件片段", "type": "document"})
    except Exception:  # noqa: BLE001 - 搜索失败不阻断
        pass
    # LIKE 兜底：覆盖中文短词（FTS5 无中文分词器）
    seen_note_ids = {item["id"] for item in notes}
    if not notes:
        note_rows = db.execute(
            select(TopicNote).where(TopicNote.plain_text.ilike(pattern)).limit(limit)
        ).scalars()
        for note in note_rows:
            topic = db.get(Topic, note.topic_id)
            if topic is not None and str(topic.id) not in seen_note_ids:
                notes.append({"id": str(topic.id), "name": topic.name, "type": "note"})
                seen_note_ids.add(str(topic.id))
    seen_doc_ids = {item["id"] for item in documents}
    if not documents:
        chunk_rows = db.execute(
            select(DocumentChunk.document_id)
            .where(DocumentChunk.content.ilike(pattern))
            .limit(limit)
        ).scalars()
        for doc_id in chunk_rows:
            if str(doc_id) in seen_doc_ids:
                continue
            document = db.get(Document, doc_id)
            if document is not None:
                documents.append(
                    {"id": str(doc_id), "name": document.filename, "type": "document"}
                )
                seen_doc_ids.add(str(doc_id))
    return {
        "persons": persons,
        "topics": topics,
        "interactions": interactions,
        "notes": notes,
        "documents": documents,
    }


def uuid_from_row(value: object) -> object:
    import uuid

    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError):
        return None
