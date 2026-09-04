"""Module 29 of 60 in a call chain. Calls into chain_029."""

from throwaway_live_verify_v4.chain_029 import step_029


def step_028(accumulated):
    """Append 28 to `accumulated`, then call step_029."""
    return step_029(accumulated + [28])
