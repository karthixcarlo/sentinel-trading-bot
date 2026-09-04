"""Module 28 of 60 in a call chain. Calls into chain_028."""

from throwaway_live_verify_v4.chain_028 import step_028


def step_027(accumulated):
    """Append 27 to `accumulated`, then call step_028."""
    return step_028(accumulated + [27])
