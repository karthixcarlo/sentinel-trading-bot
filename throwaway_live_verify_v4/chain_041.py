"""Throwaway fixture module 42/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_042.step_042(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_042 import step_042


def step_041(accumulated):
    """Append this step, then continue the chain."""
    return step_042(accumulated + [41])
