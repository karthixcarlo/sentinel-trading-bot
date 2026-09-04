"""Throwaway fixture test -- not a real test, see ../README.md."""

from throwaway_live_verify_v4.chain_000 import step_000


def test_full_chain_visits_every_step_in_order():
    assert step_000([]) == list(range(60))
