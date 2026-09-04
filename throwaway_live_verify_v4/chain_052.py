"""Module 53 of 60 in a call chain. Calls into chain_053."""

from throwaway_live_verify_v4.chain_053 import step_053


def step_052(accumulated):
    """Append 52 to `accumulated`, then call step_053."""
    return step_053(accumulated + [52])
