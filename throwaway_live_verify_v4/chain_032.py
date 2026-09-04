"""Module 33 of 60 in a call chain. Calls into chain_033."""

from throwaway_live_verify_v4.chain_033 import step_033


def step_032(accumulated):
    """Append 32 to `accumulated`, then call step_033."""
    return step_033(accumulated + [32])
