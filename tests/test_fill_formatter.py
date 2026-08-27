"""services/fill_formatter.py must never report a negative fill quantity."""

from services.fill_formatter import format_fill_message


def test_a_normal_fill_formats_correctly():
    assert format_fill_message("TCS", 10, 3500.5) == "Filled 10 TCS @ 3500.50"


def test_a_negative_quantity_is_reported_as_zero_not_negative():
    assert format_fill_message("TCS", -3, 3500.5) == "Filled 0 TCS @ 3500.50"
