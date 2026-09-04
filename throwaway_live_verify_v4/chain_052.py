"""Throwaway fixture module 53/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_053.step_053(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_053 import step_053


def step_052(accumulated):
    """Append this step, then continue the chain."""
    return step_053(accumulated + [52])
