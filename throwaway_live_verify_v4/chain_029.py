"""Module 30 of 60 in a call chain. Calls into chain_030."""

from throwaway_live_verify_v4.chain_030 import step_030


def step_029(accumulated):
    """Append 29 to `accumulated`, then call step_030."""
    return step_030(accumulated + [29])
