"""Throwaway fixture module 59/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_059.step_059(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_059 import step_059


def step_058(accumulated):
    """Append this step, then continue the chain."""
    return step_059(accumulated + [58])
