"""Throwaway fixture test (20/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.tree_walk_one import (
    chunk_tree_walk_one,
    normalize_tree_walk_one,
    summarize_tree_walk_one,
)


def test_normalize_tree_walk_one_collapses_whitespace():
    assert normalize_tree_walk_one("  a   b  c ") == "a b c"


def test_chunk_tree_walk_one_splits_evenly():
    assert chunk_tree_walk_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_tree_walk_one_handles_empty_input():
    result = summarize_tree_walk_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
