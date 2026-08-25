"""Computes how many whole shares a fixed cash allocation buys.

A small, isolated utility split out for a state-persistence verification
run -- deliberately independent of services/broker_engine.py so this
change cannot collide with anything else in the repository.
"""


def shares_for_allocation(cash: float, price: float) -> int:
    """How many whole shares `cash` buys at `price`.

    Must never return a negative or fractional share count -- a broker
    order for -3 shares or 4.5 shares is not a valid order.
    """
    if cash <= 0 or price <= 0:
        return 0
    return int(cash / price)
