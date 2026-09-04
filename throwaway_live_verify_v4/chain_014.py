"""Throwaway fixture module 15/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_015.step_015(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_015 import step_015


def step_014(accumulated):
    """Append this step, then continue the chain."""
    return step_015(accumulated + [14])
