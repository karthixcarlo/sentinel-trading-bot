"""Throwaway fixture test (63/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.cache_lite_three import (
    chunk_cache_lite_three,
    normalize_cache_lite_three,
    summarize_cache_lite_three,
)


def test_normalize_cache_lite_three_collapses_whitespace():
    assert normalize_cache_lite_three("  a   b  c ") == "a b c"


def test_chunk_cache_lite_three_splits_evenly():
    assert chunk_cache_lite_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_cache_lite_three_handles_empty_input():
    result = summarize_cache_lite_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
