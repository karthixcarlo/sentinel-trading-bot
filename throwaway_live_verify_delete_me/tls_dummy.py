"""Throwaway fixture file — not real code, see ../README.md."""

import requests


def dummy_fetch_price_feed(url: str):
    """`verify=False` — disabled TLS certificate verification, intentional
    in this disposable fixture."""
    return requests.get(url, verify=False, timeout=5)  # noqa: S501
