"""Throwaway fixture test (9/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.json_shape import (
    chunk_json_shape,
    normalize_json_shape,
    summarize_json_shape,
)


def test_normalize_json_shape_collapses_whitespace():
    assert normalize_json_shape("  a   b  c ") == "a b c"


def test_chunk_json_shape_splits_evenly():
    assert chunk_json_shape([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_json_shape_handles_empty_input():
    result = summarize_json_shape([])
    assert result["count"] == 0
    assert result["average"] == 0.0
