"""Throwaway fixture test (6/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.report_lines_one import (
    chunk_report_lines_one,
    normalize_report_lines_one,
    summarize_report_lines_one,
)


def test_normalize_report_lines_one_collapses_whitespace():
    assert normalize_report_lines_one("  a   b  c ") == "a b c"


def test_chunk_report_lines_one_splits_evenly():
    assert chunk_report_lines_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_report_lines_one_handles_empty_input():
    result = summarize_report_lines_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
