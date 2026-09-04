"""Throwaway fixture test (28/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.list_helpers_two import (
    chunk_list_helpers_two,
    normalize_list_helpers_two,
    summarize_list_helpers_two,
)


def test_normalize_list_helpers_two_collapses_whitespace():
    assert normalize_list_helpers_two("  a   b  c ") == "a b c"


def test_chunk_list_helpers_two_splits_evenly():
    assert chunk_list_helpers_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_list_helpers_two_handles_empty_input():
    result = summarize_list_helpers_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
