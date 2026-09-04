"""Module 3 of 60 in a call chain. Calls into chain_003."""

from throwaway_live_verify_v4.chain_003 import step_003


def step_002(accumulated):
    """Append 2 to `accumulated`, then call step_003."""
    return step_003(accumulated + [2])
