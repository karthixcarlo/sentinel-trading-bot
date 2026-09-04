"""Throwaway fixture file — not real code, see ../README.md."""

import os


def dummy_read_upload(base_dir: str, filename: str) -> bytes:
    """No `..`/absolute-path check on `filename` — path traversal shape,
    intentional in this disposable fixture."""
    path = os.path.join(base_dir, filename)
    with open(path, "rb") as f:
        return f.read()
