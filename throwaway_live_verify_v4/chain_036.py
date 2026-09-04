"""Module 37 of 60 in a call chain. Calls into chain_037."""

from throwaway_live_verify_v4.chain_037 import step_037


def step_036(accumulated):
    """Append 36 to `accumulated`, then call step_037."""
    return step_037(accumulated + [36])
