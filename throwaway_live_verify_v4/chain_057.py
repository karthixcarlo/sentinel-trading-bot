"""Throwaway fixture module 58/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_058.step_058(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_058 import step_058


def step_057(accumulated):
    """Append this step, then continue the chain."""
    return step_058(accumulated + [57])
