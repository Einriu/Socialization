"""文本切分：按段落累积，保留重叠。"""

from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 700, overlap: int = 100) -> list[str]:
    """将文本切分为约 chunk_size 字符的片段，相邻片段保留 overlap 重叠。"""
    if not text:
        return []
    paragraphs = [p.strip() for p in text.splitlines() if p.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(current) + len(paragraph) + 1 <= chunk_size:
            current = f"{current}\n{paragraph}".strip()
            continue
        if current:
            chunks.append(current)
        # 段落自身超过上限时按字符切
        if len(paragraph) > chunk_size:
            start = 0
            while start < len(paragraph):
                end = min(start + chunk_size, len(paragraph))
                chunks.append(paragraph[start:end])
                start = end - overlap if end < len(paragraph) else end
            current = ""
            continue
        current = paragraph
    if current:
        chunks.append(current)
    if overlap > 0 and len(chunks) > 1:
        merged: list[str] = []
        for i, chunk in enumerate(chunks):
            if i == 0:
                merged.append(chunk)
                continue
            prev = merged[-1]
            tail = prev[-overlap:] if len(prev) >= overlap else prev
            merged.append(f"{tail}{chunk}")
        chunks = merged
    return [chunk.strip() for chunk in chunks if chunk.strip()]
