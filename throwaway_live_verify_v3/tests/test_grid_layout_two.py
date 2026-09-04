"""Throwaway fixture test (48/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.grid_layout_two import (
    chunk_grid_layout_two,
    normalize_grid_layout_two,
    summarize_grid_layout_two,
)


def test_normalize_grid_layout_two_collapses_whitespace():
    assert normalize_grid_layout_two("  a   b  c ") == "a b c"


def test_chunk_grid_layout_two_splits_evenly():
    assert chunk_grid_layout_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_grid_layout_two_handles_empty_input():
    result = summarize_grid_layout_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
