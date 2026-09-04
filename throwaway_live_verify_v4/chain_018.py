"""Throwaway fixture module 19/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_019.step_019(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_019 import step_019


def step_018(accumulated):
    """Append this step, then continue the chain."""
    return step_019(accumulated + [18])
