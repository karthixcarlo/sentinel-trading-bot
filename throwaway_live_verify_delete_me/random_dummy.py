"""Throwaway fixture file — not real code, see ../README.md."""

import random
import string


def dummy_generate_reset_token() -> str:
    """`random`, not `secrets` — predictable token generation, intentional
    in this disposable fixture."""
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
