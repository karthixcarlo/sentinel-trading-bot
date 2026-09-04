"""Throwaway fixture module 50/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_050.step_050(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_050 import step_050


def step_049(accumulated):
    """Append this step, then continue the chain."""
    return step_050(accumulated + [49])
