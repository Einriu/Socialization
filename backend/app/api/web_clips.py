"""网页收藏 API。"""

from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AppError
from app.core.response import success_response
from app.parsers.base import parse_html_text
from app.services.document_service import DocumentService

router = APIRouter()


class WebClipCreate(BaseModel):
    url: str = Field(min_length=1)
    title: str | None = None


@router.post("/web-clips")
def save_web_clip(data: WebClipCreate, db: Session = Depends(get_db)) -> dict:
    try:
        response = httpx.get(
            data.url,
            timeout=15,
            follow_redirects=True,
            headers={"User-Agent": "Socialization/0.1"},
        )
        response.raise_for_status()
    except Exception as exc:  # noqa: BLE001 - 网络失败统一提示
        raise AppError(
            "AI_PROVIDER_ERROR",
            f"抓取网页失败：{type(exc).__name__}",
            status_code=400,
        ) from exc
    text = parse_html_text(response.text)
    if not text.strip():
        raise AppError("VALIDATION_ERROR", "网页没有可收藏的文字内容", status_code=400)
    host = data.url.split("//")[-1].split("/")[0]
    filename = f"{data.title or host}.html"
    document = DocumentService(db).upload(filename, response.text.encode("utf-8"))
    document = DocumentService(db).process(document.id)
    return success_response(
        {
            "id": str(document.id),
            "filename": document.filename,
            "status": document.status,
        }
    )
