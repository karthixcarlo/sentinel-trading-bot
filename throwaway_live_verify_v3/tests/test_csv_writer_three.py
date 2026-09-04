"""Throwaway fixture test (60/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.csv_writer_three import (
    chunk_csv_writer_three,
    normalize_csv_writer_three,
    summarize_csv_writer_three,
)


def test_normalize_csv_writer_three_collapses_whitespace():
    assert normalize_csv_writer_three("  a   b  c ") == "a b c"


def test_chunk_csv_writer_three_splits_evenly():
    assert chunk_csv_writer_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_csv_writer_three_handles_empty_input():
    result = summarize_csv_writer_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
