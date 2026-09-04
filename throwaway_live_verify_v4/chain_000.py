"""Module 1 of 60 in a call chain. Calls into chain_001."""

from throwaway_live_verify_v4.chain_001 import step_001


def step_000(accumulated):
    """Append 0 to `accumulated`, then call step_001."""
    return step_001(accumulated + [0])
