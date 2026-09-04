"""Throwaway fixture test (7/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.table_render_one import (
    chunk_table_render_one,
    normalize_table_render_one,
    summarize_table_render_one,
)


def test_normalize_table_render_one_collapses_whitespace():
    assert normalize_table_render_one("  a   b  c ") == "a b c"


def test_chunk_table_render_one_splits_evenly():
    assert chunk_table_render_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_table_render_one_handles_empty_input():
    result = summarize_table_render_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
