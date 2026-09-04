"""Module 25 of 60 in a call chain. Calls into chain_025."""

from throwaway_live_verify_v4.chain_025 import step_025


def step_024(accumulated):
    """Append 24 to `accumulated`, then call step_025."""
    return step_025(accumulated + [24])
