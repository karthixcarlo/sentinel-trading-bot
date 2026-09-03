# -*- coding: utf-8 -*-
"""Tests for slippage_guard."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services"))

from slippage_guard import calculate_slippage_bps, is_fill_within_tolerance


def test_positive_slippage_when_fill_is_worse():
    bps = calculate_slippage_bps(expected_price=100.0, fill_price=100.5)
    assert bps == 50.0


def test_negative_slippage_when_fill_is_better():
    bps = calculate_slippage_bps(expected_price=100.0, fill_price=99.5)
    assert bps == -50.0


def test_fill_within_default_tolerance():
    assert is_fill_within_tolerance(expected_price=100.0, fill_price=100.1) is True


def test_fill_outside_default_tolerance():
    assert is_fill_within_tolerance(expected_price=100.0, fill_price=101.0) is False
