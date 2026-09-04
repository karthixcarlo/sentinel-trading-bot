"""Throwaway fixture test (66/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.event_bus_three import (
    chunk_event_bus_three,
    normalize_event_bus_three,
    summarize_event_bus_three,
)


def test_normalize_event_bus_three_collapses_whitespace():
    assert normalize_event_bus_three("  a   b  c ") == "a b c"


def test_chunk_event_bus_three_splits_evenly():
    assert chunk_event_bus_three([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_event_bus_three_handles_empty_input():
    result = summarize_event_bus_three([])
    assert result["count"] == 0
    assert result["average"] == 0.0
