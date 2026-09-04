"""Throwaway fixture module 31/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_031.step_031(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_031 import step_031


def step_030(accumulated):
    """Append this step, then continue the chain."""
    return step_031(accumulated + [30])
