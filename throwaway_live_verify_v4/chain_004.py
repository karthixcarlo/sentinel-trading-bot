"""Throwaway fixture module 5/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_005.step_005(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_005 import step_005


def step_004(accumulated):
    """Append this step, then continue the chain."""
    return step_005(accumulated + [4])
