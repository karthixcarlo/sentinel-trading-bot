"""Throwaway fixture module 38/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_038.step_038(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_038 import step_038


def step_037(accumulated):
    """Append this step, then continue the chain."""
    return step_038(accumulated + [37])
