"""Throwaway fixture module 45/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_045.step_045(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_045 import step_045


def step_044(accumulated):
    """Append this step, then continue the chain."""
    return step_045(accumulated + [44])
