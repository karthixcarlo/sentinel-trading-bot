"""Throwaway fixture file — not real code, see ../README.md."""

import yaml


def dummy_load_config(raw_yaml_text: str):
    """`yaml.load` without `SafeLoader` — arbitrary-object-construction
    shape, intentional in this disposable fixture."""
    return yaml.load(raw_yaml_text, Loader=yaml.UnsafeLoader)  # noqa: S506
