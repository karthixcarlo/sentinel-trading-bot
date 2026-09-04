"""Throwaway fixture test (26/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.histogram_bins_one import (
    chunk_histogram_bins_one,
    normalize_histogram_bins_one,
    summarize_histogram_bins_one,
)


def test_normalize_histogram_bins_one_collapses_whitespace():
    assert normalize_histogram_bins_one("  a   b  c ") == "a b c"


def test_chunk_histogram_bins_one_splits_evenly():
    assert chunk_histogram_bins_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_histogram_bins_one_handles_empty_input():
    result = summarize_histogram_bins_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
