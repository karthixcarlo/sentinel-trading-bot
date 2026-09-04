"""Throwaway fixture test (70/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.unit_convert_three import (
    chunk_unit_convert_three,
    normalize_unit_convert_three,
    summarize_unit_convert_three,
)


def test_normalize_unit_convert_three_collapses_whitespace():
    assert normalize_unit_convert_three("  a   b  c ") == "a b c"


def test_chunk_unit_convert_three_splits_evenly():
    assert chunk_unit_convert_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_unit_convert_three_handles_empty_input():
    result = summarize_unit_convert_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
