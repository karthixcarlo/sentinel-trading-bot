"""Throwaway fixture module 56/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_056.step_056(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_056 import step_056


def step_055(accumulated):
    """Append this step, then continue the chain."""
    return step_056(accumulated + [55])
