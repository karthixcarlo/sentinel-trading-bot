"""Throwaway fixture test (21/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.graph_ops_one import (
    chunk_graph_ops_one,
    normalize_graph_ops_one,
    summarize_graph_ops_one,
)


def test_normalize_graph_ops_one_collapses_whitespace():
    assert normalize_graph_ops_one("  a   b  c ") == "a b c"


def test_chunk_graph_ops_one_splits_evenly():
    assert chunk_graph_ops_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_graph_ops_one_handles_empty_input():
    result = summarize_graph_ops_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
