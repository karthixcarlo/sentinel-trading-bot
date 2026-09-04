"""Throwaway fixture test (19/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.sorter_utils import (
    chunk_sorter_utils,
    normalize_sorter_utils,
    summarize_sorter_utils,
)


def test_normalize_sorter_utils_collapses_whitespace():
    assert normalize_sorter_utils("  a   b  c ") == "a b c"


def test_chunk_sorter_utils_splits_evenly():
    assert chunk_sorter_utils([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_sorter_utils_handles_empty_input():
    result = summarize_sorter_utils([])
    assert result["count"] == 0
    assert result["average"] == 0.0
