"""Throwaway fixture test (37/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.cache_lite_two import (
    chunk_cache_lite_two,
    normalize_cache_lite_two,
    summarize_cache_lite_two,
)


def test_normalize_cache_lite_two_collapses_whitespace():
    assert normalize_cache_lite_two("  a   b  c ") == "a b c"


def test_chunk_cache_lite_two_splits_evenly():
    assert chunk_cache_lite_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_cache_lite_two_handles_empty_input():
    result = summarize_cache_lite_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
