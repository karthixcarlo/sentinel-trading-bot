"""Throwaway fixture test (8/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.csv_writer import (
    chunk_csv_writer,
    normalize_csv_writer,
    summarize_csv_writer,
)


def test_normalize_csv_writer_collapses_whitespace():
    assert normalize_csv_writer("  a   b  c ") == "a b c"


def test_chunk_csv_writer_splits_evenly():
    assert chunk_csv_writer([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_csv_writer_handles_empty_input():
    result = summarize_csv_writer([])
    assert result["count"] == 0
    assert result["average"] == 0.0
