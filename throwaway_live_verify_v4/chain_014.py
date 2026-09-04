"""Module 15 of 60 in a call chain. Calls into chain_015."""

from throwaway_live_verify_v4.chain_015 import step_015


def step_014(accumulated):
    """Append 14 to `accumulated`, then call step_015."""
    return step_015(accumulated + [14])
