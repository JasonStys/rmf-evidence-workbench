# Contribution and coding conventions

Keep this lab bounded, synthetic and explicit about what it can establish. Use Python for evidence reasoning/storage, TypeScript for typed review, SQL for parameterized persistence and Bash for fixed orchestration. Add a language/dependency only where it has a clear task advantage. No production access or certification claims.

Add negative/regression tests for schema, evidence, chronology, scope, identity or persistence changes. Preserve unknown/integrity distinctions and no-authorization state. Never weaken a gate to obtain green CI. Performance measurements need environment/scope and correctness evidence; they are not production capacity or an asymptotic proof.

Formatting order: `python -m ruff check --fix .`, `python -m ruff format .`, `python scripts/code_map.py`, `npm run maps`, stage intended files, `python scripts/file_guide.py`, then execute check modes and full validation. Function/class contracts explain inputs/outputs and safety rationale; exact header maps complement self-documenting names. Natural-format JSON/vendor locks do not receive invalid comment headers; their purposes appear in the exhaustive README guide.

Review exact versions, release digests, notices and advisory graphs on dependency/schema updates. Preserve the original NIST notice and unmodified schemas. Keep raw private evidence, databases, binaries, credentials, caches and generated builds out of Git. Publish only deliberately selected fictional examples and measured aggregate reports with reproduction instructions and verified source/run links.
