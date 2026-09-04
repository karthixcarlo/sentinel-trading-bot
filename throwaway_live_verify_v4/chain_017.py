"""Throwaway fixture module 18/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_018.step_018(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_018 import step_018


def step_017(accumulated):
    """Append this step, then continue the chain."""
    return step_018(accumulated + [17])
