"""Throwaway fixture test (13/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.worker_loop_one import (
    chunk_worker_loop_one,
    normalize_worker_loop_one,
    summarize_worker_loop_one,
)


def test_normalize_worker_loop_one_collapses_whitespace():
    assert normalize_worker_loop_one("  a   b  c ") == "a b c"


def test_chunk_worker_loop_one_splits_evenly():
    assert chunk_worker_loop_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_worker_loop_one_handles_empty_input():
    result = summarize_worker_loop_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
