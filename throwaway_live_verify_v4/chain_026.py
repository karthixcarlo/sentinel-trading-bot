"""Module 27 of 60 in a call chain. Calls into chain_027."""

from throwaway_live_verify_v4.chain_027 import step_027


def step_026(accumulated):
    """Append 26 to `accumulated`, then call step_027."""
    return step_027(accumulated + [26])
