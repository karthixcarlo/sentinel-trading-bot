"""Module 55 of 60 in a call chain. Calls into chain_055."""

from throwaway_live_verify_v4.chain_055 import step_055


def step_054(accumulated):
    """Append 54 to `accumulated`, then call step_055."""
    return step_055(accumulated + [54])
