"""Throwaway fixture module 41/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_041.step_041(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_041 import step_041


def step_040(accumulated):
    """Append this step, then continue the chain."""
    return step_041(accumulated + [40])
