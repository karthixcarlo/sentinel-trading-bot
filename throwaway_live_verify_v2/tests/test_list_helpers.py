"""Throwaway fixture test (2/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.list_helpers import (
    chunk_list_helpers,
    normalize_list_helpers,
    summarize_list_helpers,
)


def test_normalize_list_helpers_collapses_whitespace():
    assert normalize_list_helpers("  a   b  c ") == "a b c"


def test_chunk_list_helpers_splits_evenly():
    assert chunk_list_helpers([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_list_helpers_handles_empty_input():
    result = summarize_list_helpers([])
    assert result["count"] == 0
    assert result["average"] == 0.0
