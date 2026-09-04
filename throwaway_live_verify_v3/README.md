# Throwaway fixture v3 -- safe to delete

Third attempt at live-verifying a genuine specialist timeout. v1 tripped real risk-area path rules (auth/security/config keywords in filenames) and scored HIGH from area detection alone. v2 fixed that (verified LOW via a real dry run of area_detector.py + risk_engine.py) but its 43-file/1628-line diff let every specialist finish inside the 10s floor -- no timeout. v3 keeps v2's safe naming but roughly doubles the file count (78 modules) and widens each module (5 functions + a class instead of 3), to push real tool-calling volume further while staying LOW risk by the same construction.

Safe to close/delete this PR and branch after verification.
