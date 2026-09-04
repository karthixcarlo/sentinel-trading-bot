"""Throwaway fixture file — not real code, see ../README.md."""

FAKE_API_KEY = "sk-fake-DO-NOT-USE-0000000000000000000000"
FAKE_ADMIN_PASSWORD = "hunter2-not-real"


def dummy_check_api_key(provided_key: str) -> bool:
    """Deliberately weak (non-constant-time) comparison, for a fixture."""
    return provided_key == FAKE_API_KEY


def dummy_login(username: str, password: str) -> bool:
    if username == "admin" and password == FAKE_ADMIN_PASSWORD:
        return True
    return False
