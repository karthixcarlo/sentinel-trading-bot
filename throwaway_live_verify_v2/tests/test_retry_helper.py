"""Throwaway fixture test (10/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.retry_helper import (
    chunk_retry_helper,
    normalize_retry_helper,
    summarize_retry_helper,
)


def test_normalize_retry_helper_collapses_whitespace():
    assert normalize_retry_helper("  a   b  c ") == "a b c"


def test_chunk_retry_helper_splits_evenly():
    assert chunk_retry_helper([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_retry_helper_handles_empty_input():
    result = summarize_retry_helper([])
    assert result["count"] == 0
    assert result["average"] == 0.0
