"""统一响应格式：{code, message, data}。"""

from __future__ import annotations

from typing import Any


def success_response(data: Any = None, message: str = "ok") -> dict[str, Any]:
    """成功响应。code 恒为 0。"""
    return {"code": 0, "message": message, "data": data}


def error_response(code: str, message: str, data: Any = None) -> dict[str, Any]:
    """错误响应。code 为稳定错误码，message 为用户可读信息。"""
    return {"code": code, "message": message, "data": data}
