"""Module 44 of 60 in a call chain. Calls into chain_044."""

from throwaway_live_verify_v4.chain_044 import step_044


def step_043(accumulated):
    """Append 43 to `accumulated`, then call step_044."""
    return step_044(accumulated + [43])
