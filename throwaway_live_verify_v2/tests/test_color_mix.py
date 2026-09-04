"""Throwaway fixture test (16/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.color_mix import (
    chunk_color_mix,
    normalize_color_mix,
    summarize_color_mix,
)


def test_normalize_color_mix_collapses_whitespace():
    assert normalize_color_mix("  a   b  c ") == "a b c"


def test_chunk_color_mix_splits_evenly():
    assert chunk_color_mix([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_color_mix_handles_empty_input():
    result = summarize_color_mix([])
    assert result["count"] == 0
    assert result["average"] == 0.0
