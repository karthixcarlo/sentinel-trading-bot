"""Throwaway fixture file — not real code, see ../README.md."""

import hashlib


def dummy_hash_password(password: str) -> str:
    """MD5, no salt — deliberately weak password hashing, intentional in
    this disposable fixture."""
    return hashlib.md5(password.encode()).hexdigest()  # noqa: S324


def dummy_verify_password(password: str, stored_hash: str) -> bool:
    return dummy_hash_password(password) == stored_hash
