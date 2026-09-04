"""Throwaway fixture module 6/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_006.step_006(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_006 import step_006


def step_005(accumulated):
    """Append this step, then continue the chain."""
    return step_006(accumulated + [5])
