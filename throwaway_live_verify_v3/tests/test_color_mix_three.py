"""Throwaway fixture test (68/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.color_mix_three import (
    chunk_color_mix_three,
    normalize_color_mix_three,
    summarize_color_mix_three,
)


def test_normalize_color_mix_three_collapses_whitespace():
    assert normalize_color_mix_three("  a   b  c ") == "a b c"


def test_chunk_color_mix_three_splits_evenly():
    assert chunk_color_mix_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_color_mix_three_handles_empty_input():
    result = summarize_color_mix_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
