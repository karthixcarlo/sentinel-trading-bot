"""Throwaway fixture test (17/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.geometry_calc import (
    chunk_geometry_calc,
    normalize_geometry_calc,
    summarize_geometry_calc,
)


def test_normalize_geometry_calc_collapses_whitespace():
    assert normalize_geometry_calc("  a   b  c ") == "a b c"


def test_chunk_geometry_calc_splits_evenly():
    assert chunk_geometry_calc([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_geometry_calc_handles_empty_input():
    result = summarize_geometry_calc([])
    assert result["count"] == 0
    assert result["average"] == 0.0
