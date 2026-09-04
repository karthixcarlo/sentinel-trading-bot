"""Throwaway fixture module (45/78) -- not real code, see ../README.md.

Generic, deliberately unremarkable utility functions. Exists purely to
give a review specialist a real, varied, moderately large surface area
to read across many files -- there is nothing security- or risk-area-
relevant here on purpose.
"""


def normalize_sorter_utils_two(value):
    """Trim, lowercase, and collapse whitespace in a string-ish value."""
    if value is None:
        return ""
    text = str(value).strip()
    parts = [p for p in text.split() if p]
    return " ".join(parts).lower()


def chunk_sorter_utils_two(items, size):
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


def summarize_sorter_utils_two(numbers):
    """Return (count, total, average) for a list of numbers, safely."""
    count = len(numbers)
    total = sum(numbers) if numbers else 0
    average = (total / count) if count else 0.0
    return {"count": count, "total": total, "average": average}


def dedupe_preserving_order_sorter_utils_two(items):
    """Remove duplicates from `items`, keeping first-seen order."""
    seen = set()
    result = []
    for item in items:
        marker = item if isinstance(item, (str, int, float, bool, type(None))) else id(item)
        if marker in seen:
            continue
        seen.add(marker)
        result.append(item)
    return result


def flatten_one_level_sorter_utils_two(nested):
    """Flatten a list of lists by exactly one level."""
    flat = []
    for group in nested:
        if isinstance(group, list):
            flat.extend(group)
        else:
            flat.append(group)
    return flat


def running_totals_sorter_utils_two(numbers):
    """Return the cumulative sum after each element."""
    running = []
    total = 0
    for value in numbers:
        total += value
        running.append(total)
    return running


def clamp_sorter_utils_two(value, low, high):
    """Constrain `value` to the closed interval [low, high]."""
    if low > high:
        raise ValueError("low must not exceed high")
    return max(low, min(value, high))


class SorterUtilsTwoHelper:
    """A small, self-contained stateful helper -- one per module, so a
    specialist reading this file has both free functions and a class to
    reason about, matching the shape of a real (if boring) module."""

    def __init__(self, label="sorter_utils_two"):
        self.label = label
        self._history = []

    def record(self, value):
        self._history.append(value)
        return len(self._history)

    def last(self, default=None):
        return self._history[-1] if self._history else default

    def reset(self):
        self._history = []
