"""知识库检索：FTS5 关键词 + 范围过滤，返回片段与引用。"""

from __future__ import annotations

import uuid

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models.p1 import Document, DocumentChunk


def _fts_query(query: str) -> str:
    terms = [term for term in query.replace("，", " ").replace("。", " ").split() if term]
    return " OR ".join(f'"{term}"*' for term in terms[:8]) if terms else query


def retrieve_chunks(
    db: Session,
    query: str,
    *,
    document_ids: list[uuid.UUID] | None = None,
    person_ids: list[uuid.UUID] | None = None,
    topic_ids: list[uuid.UUID] | None = None,
    top_k: int = 5,
) -> list[dict]:
    """返回 [{chunk_id, document_id, document_name, chunk_index, content, score}]。"""
    from app.services.document_service import DocumentService

    scope_ids = document_ids or []
    if person_ids or topic_ids:
        scope_ids += DocumentService(db).linked_document_ids(
            person_ids or [], topic_ids or []
        )
    scope_ids = list(dict.fromkeys(scope_ids))

    match = _fts_query(query)
    rows: list[tuple[uuid.UUID, float]] = []
    try:
        result = db.execute(
            text(
                "SELECT id, bm25(fts_documents) AS rank FROM fts_documents "
                "WHERE fts_documents MATCH :q ORDER BY rank LIMIT :limit"
            ),
            {"q": match, "limit": 60},
        )
        rows = [(uuid.UUID(str(row[0])), float(row[1])) for row in result]
    except Exception:  # noqa: BLE001 - FTS 语法错误时回退为空
        rows = []

    if not rows:
        # LIKE 兜底：覆盖中文短词
        like_chunks = db.execute(
            select(DocumentChunk).where(
                DocumentChunk.content.ilike(f"%{query}%")
            ).limit(30)
        ).scalars()
        rows = [(chunk.id, 0.5) for chunk in like_chunks]

    candidates: list[tuple[DocumentChunk, float]] = []
    seen: set[uuid.UUID] = set()
    for chunk_id, rank in rows:
        chunk = db.get(DocumentChunk, chunk_id)
        if chunk is None or chunk.document_id in seen:
            continue
        if scope_ids and chunk.document_id not in scope_ids:
            continue
        seen.add(chunk.document_id)
        # bm25 返回负分，越小越相关；转换为正分数
        candidates.append((chunk, max(0.0, -rank)))

    # 有显式范围时，若关键词结果不足，补充范围文件的靠前片段
    if len(candidates) < top_k and scope_ids:
        for doc_id in scope_ids:
            fallback = db.execute(
                select(DocumentChunk)
                .where(DocumentChunk.document_id == doc_id)
                .order_by(DocumentChunk.chunk_index.asc())
                .limit(3)
            ).scalars()
            for chunk in fallback:
                if all(item[0].id != chunk.id for item in candidates):
                    candidates.append((chunk, 0.0))

    candidates.sort(key=lambda item: item[1], reverse=True)

    # 可选向量混合：查询可嵌入且片段有向量时，0.65*cosine + 0.35*关键词分
    if candidates:
        from app.services.embedding_service import embed_texts

        query_embedding = embed_texts(db, [query])
        if query_embedding is not None and query_embedding[0]:
            query_vec = query_embedding[0]
            max_kw = max((item[1] for item in candidates), default=1.0) or 1.0
            scored: list[tuple[DocumentChunk, float]] = []
            for chunk, kw_score in candidates:
                cosine = 0.0
                if chunk.embedding:
                    vec = chunk.embedding
                    dot = sum(a * b for a, b in zip(query_vec, vec, strict=False))
                    norm_q = sum(a * a for a in query_vec) ** 0.5
                    norm_c = sum(b * b for b in vec) ** 0.5
                    if norm_q and norm_c:
                        cosine = dot / (norm_q * norm_c)
                kw_norm = kw_score / max_kw
                scored.append((chunk, 0.65 * cosine + 0.35 * kw_norm))
            candidates = scored
    candidates.sort(key=lambda item: item[1], reverse=True)
    results: list[dict] = []
    for chunk, score in candidates[:top_k]:
        document = db.get(Document, chunk.document_id)
        results.append(
            {
                "chunk_id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "document_name": document.filename if document else "未知文件",
                "chunk_index": chunk.chunk_index,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "content": chunk.content[:800],
                "score": round(score, 4),
            }
        )
    return results
