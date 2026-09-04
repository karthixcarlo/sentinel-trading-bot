"""Throwaway fixture test (35/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.json_shape_two import (
    chunk_json_shape_two,
    normalize_json_shape_two,
    summarize_json_shape_two,
)


def test_normalize_json_shape_two_collapses_whitespace():
    assert normalize_json_shape_two("  a   b  c ") == "a b c"


def test_chunk_json_shape_two_splits_evenly():
    assert chunk_json_shape_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_json_shape_two_handles_empty_input():
    result = summarize_json_shape_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
