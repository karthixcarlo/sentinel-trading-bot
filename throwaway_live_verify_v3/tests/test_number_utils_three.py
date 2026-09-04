"""Throwaway fixture test (56/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.number_utils_three import (
    chunk_number_utils_three,
    normalize_number_utils_three,
    summarize_number_utils_three,
)


def test_normalize_number_utils_three_collapses_whitespace():
    assert normalize_number_utils_three("  a   b  c ") == "a b c"


def test_chunk_number_utils_three_splits_evenly():
    assert chunk_number_utils_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_number_utils_three_handles_empty_input():
    result = summarize_number_utils_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
