"""Throwaway fixture module 3/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_003.step_003(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_003 import step_003


def step_002(accumulated):
    """Append this step, then continue the chain."""
    return step_003(accumulated + [2])
