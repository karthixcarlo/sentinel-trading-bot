"""Throwaway fixture test (54/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.list_helpers_three import (
    chunk_list_helpers_three,
    normalize_list_helpers_three,
    summarize_list_helpers_three,
)


def test_normalize_list_helpers_three_collapses_whitespace():
    assert normalize_list_helpers_three("  a   b  c ") == "a b c"


def test_chunk_list_helpers_three_splits_evenly():
    assert chunk_list_helpers_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_list_helpers_three_handles_empty_input():
    result = summarize_list_helpers_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
