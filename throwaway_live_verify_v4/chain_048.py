"""Throwaway fixture module 49/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_049.step_049(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_049 import step_049


def step_048(accumulated):
    """Append this step, then continue the chain."""
    return step_049(accumulated + [48])
