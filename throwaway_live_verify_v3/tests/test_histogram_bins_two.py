"""Throwaway fixture test (52/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.histogram_bins_two import (
    chunk_histogram_bins_two,
    normalize_histogram_bins_two,
    summarize_histogram_bins_two,
)


def test_normalize_histogram_bins_two_collapses_whitespace():
    assert normalize_histogram_bins_two("  a   b  c ") == "a b c"


def test_chunk_histogram_bins_two_splits_evenly():
    assert chunk_histogram_bins_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_histogram_bins_two_handles_empty_input():
    result = summarize_histogram_bins_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
