"""Throwaway fixture module 8/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_008.step_008(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_008 import step_008


def step_007(accumulated):
    """Append this step, then continue the chain."""
    return step_008(accumulated + [7])
