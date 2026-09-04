"""Module 10 of 60 in a call chain. Calls into chain_010."""

from throwaway_live_verify_v4.chain_010 import step_010


def step_009(accumulated):
    """Append 9 to `accumulated`, then call step_010."""
    return step_010(accumulated + [9])
