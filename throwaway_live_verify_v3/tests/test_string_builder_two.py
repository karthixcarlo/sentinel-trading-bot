"""Throwaway fixture test (31/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.string_builder_two import (
    chunk_string_builder_two,
    normalize_string_builder_two,
    summarize_string_builder_two,
)


def test_normalize_string_builder_two_collapses_whitespace():
    assert normalize_string_builder_two("  a   b  c ") == "a b c"


def test_chunk_string_builder_two_splits_evenly():
    assert chunk_string_builder_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_string_builder_two_handles_empty_input():
    result = summarize_string_builder_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
