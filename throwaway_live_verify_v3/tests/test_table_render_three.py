"""Throwaway fixture test (59/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.table_render_three import (
    chunk_table_render_three,
    normalize_table_render_three,
    summarize_table_render_three,
)


def test_normalize_table_render_three_collapses_whitespace():
    assert normalize_table_render_three("  a   b  c ") == "a b c"


def test_chunk_table_render_three_splits_evenly():
    assert chunk_table_render_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_table_render_three_handles_empty_input():
    result = summarize_table_render_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
