"""Throwaway fixture test (32/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.report_lines_two import (
    chunk_report_lines_two,
    normalize_report_lines_two,
    summarize_report_lines_two,
)


def test_normalize_report_lines_two_collapses_whitespace():
    assert normalize_report_lines_two("  a   b  c ") == "a b c"


def test_chunk_report_lines_two_splits_evenly():
    assert chunk_report_lines_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_report_lines_two_handles_empty_input():
    result = summarize_report_lines_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
