"""Throwaway fixture test (11/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.cache_lite_one import (
    chunk_cache_lite_one,
    normalize_cache_lite_one,
    summarize_cache_lite_one,
)


def test_normalize_cache_lite_one_collapses_whitespace():
    assert normalize_cache_lite_one("  a   b  c ") == "a b c"


def test_chunk_cache_lite_one_splits_evenly():
    assert chunk_cache_lite_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_cache_lite_one_handles_empty_input():
    result = summarize_cache_lite_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
