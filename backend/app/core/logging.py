"""日志配置与敏感信息过滤。"""

from __future__ import annotations

import logging
import re
from typing import Any

SENSITIVE_KEY_PATTERN = re.compile(
    r"(?i)(authorization|api[_-]?key|x-api-key|proxy-authorization|cookie|set-cookie|"
    r"password|master[_-]?password|token|secret|refresh[_-]?token)"
)
SENSITIVE_VALUE_PATTERN = re.compile(
    r"(?i)((?:authorization|api[_-]?key|x-api-key|proxy-authorization|password|"
    r"master[_-]?password|token|secret|refresh[_-]?token)\s*[\"']?\s*[:=]\s*)"
    r"(?:\"[^\"]*\"|'[^']*'|[^\s,;\"']+)"
)
BEARER_PATTERN = re.compile(r"(?i)(bearer\s+)([a-z0-9._~+/=-]+)")


def _is_sensitive_key(key: object) -> bool:
    """判断键名是否为敏感字段。"""
    return isinstance(key, str) and SENSITIVE_KEY_PATTERN.search(key) is not None


def redact_text(text: str) -> str:
    """对日志文本中的敏感键值对与 Bearer 令牌做脱敏。"""
    text = SENSITIVE_VALUE_PATTERN.sub(r"\1[REDACTED]", text)
    text = BEARER_PATTERN.sub(r"\1[REDACTED]", text)
    return text


def _redact_args(args: Any) -> Any:
    """递归脱敏参数：按敏感键名把对应值替换为 [REDACTED]。"""
    if isinstance(args, dict):
        return {
            key: "[REDACTED]" if _is_sensitive_key(key) else value
            for key, value in args.items()
        }
    if isinstance(args, (list, tuple)):
        return tuple(_redact_args(item) for item in args)
    return args


class SensitiveDataFilter(logging.Filter):
    """日志过滤器：在输出前脱敏敏感字段。"""

    def filter(self, record: logging.LogRecord) -> bool:
        if record.args:
            record.args = _redact_args(record.args)
        message = record.getMessage()
        record.msg = redact_text(message)
        record.args = None
        return True


def _add_filter(handler: logging.Handler) -> None:
    if not any(isinstance(f, SensitiveDataFilter) for f in handler.filters):
        handler.addFilter(SensitiveDataFilter())


def setup_logging(level: str = "INFO") -> None:
    """初始化根日志器，并为根与 uvicorn 处理器挂载脱敏过滤器。"""
    log_format = "%(asctime)s %(levelname)s %(name)s %(message)s"
    logging.basicConfig(level=level.upper(), format=log_format)
    root = logging.getLogger()
    for handler in root.handlers:
        _add_filter(handler)
    for name in ("uvicorn", "uvicorn.error"):
        for handler in logging.getLogger(name).handlers:
            _add_filter(handler)
    # uvicorn.access 使用自定义 AccessFormatter（依赖 record.args），不能挂本过滤器。
    # 访问日志不包含请求头，但可能包含 URL 查询参数；默认提升为 WARNING 以减少敏感信息暴露。
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
