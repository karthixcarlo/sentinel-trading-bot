"""Module 19 of 60 in a call chain. Calls into chain_019."""

from throwaway_live_verify_v4.chain_019 import step_019


def step_018(accumulated):
    """Append 18 to `accumulated`, then call step_019."""
    return step_019(accumulated + [18])
