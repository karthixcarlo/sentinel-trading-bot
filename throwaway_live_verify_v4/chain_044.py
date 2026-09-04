"""Module 45 of 60 in a call chain. Calls into chain_045."""

from throwaway_live_verify_v4.chain_045 import step_045


def step_044(accumulated):
    """Append 44 to `accumulated`, then call step_045."""
    return step_045(accumulated + [44])
