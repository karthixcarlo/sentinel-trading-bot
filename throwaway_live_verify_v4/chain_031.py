"""Throwaway fixture module 32/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_032.step_032(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_032 import step_032


def step_031(accumulated):
    """Append this step, then continue the chain."""
    return step_032(accumulated + [31])
