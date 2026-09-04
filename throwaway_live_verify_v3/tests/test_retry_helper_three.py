"""Throwaway fixture test (62/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.retry_helper_three import (
    chunk_retry_helper_three,
    normalize_retry_helper_three,
    summarize_retry_helper_three,
)


def test_normalize_retry_helper_three_collapses_whitespace():
    assert normalize_retry_helper_three("  a   b  c ") == "a b c"


def test_chunk_retry_helper_three_splits_evenly():
    assert chunk_retry_helper_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_retry_helper_three_handles_empty_input():
    result = summarize_retry_helper_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
