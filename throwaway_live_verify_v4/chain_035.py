"""Module 36 of 60 in a call chain. Calls into chain_036."""

from throwaway_live_verify_v4.chain_036 import step_036


def step_035(accumulated):
    """Append 35 to `accumulated`, then call step_036."""
    return step_036(accumulated + [35])
