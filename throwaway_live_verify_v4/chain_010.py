"""Throwaway fixture module 11/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_011.step_011(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_011 import step_011


def step_010(accumulated):
    """Append this step, then continue the chain."""
    return step_011(accumulated + [10])
