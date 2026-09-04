"""Throwaway fixture test (1/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.text_formatting_one import (
    chunk_text_formatting_one,
    normalize_text_formatting_one,
    summarize_text_formatting_one,
)


def test_normalize_text_formatting_one_collapses_whitespace():
    assert normalize_text_formatting_one("  a   b  c ") == "a b c"


def test_chunk_text_formatting_one_splits_evenly():
    assert chunk_text_formatting_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_text_formatting_one_handles_empty_input():
    result = summarize_text_formatting_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
