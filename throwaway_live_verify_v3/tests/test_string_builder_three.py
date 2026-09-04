"""Throwaway fixture test (57/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.string_builder_three import (
    chunk_string_builder_three,
    normalize_string_builder_three,
    summarize_string_builder_three,
)


def test_normalize_string_builder_three_collapses_whitespace():
    assert normalize_string_builder_three("  a   b  c ") == "a b c"


def test_chunk_string_builder_three_splits_evenly():
    assert chunk_string_builder_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_string_builder_three_handles_empty_input():
    result = summarize_string_builder_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
