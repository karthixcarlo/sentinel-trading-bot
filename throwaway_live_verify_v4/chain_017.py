"""Module 18 of 60 in a call chain. Calls into chain_018."""

from throwaway_live_verify_v4.chain_018 import step_018


def step_017(accumulated):
    """Append 17 to `accumulated`, then call step_018."""
    return step_018(accumulated + [17])
