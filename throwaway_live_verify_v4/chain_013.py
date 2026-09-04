"""Throwaway fixture module 14/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_014.step_014(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_014 import step_014


def step_013(accumulated):
    """Append this step, then continue the chain."""
    return step_014(accumulated + [13])
