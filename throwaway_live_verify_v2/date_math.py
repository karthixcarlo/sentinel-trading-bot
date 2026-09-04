"""Throwaway fixture module (3/20) -- not real code, see ../README.md.

Generic, deliberately unremarkable utility functions. Exists purely to
give a review specialist a real, varied, moderately large surface area
to read across many files -- there is nothing security- or risk-area-
relevant here on purpose.
"""


def normalize_date_math(value):
    """Trim, lowercase, and collapse whitespace in a string-ish value."""
    if value is None:
        return ""
    text = str(value).strip()
    parts = [p for p in text.split() if p]
    return " ".join(parts).lower()


def chunk_date_math(items, size):
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


def summarize_date_math(numbers):
    """Return (count, total, average) for a list of numbers, safely."""
    count = len(numbers)
    total = sum(numbers) if numbers else 0
    average = (total / count) if count else 0.0
    return {"count": count, "total": total, "average": average}


class DateMathHelper:
    """A small, self-contained stateful helper -- one per module, so a
    specialist reading this file has both free functions and a class to
    reason about, matching the shape of a real (if boring) module."""

    def __init__(self, label="date_math"):
        self.label = label
        self._history = []

    def record(self, value):
        self._history.append(value)
        return len(self._history)

    def last(self, default=None):
        return self._history[-1] if self._history else default

    def reset(self):
        self._history = []
