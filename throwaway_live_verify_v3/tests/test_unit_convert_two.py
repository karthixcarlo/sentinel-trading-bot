"""Throwaway fixture test (44/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.unit_convert_two import (
    chunk_unit_convert_two,
    normalize_unit_convert_two,
    summarize_unit_convert_two,
)


def test_normalize_unit_convert_two_collapses_whitespace():
    assert normalize_unit_convert_two("  a   b  c ") == "a b c"


def test_chunk_unit_convert_two_splits_evenly():
    assert chunk_unit_convert_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_unit_convert_two_handles_empty_input():
    result = summarize_unit_convert_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
