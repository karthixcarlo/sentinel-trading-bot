"""Throwaway fixture test (6/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.report_lines import (
    chunk_report_lines,
    normalize_report_lines,
    summarize_report_lines,
)


def test_normalize_report_lines_collapses_whitespace():
    assert normalize_report_lines("  a   b  c ") == "a b c"


def test_chunk_report_lines_splits_evenly():
    assert chunk_report_lines([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_report_lines_handles_empty_input():
    result = summarize_report_lines([])
    assert result["count"] == 0
    assert result["average"] == 0.0
