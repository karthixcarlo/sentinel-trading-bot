"""Throwaway fixture test (65/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.worker_loop_three import (
    chunk_worker_loop_three,
    normalize_worker_loop_three,
    summarize_worker_loop_three,
)


def test_normalize_worker_loop_three_collapses_whitespace():
    assert normalize_worker_loop_three("  a   b  c ") == "a b c"


def test_chunk_worker_loop_three_splits_evenly():
    assert chunk_worker_loop_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_worker_loop_three_handles_empty_input():
    result = summarize_worker_loop_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
