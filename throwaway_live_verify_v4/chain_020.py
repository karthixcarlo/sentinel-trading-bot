"""Module 21 of 60 in a call chain. Calls into chain_021."""

from throwaway_live_verify_v4.chain_021 import step_021


def step_020(accumulated):
    """Append 20 to `accumulated`, then call step_021."""
    return step_021(accumulated + [20])
