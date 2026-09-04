"""Throwaway fixture test (11/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.cache_lite import (
    chunk_cache_lite,
    normalize_cache_lite,
    summarize_cache_lite,
)


def test_normalize_cache_lite_collapses_whitespace():
    assert normalize_cache_lite("  a   b  c ") == "a b c"


def test_chunk_cache_lite_splits_evenly():
    assert chunk_cache_lite([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_cache_lite_handles_empty_input():
    result = summarize_cache_lite([])
    assert result["count"] == 0
    assert result["average"] == 0.0
