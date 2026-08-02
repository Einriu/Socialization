"""FastAPI 应用入口。"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401  # 注册全部 ORM 元数据
from app.api import health, interactions, persons, tags
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
    return app


app = create_app()
