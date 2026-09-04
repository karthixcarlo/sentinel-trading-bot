"""Throwaway fixture module 30/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_030.step_030(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_030 import step_030


def step_029(accumulated):
    """Append this step, then continue the chain."""
    return step_030(accumulated + [29])
