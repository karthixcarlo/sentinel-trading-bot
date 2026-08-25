"""Formats a fill confirmation message for a filled order.

A small, isolated utility split out for a reply-triggered-approval
verification run -- deliberately independent of everything else in the
repository so this change cannot collide with anything real.
"""


def format_fill_message(symbol: str, quantity: int, price: float) -> str:
    """Human-readable confirmation text for one filled order."""
    return f"Filled {quantity} {symbol} @ {price:.2f}"
