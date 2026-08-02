"""系统健康检查 API。"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.database import check_database
from app.core.exceptions import AppError
from app.core.response import success_response

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
def health() -> dict[str, Any]:
    """返回应用版本、SQLite 连接状态、SELECT 1 结果与 journal_mode。"""
    settings = get_settings()
    try:
        database = check_database()
    except Exception:
        logger.exception("健康检查失败：数据库不可用")
        raise AppError("DATABASE_UNAVAILABLE", status_code=503) from None
    return success_response(
        {
            "version": settings.app_version,
            "app_name": settings.app_name,
            "database": database,
        }
    )
