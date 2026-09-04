"""Throwaway fixture test (72/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.tree_walk_three import (
    chunk_tree_walk_three,
    normalize_tree_walk_three,
    summarize_tree_walk_three,
)


def test_normalize_tree_walk_three_collapses_whitespace():
    assert normalize_tree_walk_three("  a   b  c ") == "a b c"


def test_chunk_tree_walk_three_splits_evenly():
    assert chunk_tree_walk_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_tree_walk_three_handles_empty_input():
    result = summarize_tree_walk_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
