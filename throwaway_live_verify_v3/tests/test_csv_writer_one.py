"""Throwaway fixture test (8/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.csv_writer_one import (
    chunk_csv_writer_one,
    normalize_csv_writer_one,
    summarize_csv_writer_one,
)


def test_normalize_csv_writer_one_collapses_whitespace():
    assert normalize_csv_writer_one("  a   b  c ") == "a b c"


def test_chunk_csv_writer_one_splits_evenly():
    assert chunk_csv_writer_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_csv_writer_one_handles_empty_input():
    result = summarize_csv_writer_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
