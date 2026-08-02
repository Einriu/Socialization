"""FastAPI 应用入口。"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import app.models  # noqa: F401  # 注册全部 ORM 元数据
from app.api import (
    backups,
    conversations,
    custom_fields,
    dashboard,
    documents,
    health,
    interactions,
    memory,
    persons,
    practice,
    providers,
    reviews,
    search,
    tags,
    topics,
    web_clips,
)
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging

setup_logging(get_settings().log_level)


def create_app() -> FastAPI:
    """应用工厂：装配中间件、异常处理器与路由。"""
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(health.router, prefix="/api")
    app.include_router(persons.router, prefix="/api")
    app.include_router(tags.router, prefix="/api")
    app.include_router(interactions.router, prefix="/api")
    app.include_router(topics.router, prefix="/api")
    app.include_router(providers.router, prefix="/api")
    app.include_router(conversations.router, prefix="/api")
    app.include_router(backups.router, prefix="/api")
    app.include_router(documents.router, prefix="/api")
    app.include_router(search.router, prefix="/api")
    app.include_router(custom_fields.router, prefix="/api")
    app.include_router(practice.router, prefix="/api")
    app.include_router(reviews.router, prefix="/api")
    app.include_router(memory.router, prefix="/api")
    app.include_router(dashboard.router, prefix="/api")
    app.include_router(web_clips.router, prefix="/api")
    _mount_frontend(app)
    return app


def _mount_frontend(app: FastAPI) -> None:
    """生产模式：挂载 frontend/dist（含桌面打包场景）。"""
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS) / "frontend_dist"  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parents[1] / "frontend" / "dist"
    if not (base / "index.html").exists():
        return
    assets = base / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=str(assets)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str) -> FileResponse:
        target = base / full_path
        if full_path and target.is_file():
            return FileResponse(target)
        return FileResponse(base / "index.html")


app = create_app()
