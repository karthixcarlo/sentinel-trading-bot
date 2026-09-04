"""Throwaway fixture module 55/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_055.step_055(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_055 import step_055


def step_054(accumulated):
    """Append this step, then continue the chain."""
    return step_055(accumulated + [54])
