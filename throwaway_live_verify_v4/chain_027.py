"""Throwaway fixture module 28/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_028.step_028(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_028 import step_028


def step_027(accumulated):
    """Append this step, then continue the chain."""
    return step_028(accumulated + [27])
