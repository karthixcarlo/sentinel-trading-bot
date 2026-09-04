"""Throwaway fixture test (43/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.geometry_calc_two import (
    chunk_geometry_calc_two,
    normalize_geometry_calc_two,
    summarize_geometry_calc_two,
)


def test_normalize_geometry_calc_two_collapses_whitespace():
    assert normalize_geometry_calc_two("  a   b  c ") == "a b c"


def test_chunk_geometry_calc_two_splits_evenly():
    assert chunk_geometry_calc_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_geometry_calc_two_handles_empty_input():
    result = summarize_geometry_calc_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
