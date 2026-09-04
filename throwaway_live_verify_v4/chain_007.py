"""Module 8 of 60 in a call chain. Calls into chain_008."""

from throwaway_live_verify_v4.chain_008 import step_008


def step_007(accumulated):
    """Append 7 to `accumulated`, then call step_008."""
    return step_008(accumulated + [7])
