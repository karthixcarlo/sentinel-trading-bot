"""Throwaway fixture file — not real code, see ../README.md."""

import subprocess


def dummy_ping_host(hostname: str) -> str:
    """`shell=True` plus unsanitized interpolation — command injection
    shape, intentional in this disposable fixture."""
    result = subprocess.run(f"ping -n 1 {hostname}", shell=True, capture_output=True)
    return result.stdout.decode(errors="replace")


def dummy_convert_file(user_supplied_path: str) -> None:
    subprocess.call("convert " + user_supplied_path + " out.png", shell=True)
