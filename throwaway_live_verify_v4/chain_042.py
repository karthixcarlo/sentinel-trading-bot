"""Throwaway fixture module 43/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_043.step_043(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_043 import step_043


def step_042(accumulated):
    """Append this step, then continue the chain."""
    return step_043(accumulated + [42])
