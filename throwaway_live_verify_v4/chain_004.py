"""Module 5 of 60 in a call chain. Calls into chain_005."""

from throwaway_live_verify_v4.chain_005 import step_005


def step_004(accumulated):
    """Append 4 to `accumulated`, then call step_005."""
    return step_005(accumulated + [4])
