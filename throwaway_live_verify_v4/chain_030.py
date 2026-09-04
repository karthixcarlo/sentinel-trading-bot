"""Module 31 of 60 in a call chain. Calls into chain_031."""

from throwaway_live_verify_v4.chain_031 import step_031


def step_030(accumulated):
    """Append 30 to `accumulated`, then call step_031."""
    return step_031(accumulated + [30])
