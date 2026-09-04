"""Throwaway fixture module 2/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_002.step_002(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_002 import step_002


def step_001(accumulated):
    """Append this step, then continue the chain."""
    return step_002(accumulated + [1])
