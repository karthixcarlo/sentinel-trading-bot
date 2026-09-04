"""Module 39 of 60 in a call chain. Calls into chain_039."""

from throwaway_live_verify_v4.chain_039 import step_039


def step_038(accumulated):
    """Append 38 to `accumulated`, then call step_039."""
    return step_039(accumulated + [38])
