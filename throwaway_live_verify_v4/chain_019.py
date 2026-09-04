"""Throwaway fixture module 20/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_020.step_020(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_020 import step_020


def step_019(accumulated):
    """Append this step, then continue the chain."""
    return step_020(accumulated + [19])
