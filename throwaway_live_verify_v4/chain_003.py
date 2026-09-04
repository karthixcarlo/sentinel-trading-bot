"""Module 4 of 60 in a call chain. Calls into chain_004."""

from throwaway_live_verify_v4.chain_004 import step_004


def step_003(accumulated):
    """Append 3 to `accumulated`, then call step_004."""
    return step_004(accumulated + [3])
