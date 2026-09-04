"""Throwaway fixture test (34/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.csv_writer_two import (
    chunk_csv_writer_two,
    normalize_csv_writer_two,
    summarize_csv_writer_two,
)


def test_normalize_csv_writer_two_collapses_whitespace():
    assert normalize_csv_writer_two("  a   b  c ") == "a b c"


def test_chunk_csv_writer_two_splits_evenly():
    assert chunk_csv_writer_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_csv_writer_two_handles_empty_input():
    result = summarize_csv_writer_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
