"""Throwaway fixture test (7/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.table_render import (
    chunk_table_render,
    normalize_table_render,
    summarize_table_render,
)


def test_normalize_table_render_collapses_whitespace():
    assert normalize_table_render("  a   b  c ") == "a b c"


def test_chunk_table_render_splits_evenly():
    assert chunk_table_render([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_table_render_handles_empty_input():
    result = summarize_table_render([])
    assert result["count"] == 0
    assert result["average"] == 0.0
