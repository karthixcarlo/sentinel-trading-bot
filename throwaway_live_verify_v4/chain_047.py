"""Module 48 of 60 in a call chain. Calls into chain_048."""

from throwaway_live_verify_v4.chain_048 import step_048


def step_047(accumulated):
    """Append 47 to `accumulated`, then call step_048."""
    return step_048(accumulated + [47])
