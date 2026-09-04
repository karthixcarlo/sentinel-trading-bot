"""Module 32 of 60 in a call chain. Calls into chain_032."""

from throwaway_live_verify_v4.chain_032 import step_032


def step_031(accumulated):
    """Append 31 to `accumulated`, then call step_032."""
    return step_032(accumulated + [31])
