"""Throwaway fixture module 1/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_001.step_001(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_001 import step_001


def step_000(accumulated):
    """Append this step, then continue the chain."""
    return step_001(accumulated + [0])
