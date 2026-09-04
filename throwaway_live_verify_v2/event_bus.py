"""Throwaway fixture module (14/20) -- not real code, see ../README.md.

Generic, deliberately unremarkable utility functions. Exists purely to
give a review specialist a real, varied, moderately large surface area
to read across many files -- there is nothing security- or risk-area-
relevant here on purpose.
"""


def normalize_event_bus(value):
    """Trim, lowercase, and collapse whitespace in a string-ish value."""
    if value is None:
        return ""
    text = str(value).strip()
    parts = [p for p in text.split() if p]
    return " ".join(parts).lower()


def chunk_event_bus(items, size):
    """Split `items` into consecutive chunks of at most `size`."""
    if size <= 0:
        raise ValueError("size must be positive")
    result = []
    current = []
    for item in items:
        current.append(item)
        if len(current) == size:
            result.append(current)
            current = []
    if current:
        result.append(current)
    return result


def summarize_event_bus(numbers):
    """Return (count, total, average) for a list of numbers, safely."""
    count = len(numbers)
    total = sum(numbers) if numbers else 0
    average = (total / count) if count else 0.0
    return {"count": count, "total": total, "average": average}


class EventBusHelper:
    """A small, self-contained stateful helper -- one per module, so a
    specialist reading this file has both free functions and a class to
    reason about, matching the shape of a real (if boring) module."""

    def __init__(self, label="event_bus"):
        self.label = label
        self._history = []

    def record(self, value):
        self._history.append(value)
        return len(self._history)

    def last(self, default=None):
        return self._history[-1] if self._history else default

    def reset(self):
        self._history = []
