"""Throwaway fixture test (13/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.worker_loop import (
    chunk_worker_loop,
    normalize_worker_loop,
    summarize_worker_loop,
)


def test_normalize_worker_loop_collapses_whitespace():
    assert normalize_worker_loop("  a   b  c ") == "a b c"


def test_chunk_worker_loop_splits_evenly():
    assert chunk_worker_loop([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_worker_loop_handles_empty_input():
    result = summarize_worker_loop([])
    assert result["count"] == 0
    assert result["average"] == 0.0
