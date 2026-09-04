"""Throwaway fixture test (4/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.number_utils_one import (
    chunk_number_utils_one,
    normalize_number_utils_one,
    summarize_number_utils_one,
)


def test_normalize_number_utils_one_collapses_whitespace():
    assert normalize_number_utils_one("  a   b  c ") == "a b c"


def test_chunk_number_utils_one_splits_evenly():
    assert chunk_number_utils_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_number_utils_one_handles_empty_input():
    result = summarize_number_utils_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
