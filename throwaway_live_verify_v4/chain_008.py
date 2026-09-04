"""Throwaway fixture module 9/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_009.step_009(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_009 import step_009


def step_008(accumulated):
    """Append this step, then continue the chain."""
    return step_009(accumulated + [8])
