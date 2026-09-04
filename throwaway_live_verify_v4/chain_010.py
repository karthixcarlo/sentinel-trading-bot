"""Module 11 of 60 in a call chain. Calls into chain_011."""

from throwaway_live_verify_v4.chain_011 import step_011


def step_010(accumulated):
    """Append 10 to `accumulated`, then call step_011."""
    return step_011(accumulated + [10])
