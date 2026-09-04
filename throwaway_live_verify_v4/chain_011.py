"""Module 12 of 60 in a call chain. Calls into chain_012."""

from throwaway_live_verify_v4.chain_012 import step_012


def step_011(accumulated):
    """Append 11 to `accumulated`, then call step_012."""
    return step_012(accumulated + [11])
