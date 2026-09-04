"""Module 52 of 60 in a call chain. Calls into chain_052."""

from throwaway_live_verify_v4.chain_052 import step_052


def step_051(accumulated):
    """Append 51 to `accumulated`, then call step_052."""
    return step_052(accumulated + [51])
