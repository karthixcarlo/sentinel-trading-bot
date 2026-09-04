"""Module 9 of 60 in a call chain. Calls into chain_009."""

from throwaway_live_verify_v4.chain_009 import step_009


def step_008(accumulated):
    """Append 8 to `accumulated`, then call step_009."""
    return step_009(accumulated + [8])
