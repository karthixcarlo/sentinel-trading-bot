"""Throwaway fixture test (42/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.color_mix_two import (
    chunk_color_mix_two,
    normalize_color_mix_two,
    summarize_color_mix_two,
)


def test_normalize_color_mix_two_collapses_whitespace():
    assert normalize_color_mix_two("  a   b  c ") == "a b c"


def test_chunk_color_mix_two_splits_evenly():
    assert chunk_color_mix_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_color_mix_two_handles_empty_input():
    result = summarize_color_mix_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
