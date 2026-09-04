"""Throwaway fixture test (18/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.unit_convert import (
    chunk_unit_convert,
    normalize_unit_convert,
    summarize_unit_convert,
)


def test_normalize_unit_convert_collapses_whitespace():
    assert normalize_unit_convert("  a   b  c ") == "a b c"


def test_chunk_unit_convert_splits_evenly():
    assert chunk_unit_convert([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_unit_convert_handles_empty_input():
    result = summarize_unit_convert([])
    assert result["count"] == 0
    assert result["average"] == 0.0
