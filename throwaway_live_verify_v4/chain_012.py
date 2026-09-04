"""Throwaway fixture module 13/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_013.step_013(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_013 import step_013


def step_012(accumulated):
    """Append this step, then continue the chain."""
    return step_013(accumulated + [12])
