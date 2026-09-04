"""Throwaway fixture module 16/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_016.step_016(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_016 import step_016


def step_015(accumulated):
    """Append this step, then continue the chain."""
    return step_016(accumulated + [15])
