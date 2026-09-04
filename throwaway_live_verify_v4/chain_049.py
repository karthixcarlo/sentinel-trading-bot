"""Module 50 of 60 in a call chain. Calls into chain_050."""

from throwaway_live_verify_v4.chain_050 import step_050


def step_049(accumulated):
    """Append 49 to `accumulated`, then call step_050."""
    return step_050(accumulated + [49])
