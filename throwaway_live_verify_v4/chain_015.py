"""Module 16 of 60 in a call chain. Calls into chain_016."""

from throwaway_live_verify_v4.chain_016 import step_016


def step_015(accumulated):
    """Append 15 to `accumulated`, then call step_016."""
    return step_016(accumulated + [15])
