"""Throwaway fixture module 54/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_054.step_054(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_054 import step_054


def step_053(accumulated):
    """Append this step, then continue the chain."""
    return step_054(accumulated + [53])
