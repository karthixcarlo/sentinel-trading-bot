"""Module 42 of 60 in a call chain. Calls into chain_042."""

from throwaway_live_verify_v4.chain_042 import step_042


def step_041(accumulated):
    """Append 41 to `accumulated`, then call step_042."""
    return step_042(accumulated + [41])
