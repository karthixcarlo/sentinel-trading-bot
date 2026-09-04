"""Throwaway fixture module 10/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_010.step_010(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_010 import step_010


def step_009(accumulated):
    """Append this step, then continue the chain."""
    return step_010(accumulated + [9])
