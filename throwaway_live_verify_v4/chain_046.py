"""Throwaway fixture module 47/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_047.step_047(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_047 import step_047


def step_046(accumulated):
    """Append this step, then continue the chain."""
    return step_047(accumulated + [46])
