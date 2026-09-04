"""Throwaway fixture test (22/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.grid_layout_one import (
    chunk_grid_layout_one,
    normalize_grid_layout_one,
    summarize_grid_layout_one,
)


def test_normalize_grid_layout_one_collapses_whitespace():
    assert normalize_grid_layout_one("  a   b  c ") == "a b c"


def test_chunk_grid_layout_one_splits_evenly():
    assert chunk_grid_layout_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_grid_layout_one_handles_empty_input():
    result = summarize_grid_layout_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
