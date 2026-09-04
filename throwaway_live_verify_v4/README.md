# Throwaway fixture v4 -- safe to delete

Fourth attempt at live-verifying a genuine specialist timeout. v2 and v3 were both large but *independent* boilerplate, and every specialist finished inside the 10s floor both times -- real evidence that file/line count alone does not reliably force extra tool-calling turns.

v4 instead chains 60 small modules together by real function calls (chain_000 calls into chain_001, which calls chain_002, ...), so actually understanding what `run_full_chain()` computes requires opening many files in sequence -- a real reason for a thorough specialist to make many tool calls, not just more bytes to skim once. Still verified LOW risk the same way (no risk-area path keywords anywhere).

Safe to close/delete this PR and branch after verification.
