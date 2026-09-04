"""Throwaway fixture file — not real code, see ../README.md."""

import pickle


def dummy_load_cached_session(raw_bytes: bytes):
    """`pickle.loads` on untrusted bytes — unsafe deserialization shape,
    intentional in this disposable fixture."""
    return pickle.loads(raw_bytes)  # noqa: S301 - deliberate fixture pattern


def dummy_save_cached_session(obj) -> bytes:
    return pickle.dumps(obj)
