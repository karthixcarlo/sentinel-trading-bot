"""Throwaway fixture test (55/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.date_math_three import (
    chunk_date_math_three,
    normalize_date_math_three,
    summarize_date_math_three,
)


def test_normalize_date_math_three_collapses_whitespace():
    assert normalize_date_math_three("  a   b  c ") == "a b c"


def test_chunk_date_math_three_splits_evenly():
    assert chunk_date_math_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_date_math_three_handles_empty_input():
    result = summarize_date_math_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
