"""Throwaway fixture module 34/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_034.step_034(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_034 import step_034


def step_033(accumulated):
    """Append this step, then continue the chain."""
    return step_034(accumulated + [33])
