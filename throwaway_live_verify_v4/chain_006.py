"""Module 7 of 60 in a call chain. Calls into chain_007."""

from throwaway_live_verify_v4.chain_007 import step_007


def step_006(accumulated):
    """Append 6 to `accumulated`, then call step_007."""
    return step_007(accumulated + [6])
