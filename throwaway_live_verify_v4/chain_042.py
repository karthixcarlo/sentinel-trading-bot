"""Module 43 of 60 in a call chain. Calls into chain_043."""

from throwaway_live_verify_v4.chain_043 import step_043


def step_042(accumulated):
    """Append 42 to `accumulated`, then call step_043."""
    return step_043(accumulated + [42])
