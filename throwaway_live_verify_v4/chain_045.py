"""Throwaway fixture module 46/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_046.step_046(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_046 import step_046


def step_045(accumulated):
    """Append this step, then continue the chain."""
    return step_046(accumulated + [45])
