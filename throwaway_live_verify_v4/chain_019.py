"""Module 20 of 60 in a call chain. Calls into chain_020."""

from throwaway_live_verify_v4.chain_020 import step_020


def step_019(accumulated):
    """Append 19 to `accumulated`, then call step_020."""
    return step_020(accumulated + [19])
