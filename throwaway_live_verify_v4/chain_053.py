"""Module 54 of 60 in a call chain. Calls into chain_054."""

from throwaway_live_verify_v4.chain_054 import step_054


def step_053(accumulated):
    """Append 53 to `accumulated`, then call step_054."""
    return step_054(accumulated + [53])
