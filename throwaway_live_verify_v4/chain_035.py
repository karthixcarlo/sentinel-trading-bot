"""Throwaway fixture module 36/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_036.step_036(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_036 import step_036


def step_035(accumulated):
    """Append this step, then continue the chain."""
    return step_036(accumulated + [35])
