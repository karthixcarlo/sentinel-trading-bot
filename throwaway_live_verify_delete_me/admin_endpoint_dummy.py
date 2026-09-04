"""Throwaway fixture file — not real code, see ../README.md."""


def dummy_admin_delete_all_users(request) -> str:
    """No auth/role check before a destructive admin action — missing
    authorization shape, intentional in this disposable fixture."""
    user_ids = request.get("user_ids", [])
    return f"deleted {len(user_ids)} users"


def dummy_admin_dashboard_data(request) -> dict:
    # Also missing an auth check, same intentional pattern.
    return {"revenue": 1_000_000, "active_users": 42}
