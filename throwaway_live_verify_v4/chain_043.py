"""Throwaway fixture module 44/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_044.step_044(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_044 import step_044


def step_043(accumulated):
    """Append this step, then continue the chain."""
    return step_044(accumulated + [43])
