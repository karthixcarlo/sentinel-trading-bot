"""Throwaway fixture test (9/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.json_shape_one import (
    chunk_json_shape_one,
    normalize_json_shape_one,
    summarize_json_shape_one,
)


def test_normalize_json_shape_one_collapses_whitespace():
    assert normalize_json_shape_one("  a   b  c ") == "a b c"


def test_chunk_json_shape_one_splits_evenly():
    assert chunk_json_shape_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_json_shape_one_handles_empty_input():
    result = summarize_json_shape_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
