"""Throwaway fixture test (10/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.retry_helper_one import (
    chunk_retry_helper_one,
    normalize_retry_helper_one,
    summarize_retry_helper_one,
)


def test_normalize_retry_helper_one_collapses_whitespace():
    assert normalize_retry_helper_one("  a   b  c ") == "a b c"


def test_chunk_retry_helper_one_splits_evenly():
    assert chunk_retry_helper_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_retry_helper_one_handles_empty_input():
    result = summarize_retry_helper_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
