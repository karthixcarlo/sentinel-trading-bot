"""Throwaway fixture module 48/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_048.step_048(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_048 import step_048


def step_047(accumulated):
    """Append this step, then continue the chain."""
    return step_048(accumulated + [47])
