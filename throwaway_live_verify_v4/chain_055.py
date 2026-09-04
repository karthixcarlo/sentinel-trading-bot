"""Module 56 of 60 in a call chain. Calls into chain_056."""

from throwaway_live_verify_v4.chain_056 import step_056


def step_055(accumulated):
    """Append 55 to `accumulated`, then call step_056."""
    return step_056(accumulated + [55])
