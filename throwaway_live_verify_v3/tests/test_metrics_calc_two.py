"""Throwaway fixture test (41/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.metrics_calc_two import (
    chunk_metrics_calc_two,
    normalize_metrics_calc_two,
    summarize_metrics_calc_two,
)


def test_normalize_metrics_calc_two_collapses_whitespace():
    assert normalize_metrics_calc_two("  a   b  c ") == "a b c"


def test_chunk_metrics_calc_two_splits_evenly():
    assert chunk_metrics_calc_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_metrics_calc_two_handles_empty_input():
    result = summarize_metrics_calc_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
