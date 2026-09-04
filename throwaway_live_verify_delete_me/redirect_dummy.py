"""Throwaway fixture file — not real code, see ../README.md."""


def dummy_build_redirect_response(next_url: str) -> dict:
    """No allowlist check on `next_url` — open-redirect shape, intentional
    in this disposable fixture."""
    return {"status": 302, "headers": {"Location": next_url}}
