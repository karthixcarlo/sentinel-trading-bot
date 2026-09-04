"""Throwaway fixture test (33/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.table_render_two import (
    chunk_table_render_two,
    normalize_table_render_two,
    summarize_table_render_two,
)


def test_normalize_table_render_two_collapses_whitespace():
    assert normalize_table_render_two("  a   b  c ") == "a b c"


def test_chunk_table_render_two_splits_evenly():
    assert chunk_table_render_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_table_render_two_handles_empty_input():
    result = summarize_table_render_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
