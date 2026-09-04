"""Module 24 of 60 in a call chain. Calls into chain_024."""

from throwaway_live_verify_v4.chain_024 import step_024


def step_023(accumulated):
    """Append 23 to `accumulated`, then call step_024."""
    return step_024(accumulated + [23])
