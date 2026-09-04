"""Module 38 of 60 in a call chain. Calls into chain_038."""

from throwaway_live_verify_v4.chain_038 import step_038


def step_037(accumulated):
    """Append 37 to `accumulated`, then call step_038."""
    return step_038(accumulated + [37])
