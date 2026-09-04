"""Throwaway fixture test (15/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.metrics_calc_one import (
    chunk_metrics_calc_one,
    normalize_metrics_calc_one,
    summarize_metrics_calc_one,
)


def test_normalize_metrics_calc_one_collapses_whitespace():
    assert normalize_metrics_calc_one("  a   b  c ") == "a b c"


def test_chunk_metrics_calc_one_splits_evenly():
    assert chunk_metrics_calc_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_metrics_calc_one_handles_empty_input():
    result = summarize_metrics_calc_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
