"""Throwaway fixture test (1/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.text_formatting import (
    chunk_text_formatting,
    normalize_text_formatting,
    summarize_text_formatting,
)


def test_normalize_text_formatting_collapses_whitespace():
    assert normalize_text_formatting("  a   b  c ") == "a b c"


def test_chunk_text_formatting_splits_evenly():
    assert chunk_text_formatting([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_text_formatting_handles_empty_input():
    result = summarize_text_formatting([])
    assert result["count"] == 0
    assert result["average"] == 0.0
