"""Module 57 of 60 in a call chain. Calls into chain_057."""

from throwaway_live_verify_v4.chain_057 import step_057


def step_056(accumulated):
    """Append 56 to `accumulated`, then call step_057."""
    return step_057(accumulated + [56])
