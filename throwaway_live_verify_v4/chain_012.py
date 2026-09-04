"""Module 13 of 60 in a call chain. Calls into chain_013."""

from throwaway_live_verify_v4.chain_013 import step_013


def step_012(accumulated):
    """Append 12 to `accumulated`, then call step_013."""
    return step_013(accumulated + [12])
