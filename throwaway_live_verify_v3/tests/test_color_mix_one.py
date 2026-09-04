"""Throwaway fixture test (16/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.color_mix_one import (
    chunk_color_mix_one,
    normalize_color_mix_one,
    summarize_color_mix_one,
)


def test_normalize_color_mix_one_collapses_whitespace():
    assert normalize_color_mix_one("  a   b  c ") == "a b c"


def test_chunk_color_mix_one_splits_evenly():
    assert chunk_color_mix_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_color_mix_one_handles_empty_input():
    result = summarize_color_mix_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
