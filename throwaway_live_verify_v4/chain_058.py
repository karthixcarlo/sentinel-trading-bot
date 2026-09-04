"""Module 59 of 60 in a call chain. Calls into chain_059."""

from throwaway_live_verify_v4.chain_059 import step_059


def step_058(accumulated):
    """Append 58 to `accumulated`, then call step_059."""
    return step_059(accumulated + [58])
