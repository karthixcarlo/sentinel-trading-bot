# Throwaway fixture v2 -- safe to delete

Second attempt at live-verifying a genuine specialist timeout (the first attempt's content tripped several real risk-area path rules -- auth/security/config keywords in filenames -- and scored HIGH purely from area detection, before any specialist finding was even involved).

This version is deliberately boring: generic utility modules, no risk-area keywords anywhere in a path, so the deterministic risk engine should land LOW regardless of what any specialist reports. Volume (20 modules, ~40 lines each, plus tests) is still real, to genuinely stress a specialist's tool-calling budget rather than simulate it.

Safe to close/delete this PR and branch after verification.
