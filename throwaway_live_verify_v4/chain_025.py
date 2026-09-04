"""Module 26 of 60 in a call chain. Calls into chain_026."""

from throwaway_live_verify_v4.chain_026 import step_026


def step_025(accumulated):
    """Append 25 to `accumulated`, then call step_026."""
    return step_026(accumulated + [25])
