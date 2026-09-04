"""Throwaway fixture test (2/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.list_helpers_one import (
    chunk_list_helpers_one,
    normalize_list_helpers_one,
    summarize_list_helpers_one,
)


def test_normalize_list_helpers_one_collapses_whitespace():
    assert normalize_list_helpers_one("  a   b  c ") == "a b c"


def test_chunk_list_helpers_one_splits_evenly():
    assert chunk_list_helpers_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_list_helpers_one_handles_empty_input():
    result = summarize_list_helpers_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
