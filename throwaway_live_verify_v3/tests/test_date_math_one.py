"""Throwaway fixture test (3/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.date_math_one import (
    chunk_date_math_one,
    normalize_date_math_one,
    summarize_date_math_one,
)


def test_normalize_date_math_one_collapses_whitespace():
    assert normalize_date_math_one("  a   b  c ") == "a b c"


def test_chunk_date_math_one_splits_evenly():
    assert chunk_date_math_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_date_math_one_handles_empty_input():
    result = summarize_date_math_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
