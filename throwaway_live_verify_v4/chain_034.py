"""Module 35 of 60 in a call chain. Calls into chain_035."""

from throwaway_live_verify_v4.chain_035 import step_035


def step_034(accumulated):
    """Append 34 to `accumulated`, then call step_035."""
    return step_035(accumulated + [34])
