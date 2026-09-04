"""Module 58 of 60 in a call chain. Calls into chain_058."""

from throwaway_live_verify_v4.chain_058 import step_058


def step_057(accumulated):
    """Append 57 to `accumulated`, then call step_058."""
    return step_058(accumulated + [57])
