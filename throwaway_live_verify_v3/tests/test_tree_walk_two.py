"""Throwaway fixture test (46/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.tree_walk_two import (
    chunk_tree_walk_two,
    normalize_tree_walk_two,
    summarize_tree_walk_two,
)


def test_normalize_tree_walk_two_collapses_whitespace():
    assert normalize_tree_walk_two("  a   b  c ") == "a b c"


def test_chunk_tree_walk_two_splits_evenly():
    assert chunk_tree_walk_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_tree_walk_two_handles_empty_input():
    result = summarize_tree_walk_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
