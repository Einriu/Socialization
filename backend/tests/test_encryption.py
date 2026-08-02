"""API Key 本地加密测试。"""

from __future__ import annotations

from pathlib import Path

import pytest
from cryptography.exceptions import InvalidTag

from app.core.config import get_settings
from app.core.encryption import decrypt_text, encrypt_text, reset_keys


def test_encrypt_decrypt_roundtrip() -> None:
    token = encrypt_text("sk-test-secret-1234")
    assert token != "sk-test-secret-1234"
    assert decrypt_text(token) == "sk-test-secret-1234"


def test_key_file_created_in_data_dir() -> None:
    key_path = Path(get_settings().data_dir) / ".secret.key"
    assert key_path.exists()
    assert len(key_path.read_bytes()) == 32


def test_reset_keys_requires_new_encryption() -> None:
    token = encrypt_text("old-key")
    reset_keys()
    with pytest.raises(InvalidTag):
        decrypt_text(token)
    assert decrypt_text(encrypt_text("new-key")) == "new-key"
