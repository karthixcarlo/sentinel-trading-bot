"""Throwaway fixture test (5/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.string_builder import (
    chunk_string_builder,
    normalize_string_builder,
    summarize_string_builder,
)


def test_normalize_string_builder_collapses_whitespace():
    assert normalize_string_builder("  a   b  c ") == "a b c"


def test_chunk_string_builder_splits_evenly():
    assert chunk_string_builder([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_string_builder_handles_empty_input():
    result = summarize_string_builder([])
    assert result["count"] == 0
    assert result["average"] == 0.0
