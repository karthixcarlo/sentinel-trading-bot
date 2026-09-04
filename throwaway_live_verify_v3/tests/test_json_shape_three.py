"""Throwaway fixture test (61/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.json_shape_three import (
    chunk_json_shape_three,
    normalize_json_shape_three,
    summarize_json_shape_three,
)


def test_normalize_json_shape_three_collapses_whitespace():
    assert normalize_json_shape_three("  a   b  c ") == "a b c"


def test_chunk_json_shape_three_splits_evenly():
    assert chunk_json_shape_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_json_shape_three_handles_empty_input():
    result = summarize_json_shape_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
