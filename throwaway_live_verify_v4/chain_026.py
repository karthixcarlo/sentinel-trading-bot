"""Throwaway fixture module 27/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_027.step_027(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_027 import step_027


def step_026(accumulated):
    """Append this step, then continue the chain."""
    return step_027(accumulated + [26])
