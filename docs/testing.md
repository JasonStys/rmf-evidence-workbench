# Risk-based testing strategy

Primary risks: fake satisfaction from absent/stale facts, semantic reference errors despite valid JSON, unsupported status/identity claims, hash/chain drift, untrusted input leakage and nonportable validation.

| Risk boundary | Actual validation |
| --- | --- |
| Workspace/facts | Closed schemas, duplicate IDs/keys, strict integers/booleans, malformed UTF-8/JSON, time windows, byte/array/tree/path bounds |
| Assessment | Exact predicates, positive sample denominators, stale/future/missing/tampered/out-of-scope evidence, freshness/deadline equality, coherent resolution |
| Properties | 150 randomized account-count batches with an independent equality oracle |
| OSCAL | Original six versioned hash-pinned schemas, real Unicode patterns/format checks, native independent Ajv against twelve exports, native negative fixture |
| Semantics | Scope/imports, duplicate UUIDs, component/AP subjects, actors, control/evidence/finding status matching, target statements, risk/finding/observation references, cross-document mutation |
| Persistence | Real SQL inserts/filters, append-only triggers, rollback/duplicate/system/chronology rejection, derived-row checks, saved-tip mismatch and local-admin truncation demonstration |
| Reviewer | Strict typed parsing, canonical encoding/duplicate rejection, invalid calendars/IDs/counts/private extra fields, terminal controls, Unicode parity and same-system diff |
| Reports/CLI | Real commands, exclusive output, escaped malicious markup, restrictive CSP and no assets/scripts/raw attachments |
| End-to-end | Actual Python assessments, both schema engines, real SQLite history and compiled Node reviewer on owned synthetic workspaces |
| Delivery | Four OS/Python lanes, strict mypy/Ruff/TypeScript, ≥90% branch-inclusive coverage, exact code/file guides and dependency/secret/static scans |

Warnings are errors; no skipped/suppressed security assertions are required for these core tests. Link/reparse rejection uses synthetic metadata to be portable without admin/developer-mode requirements; actual bounded ordinary files are exercised. No claim is made that path checks withstand a privileged concurrent filesystem attacker. The initial Windows Codex sandbox blocked pytest-owned temp creation; normal authorized test execution used ordinary test temporary-directory access, with no change to application guards.

Performance is measured after schema warmup using five batches of ten assessments plus actual six-model validation. Correctness is asserted; wall time is informational to avoid hardware-dependent false failures. It excludes Node startup, ledger IO and production collection. Bounds/algorithm analysis complement timings rather than deriving Big-O from benchmark output.

Gaps: every NIST control/enhancement, full OSCAL profile resolution/Metaschema normative constraints, XML/YAML interchange, production evidence authenticity, real government baseline categorization/authorization, multi-user access/storage, WORM/signed timestamps, massive/long-duration workloads and independent penetration/compliance review. This lab documents scope rather than making these claims.
