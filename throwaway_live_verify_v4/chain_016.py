"""Throwaway fixture module 17/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_017.step_017(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_017 import step_017


def step_016(accumulated):
    """Append this step, then continue the chain."""
    return step_017(accumulated + [16])
