"""Throwaway fixture test (27/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.text_formatting_two import (
    chunk_text_formatting_two,
    normalize_text_formatting_two,
    summarize_text_formatting_two,
)


def test_normalize_text_formatting_two_collapses_whitespace():
    assert normalize_text_formatting_two("  a   b  c ") == "a b c"


def test_chunk_text_formatting_two_splits_evenly():
    assert chunk_text_formatting_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_text_formatting_two_handles_empty_input():
    result = summarize_text_formatting_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
