"""Throwaway fixture file — not real code, see ../README.md."""

import os


def dummy_export_report(report_name: str) -> None:
    """`os.system` with string concatenation — command injection shape,
    intentional in this disposable fixture."""
    os.system("mkdir -p /tmp/reports/" + report_name)  # noqa: S605
