"""Throwaway fixture test (18/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.unit_convert_one import (
    chunk_unit_convert_one,
    normalize_unit_convert_one,
    summarize_unit_convert_one,
)


def test_normalize_unit_convert_one_collapses_whitespace():
    assert normalize_unit_convert_one("  a   b  c ") == "a b c"


def test_chunk_unit_convert_one_splits_evenly():
    assert chunk_unit_convert_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_unit_convert_one_handles_empty_input():
    result = summarize_unit_convert_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
