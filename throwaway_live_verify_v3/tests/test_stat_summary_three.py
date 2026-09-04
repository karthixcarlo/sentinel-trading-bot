"""Throwaway fixture test (77/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.stat_summary_three import (
    chunk_stat_summary_three,
    normalize_stat_summary_three,
    summarize_stat_summary_three,
)


def test_normalize_stat_summary_three_collapses_whitespace():
    assert normalize_stat_summary_three("  a   b  c ") == "a b c"


def test_chunk_stat_summary_three_splits_evenly():
    assert chunk_stat_summary_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_stat_summary_three_handles_empty_input():
    result = summarize_stat_summary_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
