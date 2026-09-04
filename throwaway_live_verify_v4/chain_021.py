"""Module 22 of 60 in a call chain. Calls into chain_022."""

from throwaway_live_verify_v4.chain_022 import step_022


def step_021(accumulated):
    """Append 21 to `accumulated`, then call step_022."""
    return step_022(accumulated + [21])
