# -*- coding: utf-8 -*-
"""
Slippage Guard - Execution Quality Check

Computes the realized slippage (in basis points) between an order's
expected price and its actual fill price, and rejects fills that slipped
past the configured tolerance before the trade is recorded.

Usage:
    from slippage_guard import calculate_slippage_bps

    bps = calculate_slippage_bps(expected_price=2900.50, fill_price=2905.75)
"""

MAX_SLIPPAGE_BPS = 25  # 0.25% -- mirrors the tolerance used by the paper executor


def calculate_slippage_bps(expected_price: float, fill_price: float) -> float:
    """
    Return the signed slippage between the expected and filled price, in
    basis points. Positive means the fill was worse than expected for a
    long entry.
    """
    return (fill_price - expected_price) / expected_price * 10000


def is_fill_within_tolerance(expected_price: float, fill_price: float, max_bps: float = MAX_SLIPPAGE_BPS) -> bool:
    """
    True if the fill's slippage is within the allowed tolerance.
    """
    return abs(calculate_slippage_bps(expected_price, fill_price)) <= max_bps
