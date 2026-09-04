"""Throwaway fixture test (30/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.number_utils_two import (
    chunk_number_utils_two,
    normalize_number_utils_two,
    summarize_number_utils_two,
)


def test_normalize_number_utils_two_collapses_whitespace():
    assert normalize_number_utils_two("  a   b  c ") == "a b c"


def test_chunk_number_utils_two_splits_evenly():
    assert chunk_number_utils_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_number_utils_two_handles_empty_input():
    result = summarize_number_utils_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
