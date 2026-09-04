"""Module 47 of 60 in a call chain. Calls into chain_047."""

from throwaway_live_verify_v4.chain_047 import step_047


def step_046(accumulated):
    """Append 46 to `accumulated`, then call step_047."""
    return step_047(accumulated + [46])
