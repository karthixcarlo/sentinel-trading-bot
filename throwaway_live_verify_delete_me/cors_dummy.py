"""Throwaway fixture file — not real code, see ../README.md."""


def dummy_cors_headers() -> dict:
    """Wildcard origin with credentials-friendly headers — overly
    permissive CORS shape, intentional in this disposable fixture."""
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
    }
