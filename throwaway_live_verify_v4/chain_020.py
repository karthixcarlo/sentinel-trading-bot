"""Throwaway fixture module 21/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_021.step_021(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_021 import step_021


def step_020(accumulated):
    """Append this step, then continue the chain."""
    return step_021(accumulated + [20])
