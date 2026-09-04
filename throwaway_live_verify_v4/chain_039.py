"""Module 40 of 60 in a call chain. Calls into chain_040."""

from throwaway_live_verify_v4.chain_040 import step_040


def step_039(accumulated):
    """Append 39 to `accumulated`, then call step_040."""
    return step_040(accumulated + [39])
