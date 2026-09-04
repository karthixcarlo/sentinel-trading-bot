"""Throwaway fixture module 33/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_033.step_033(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_033 import step_033


def step_032(accumulated):
    """Append this step, then continue the chain."""
    return step_033(accumulated + [32])
