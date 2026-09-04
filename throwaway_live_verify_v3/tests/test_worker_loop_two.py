"""Throwaway fixture test (39/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.worker_loop_two import (
    chunk_worker_loop_two,
    normalize_worker_loop_two,
    summarize_worker_loop_two,
)


def test_normalize_worker_loop_two_collapses_whitespace():
    assert normalize_worker_loop_two("  a   b  c ") == "a b c"


def test_chunk_worker_loop_two_splits_evenly():
    assert chunk_worker_loop_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_worker_loop_two_handles_empty_input():
    result = summarize_worker_loop_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
