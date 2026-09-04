"""Throwaway fixture test (69/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.geometry_calc_three import (
    chunk_geometry_calc_three,
    normalize_geometry_calc_three,
    summarize_geometry_calc_three,
)


def test_normalize_geometry_calc_three_collapses_whitespace():
    assert normalize_geometry_calc_three("  a   b  c ") == "a b c"


def test_chunk_geometry_calc_three_splits_evenly():
    assert chunk_geometry_calc_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_geometry_calc_three_handles_empty_input():
    result = summarize_geometry_calc_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
