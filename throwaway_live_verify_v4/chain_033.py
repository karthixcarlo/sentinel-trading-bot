"""Module 34 of 60 in a call chain. Calls into chain_034."""

from throwaway_live_verify_v4.chain_034 import step_034


def step_033(accumulated):
    """Append 33 to `accumulated`, then call step_034."""
    return step_034(accumulated + [33])
