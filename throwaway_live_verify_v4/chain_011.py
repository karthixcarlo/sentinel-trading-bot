"""Throwaway fixture module 12/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_012.step_012(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_012 import step_012


def step_011(accumulated):
    """Append this step, then continue the chain."""
    return step_012(accumulated + [11])
