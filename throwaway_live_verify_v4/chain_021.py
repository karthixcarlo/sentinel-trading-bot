"""Throwaway fixture module 22/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_022.step_022(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_022 import step_022


def step_021(accumulated):
    """Append this step, then continue the chain."""
    return step_022(accumulated + [21])
