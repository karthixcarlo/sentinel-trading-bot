"""Module 23 of 60 in a call chain. Calls into chain_023."""

from throwaway_live_verify_v4.chain_023 import step_023


def step_022(accumulated):
    """Append 22 to `accumulated`, then call step_023."""
    return step_023(accumulated + [22])
