"""应用配置（Pydantic Settings，环境变量驱动）。"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """从环境变量或项目根目录 .env 读取的全局配置。"""

    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Socialization"
    app_version: str = "0.1.0"
    database_url: str = "sqlite:///data/socialization.db"
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    frontend_port: int = 3000
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://127.0.0.1:3000", "http://localhost:3000"]
    )
    log_level: str = "INFO"

    @field_validator("database_url", mode="after")
    @classmethod
    def _resolve_sqlite_path(cls, value: str) -> str:
        """将相对路径的 SQLite URL 解析为项目根目录下的绝对路径。"""
        prefix = "sqlite:///"
        if value.startswith(prefix):
            raw = value[len(prefix) :]
            if not os.path.isabs(raw):
                raw = str(REPO_ROOT / raw)
            return f"{prefix}{raw.replace(os.sep, '/')}"
        return value


@lru_cache
def get_settings() -> Settings:
    """返回缓存的 Settings 实例。"""
    return Settings()
