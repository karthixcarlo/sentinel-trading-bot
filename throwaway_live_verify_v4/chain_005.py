"""Module 6 of 60 in a call chain. Calls into chain_006."""

from throwaway_live_verify_v4.chain_006 import step_006


def step_005(accumulated):
    """Append 5 to `accumulated`, then call step_006."""
    return step_006(accumulated + [5])
