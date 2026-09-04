"""Throwaway fixture test (3/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.date_math import (
    chunk_date_math,
    normalize_date_math,
    summarize_date_math,
)


def test_normalize_date_math_collapses_whitespace():
    assert normalize_date_math("  a   b  c ") == "a b c"


def test_chunk_date_math_splits_evenly():
    assert chunk_date_math([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_date_math_handles_empty_input():
    result = summarize_date_math([])
    assert result["count"] == 0
    assert result["average"] == 0.0
