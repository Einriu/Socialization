"""API Key 本地加密：AES-256-GCM，密钥文件首次运行自动生成（无主密码）。"""

from __future__ import annotations

import base64
import os
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import get_settings

_NONCE_SIZE = 12


def _key_path() -> Path:
    return Path(get_settings().data_dir) / ".secret.key"


def _load_or_create_key() -> bytes:
    path = _key_path()
    if path.exists():
        raw = path.read_bytes()
        if len(raw) == 32:
            return raw
        raise RuntimeError("本地密钥文件损坏，请删除 data/.secret.key 后重新配置 API Key")
    path.parent.mkdir(parents=True, exist_ok=True)
    key = os.urandom(32)
    path.write_bytes(key)
    return key


def encrypt_text(plaintext: str) -> str:
    """加密文本，返回 base64(nonce + ciphertext)。"""
    key = _load_or_create_key()
    nonce = os.urandom(_NONCE_SIZE)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("ascii")


def decrypt_text(token: str) -> str:
    """解密 encrypt_text 的结果。"""
    key = _load_or_create_key()
    raw = base64.b64decode(token)
    nonce, ciphertext = raw[:_NONCE_SIZE], raw[_NONCE_SIZE:]
    return AESGCM(key).decrypt(nonce, ciphertext, None).decode("utf-8")


def reset_keys() -> None:
    """删除本地密钥文件（等价于重置全部已加密密钥）。"""
    path = _key_path()
    if path.exists():
        path.unlink()
