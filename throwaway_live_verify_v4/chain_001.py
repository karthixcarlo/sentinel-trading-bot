"""Module 2 of 60 in a call chain. Calls into chain_002."""

from throwaway_live_verify_v4.chain_002 import step_002


def step_001(accumulated):
    """Append 1 to `accumulated`, then call step_002."""
    return step_002(accumulated + [1])
