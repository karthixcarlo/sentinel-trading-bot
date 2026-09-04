"""Throwaway fixture test (58/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.report_lines_three import (
    chunk_report_lines_three,
    normalize_report_lines_three,
    summarize_report_lines_three,
)


def test_normalize_report_lines_three_collapses_whitespace():
    assert normalize_report_lines_three("  a   b  c ") == "a b c"


def test_chunk_report_lines_three_splits_evenly():
    assert chunk_report_lines_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_report_lines_three_handles_empty_input():
    result = summarize_report_lines_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
