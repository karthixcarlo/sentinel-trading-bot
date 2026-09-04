"""Throwaway fixture test (14/78) -- not a real test, see ../README.md."""

from throwaway_live_verify_v3.event_bus_one import (
    chunk_event_bus_one,
    normalize_event_bus_one,
    summarize_event_bus_one,
)


def test_normalize_event_bus_one_collapses_whitespace():
    assert normalize_event_bus_one("  a   b  c ") == "a b c"


def test_chunk_event_bus_one_splits_evenly():
    assert chunk_event_bus_one([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_summarize_event_bus_one_handles_empty_input():
    result = summarize_event_bus_one([])
    assert result["count"] == 0
    assert result["average"] == 0.0
