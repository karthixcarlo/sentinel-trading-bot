"""Throwaway fixture test (50/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.matrix_ops_two import (
    chunk_matrix_ops_two,
    normalize_matrix_ops_two,
    summarize_matrix_ops_two,
)


def test_normalize_matrix_ops_two_collapses_whitespace():
    assert normalize_matrix_ops_two("  a   b  c ") == "a b c"


def test_chunk_matrix_ops_two_splits_evenly():
    assert chunk_matrix_ops_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_matrix_ops_two_handles_empty_input():
    result = summarize_matrix_ops_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
