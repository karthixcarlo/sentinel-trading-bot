"""Throwaway fixture module 57/60 -- not real code, see ../README.md.

Part of a deliberate call chain: this step appends its own number, then hands off to chain_057.step_057(). Understanding the final result of the chain means following it all the way through -- that's the point of this fixture (see ../README.md).
"""

from throwaway_live_verify_v4.chain_057 import step_057


def step_056(accumulated):
    """Append this step, then continue the chain."""
    return step_057(accumulated + [56])
