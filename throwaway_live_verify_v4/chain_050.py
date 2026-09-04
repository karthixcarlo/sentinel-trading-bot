"""Module 51 of 60 in a call chain. Calls into chain_051."""

from throwaway_live_verify_v4.chain_051 import step_051


def step_050(accumulated):
    """Append 50 to `accumulated`, then call step_051."""
    return step_051(accumulated + [50])
