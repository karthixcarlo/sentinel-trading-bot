# Throwaway fixture — safe to delete

This entire directory exists only to force a real AIDA-MATE review to
process a diff heavy enough to genuinely stress a specialist agent's
per-call timeout (live verification of `needs_human_review` + gated
auto-merge). Every file below is synthetic, disposable, and contains no
real credentials, company data, or production logic — just plausible
security-relevant *patterns* (fake secrets, unsafe deserialization,
injection-shaped string building, etc.) spread across many small files
so a specialist has real, distinct things to look at in each one.

This PR and its branch are meant to be closed/deleted after the live
verification is done.
