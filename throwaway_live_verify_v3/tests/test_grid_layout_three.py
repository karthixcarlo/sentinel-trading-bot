"""Throwaway fixture test (74/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.grid_layout_three import (
    chunk_grid_layout_three,
    normalize_grid_layout_three,
    summarize_grid_layout_three,
)


def test_normalize_grid_layout_three_collapses_whitespace():
    assert normalize_grid_layout_three("  a   b  c ") == "a b c"


def test_chunk_grid_layout_three_splits_evenly():
    assert chunk_grid_layout_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_grid_layout_three_handles_empty_input():
    result = summarize_grid_layout_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
