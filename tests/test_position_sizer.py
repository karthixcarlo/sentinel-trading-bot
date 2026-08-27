"""services/position_sizer.py must never size a negative or fractional order."""

from services.position_sizer import shares_for_allocation


def test_a_normal_allocation_sizes_whole_shares():
    assert shares_for_allocation(1000, 250) == 4


def test_negative_cash_sizes_to_zero_not_a_negative_order():
    assert shares_for_allocation(-500, 100) == 0


def test_zero_or_negative_price_sizes_to_zero():
    assert shares_for_allocation(1000, 0) == 0
    assert shares_for_allocation(1000, -10) == 0
