"""Throwaway fixture test (14/20) -- not a real test, see ../README.md."""

from throwaway_live_verify_v2.event_bus import (
    chunk_event_bus,
    normalize_event_bus,
    summarize_event_bus,
)


def test_normalize_event_bus_collapses_whitespace():
    assert normalize_event_bus("  a   b  c ") == "a b c"


def test_chunk_event_bus_splits_evenly():
    assert chunk_event_bus([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_event_bus_handles_empty_input():
    result = summarize_event_bus([])
    assert result["count"] == 0
    assert result["average"] == 0.0
