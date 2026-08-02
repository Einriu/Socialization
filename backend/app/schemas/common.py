"""通用 Schema：分页结果。"""

from __future__ import annotations

from pydantic import BaseModel


class Page[T](BaseModel):
    """统一分页结果。"""

    items: list[T]
    total: int
    page: int
    page_size: int
