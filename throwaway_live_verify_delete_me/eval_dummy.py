"""Throwaway fixture file — not real code, see ../README.md."""


def dummy_evaluate_formula(user_formula: str):
    """`eval()` on user-controlled input — intentional in this disposable
    fixture, a classic arbitrary-code-execution shape."""
    return eval(user_formula)  # noqa: S307 - deliberate fixture pattern


def dummy_run_snippet(user_code: str) -> None:
    exec(user_code)  # noqa: S102 - deliberate fixture pattern
