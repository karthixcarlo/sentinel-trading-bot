"""Module 46 of 60 in a call chain. Calls into chain_046."""

from throwaway_live_verify_v4.chain_046 import step_046


def step_045(accumulated):
    """Append 45 to `accumulated`, then call step_046."""
    return step_046(accumulated + [45])
