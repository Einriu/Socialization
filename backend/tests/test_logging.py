"""敏感信息日志脱敏测试。"""

from __future__ import annotations

import logging

from app.core.logging import SensitiveDataFilter, redact_text


def test_redact_text_masks_authorization_and_api_key() -> None:
    text = '{"Authorization": "Bearer sk-secret-123", "x-api-key": "abc123"}'
    redacted = redact_text(text)
    assert "sk-secret-123" not in redacted
    assert "abc123" not in redacted
    assert redacted.count("[REDACTED]") == 2


def test_redact_text_masks_key_value_pattern() -> None:
    redacted = redact_text("provider api_key=sk-very-secret timeout=30")
    assert "sk-very-secret" not in redacted
    assert "[REDACTED]" in redacted
    assert "timeout=30" in redacted


def test_sensitive_filter_redacts_positional_args() -> None:
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="调用 provider: api_key=%s",
        args=("sk-very-secret",),
        exc_info=None,
    )
    assert SensitiveDataFilter().filter(record)
    formatted = record.getMessage()
    assert "sk-very-secret" not in formatted
    assert "[REDACTED]" in formatted


def test_sensitive_filter_redacts_dict_args_by_key() -> None:
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="headers: %s",
        args=({"Authorization": "Bearer tok-abc", "User-Agent": "pytest"},),
        exc_info=None,
    )
    assert SensitiveDataFilter().filter(record)
    formatted = record.getMessage()
    assert "tok-abc" not in formatted
    assert "[REDACTED]" in formatted
    assert "pytest" in formatted
