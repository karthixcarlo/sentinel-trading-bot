"""Module 41 of 60 in a call chain. Calls into chain_041."""

from throwaway_live_verify_v4.chain_041 import step_041


def step_040(accumulated):
    """Append 40 to `accumulated`, then call step_041."""
    return step_041(accumulated + [40])
