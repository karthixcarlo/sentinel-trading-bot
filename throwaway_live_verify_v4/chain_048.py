"""Module 49 of 60 in a call chain. Calls into chain_049."""

from throwaway_live_verify_v4.chain_049 import step_049


def step_048(accumulated):
    """Append 48 to `accumulated`, then call step_049."""
    return step_049(accumulated + [48])
