"""Throwaway fixture test (40/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.event_bus_two import (
    chunk_event_bus_two,
    normalize_event_bus_two,
    summarize_event_bus_two,
)


def test_normalize_event_bus_two_collapses_whitespace():
    assert normalize_event_bus_two("  a   b  c ") == "a b c"


def test_chunk_event_bus_two_splits_evenly():
    assert chunk_event_bus_two([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_event_bus_two_handles_empty_input():
    result = summarize_event_bus_two([])
    assert result["count"] == 0
    assert result["average"] == 0.0
