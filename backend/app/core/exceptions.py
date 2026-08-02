"""统一异常类型与 FastAPI 异常处理器。"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.response import error_response

logger = logging.getLogger(__name__)

ERROR_MESSAGES: dict[str, str] = {
    "NOT_FOUND": "资源不存在",
    "METHOD_NOT_ALLOWED": "请求方法不允许",
    "UNAUTHORIZED": "未授权",
    "FORBIDDEN": "禁止访问",
    "CONFLICT": "资源状态冲突",
    "VALIDATION_ERROR": "请求参数校验失败",
    "DATABASE_UNAVAILABLE": "数据库不可用",
    "AI_PROVIDER_ERROR": "AI 提供商调用失败",
    "INTERNAL_ERROR": "服务器内部错误",
}

_HTTP_CODE_MAPPING: dict[int, str] = {
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
}


class AppError(Exception):
    """业务异常，携带稳定错误码与 HTTP 状态码。"""

    def __init__(self, code: str, message: str | None = None, status_code: int = 400) -> None:
        self.code = code
        self.message = message or ERROR_MESSAGES.get(code, code)
        self.status_code = status_code
        super().__init__(self.message)


def register_exception_handlers(app: FastAPI) -> None:
    """在应用上注册统一异常处理器。"""

    @app.exception_handler(AppError)
    async def handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(exc.code, exc.message),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = _HTTP_CODE_MAPPING.get(exc.status_code, str(exc.status_code))
        message = ERROR_MESSAGES.get(code, str(exc.detail))
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(code, message),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details: Any = [
            {key: value for key, value in item.items() if key != "input"}
            for item in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=error_response("VALIDATION_ERROR", str(details)),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, _exc: Exception) -> JSONResponse:
        logger.exception("未处理异常: %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content=error_response("INTERNAL_ERROR", ERROR_MESSAGES["INTERNAL_ERROR"]),
        )
