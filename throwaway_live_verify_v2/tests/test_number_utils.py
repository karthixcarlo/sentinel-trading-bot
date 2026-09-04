"""Throwaway fixture test (4/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.number_utils import (
    chunk_number_utils,
    normalize_number_utils,
    summarize_number_utils,
)


def test_normalize_number_utils_collapses_whitespace():
    assert normalize_number_utils("  a   b  c ") == "a b c"


def test_chunk_number_utils_splits_evenly():
    assert chunk_number_utils([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_number_utils_handles_empty_input():
    result = summarize_number_utils([])
    assert result["count"] == 0
    assert result["average"] == 0.0
