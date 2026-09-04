"""Throwaway fixture module 26/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_026.step_026(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_026 import step_026


def step_025(accumulated):
    """Append this step, then continue the chain."""
    return step_026(accumulated + [25])
