"""Throwaway fixture test (53/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.text_formatting_three import (
    chunk_text_formatting_three,
    normalize_text_formatting_three,
    summarize_text_formatting_three,
)


def test_normalize_text_formatting_three_collapses_whitespace():
    assert normalize_text_formatting_three("  a   b  c ") == "a b c"


def test_chunk_text_formatting_three_splits_evenly():
    assert chunk_text_formatting_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_text_formatting_three_handles_empty_input():
    result = summarize_text_formatting_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
