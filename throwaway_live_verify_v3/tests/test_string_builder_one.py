"""Throwaway fixture test (5/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.string_builder_one import (
    chunk_string_builder_one,
    normalize_string_builder_one,
    summarize_string_builder_one,
)


def test_normalize_string_builder_one_collapses_whitespace():
    assert normalize_string_builder_one("  a   b  c ") == "a b c"


def test_chunk_string_builder_one_splits_evenly():
    assert chunk_string_builder_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_string_builder_one_handles_empty_input():
    result = summarize_string_builder_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
