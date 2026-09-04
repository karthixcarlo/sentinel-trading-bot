"""Throwaway fixture test (36/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.retry_helper_two import (
    chunk_retry_helper_two,
    normalize_retry_helper_two,
    summarize_retry_helper_two,
)


def test_normalize_retry_helper_two_collapses_whitespace():
    assert normalize_retry_helper_two("  a   b  c ") == "a b c"


def test_chunk_retry_helper_two_splits_evenly():
    assert chunk_retry_helper_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_retry_helper_two_handles_empty_input():
    result = summarize_retry_helper_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
