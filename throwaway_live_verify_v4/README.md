# chain fixture

A set of 60 small Python modules. Each module defines one function that appends its own index to a list and calls the same-named function in the next module, forming one chain from `chain_000` through `chain_059`. The final module returns the accumulated list without calling further.

`tests/test_chain.py` calls `chain_000.step_000([])` and checks the result equals `list(range(60))`.
