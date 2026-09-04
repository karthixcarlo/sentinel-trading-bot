"""Throwaway fixture test (20/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.tree_walk import (
    chunk_tree_walk,
    normalize_tree_walk,
    summarize_tree_walk,
)


def test_normalize_tree_walk_collapses_whitespace():
    assert normalize_tree_walk("  a   b  c ") == "a b c"


def test_chunk_tree_walk_splits_evenly():
    assert chunk_tree_walk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_tree_walk_handles_empty_input():
    result = summarize_tree_walk([])
    assert result["count"] == 0
    assert result["average"] == 0.0
