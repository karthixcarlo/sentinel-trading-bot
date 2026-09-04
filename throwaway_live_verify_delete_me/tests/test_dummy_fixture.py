"""Throwaway fixture test — not a real test, see ../README.md."""

from throwaway_live_verify_delete_me.auth_dummy import dummy_check_api_key
from throwaway_live_verify_delete_me.crypto_dummy import dummy_hash_password


def test_dummy_check_api_key_rejects_wrong_key():
    assert dummy_check_api_key("not-the-real-key") is False


def test_dummy_hash_password_is_deterministic():
    assert dummy_hash_password("x") == dummy_hash_password("x")
