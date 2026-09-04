"""Throwaway fixture test (15/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.metrics_calc import (
    chunk_metrics_calc,
    normalize_metrics_calc,
    summarize_metrics_calc,
)


def test_normalize_metrics_calc_collapses_whitespace():
    assert normalize_metrics_calc("  a   b  c ") == "a b c"


def test_chunk_metrics_calc_splits_evenly():
    assert chunk_metrics_calc([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_metrics_calc_handles_empty_input():
    result = summarize_metrics_calc([])
    assert result["count"] == 0
    assert result["average"] == 0.0
