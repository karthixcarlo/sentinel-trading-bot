"""Throwaway fixture module 51/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_051.step_051(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_051 import step_051


def step_050(accumulated):
    """Append this step, then continue the chain."""
    return step_051(accumulated + [50])
