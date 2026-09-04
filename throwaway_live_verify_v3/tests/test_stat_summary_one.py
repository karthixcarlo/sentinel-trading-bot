"""Throwaway fixture test (25/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.stat_summary_one import (
    chunk_stat_summary_one,
    normalize_stat_summary_one,
    summarize_stat_summary_one,
)


def test_normalize_stat_summary_one_collapses_whitespace():
    assert normalize_stat_summary_one("  a   b  c ") == "a b c"


def test_chunk_stat_summary_one_splits_evenly():
    assert chunk_stat_summary_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_stat_summary_one_handles_empty_input():
    result = summarize_stat_summary_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
