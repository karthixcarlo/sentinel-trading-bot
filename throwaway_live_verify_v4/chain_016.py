"""Module 17 of 60 in a call chain. Calls into chain_017."""

from throwaway_live_verify_v4.chain_017 import step_017


def step_016(accumulated):
    """Append 16 to `accumulated`, then call step_017."""
    return step_017(accumulated + [16])
