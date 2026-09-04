"""Throwaway fixture test (76/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.matrix_ops_three import (
    chunk_matrix_ops_three,
    normalize_matrix_ops_three,
    summarize_matrix_ops_three,
)


def test_normalize_matrix_ops_three_collapses_whitespace():
    assert normalize_matrix_ops_three("  a   b  c ") == "a b c"


def test_chunk_matrix_ops_three_splits_evenly():
    assert chunk_matrix_ops_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_matrix_ops_three_handles_empty_input():
    result = summarize_matrix_ops_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
