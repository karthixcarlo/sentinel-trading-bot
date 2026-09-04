"""Throwaway fixture module 4/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_004.step_004(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_004 import step_004


def step_003(accumulated):
    """Append this step, then continue the chain."""
    return step_004(accumulated + [3])
