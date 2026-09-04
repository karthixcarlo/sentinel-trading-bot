"""Throwaway fixture test (23/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.vector_math_one import (
    chunk_vector_math_one,
    normalize_vector_math_one,
    summarize_vector_math_one,
)


def test_normalize_vector_math_one_collapses_whitespace():
    assert normalize_vector_math_one("  a   b  c ") == "a b c"


def test_chunk_vector_math_one_splits_evenly():
    assert chunk_vector_math_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_vector_math_one_handles_empty_input():
    result = summarize_vector_math_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
