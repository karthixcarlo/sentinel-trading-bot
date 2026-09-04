"""Throwaway fixture test (78/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.histogram_bins_three import (
    chunk_histogram_bins_three,
    normalize_histogram_bins_three,
    summarize_histogram_bins_three,
)


def test_normalize_histogram_bins_three_collapses_whitespace():
    assert normalize_histogram_bins_three("  a   b  c ") == "a b c"


def test_chunk_histogram_bins_three_splits_evenly():
    assert chunk_histogram_bins_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_histogram_bins_three_handles_empty_input():
    result = summarize_histogram_bins_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
