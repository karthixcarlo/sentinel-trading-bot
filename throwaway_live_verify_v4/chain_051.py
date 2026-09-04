"""Throwaway fixture module 52/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_052.step_052(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_052 import step_052


def step_051(accumulated):
    """Append this step, then continue the chain."""
    return step_052(accumulated + [51])
