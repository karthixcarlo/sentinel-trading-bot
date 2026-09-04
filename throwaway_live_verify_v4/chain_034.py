"""Throwaway fixture module 35/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_035.step_035(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_035 import step_035


def step_034(accumulated):
    """Append this step, then continue the chain."""
    return step_035(accumulated + [34])
