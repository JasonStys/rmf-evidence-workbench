# Measured validation and author review

Author: Jason Stys. Date: 2026-10-13. Publication acceptance requires every check on final main to pass; verified source/run links will be completed after actual CI, not inferred from local tests.

The local Windows suite currently passes 108 Python tests and three TypeScript tests, with 96.70% branch-inclusive coverage. Strict mypy/Ruff/TypeScript and complete dependency audits pass. Actual synthetic end-to-end execution validates twelve exported OSCAL documents in both Python and Ajv, stores/verifies two SQLite snapshots and reviews three control plus three risk transitions. Baseline: three satisfied, two unsatisfied, one unknown. Remediation: six satisfied predicates and three bounded lab risk closures. Neither scenario authorizes a system.

## Review and development findings

Security review: source/clock/manifest trust assumptions, no URI/executable fetch, terminal/path/JSON bounds, closed fields, escaped inert HTML, raw-evidence exclusion, bound SQL, trigger/tip limits, schema/tool/action integrity and workflow permission/storage behavior. Correctness review: no fabricated findings for unknown states, linked statement/entity identity, coherent milestone closure, cross-model isolation, preserved actual/expected artifact hashes, exact summaries and chronological/atomic history. Performance review: dictionary joins, bounded work, schema-cache keys by verified bytes, stable sorting and actual warmed validation benchmark.

Actual prototype findings were corrected and regression-tested: official NIST Unicode patterns need compatible Python validation; native Ajv validates those same bytes independently. Shared AR/POA&M data needed deep copies so modifying one model cannot alter the other invisibly. Giant adversarial test inputs need bounded test IDs for portable logging. The initial Codex Windows sandbox denied pytest-owned temp creation; authorized normal test execution did not weaken application controls. No schema rewrites, vulnerability suppressions, assertion removals, local Docker repair or official authorization occurred.

All claims are scoped: selected fictional predicates, supported simple OSCAL chain, unsigned local plaintext history and informational timings. No independent reviewer, full government baseline assessment, certification, production use, host/account collection, or paid infrastructure deployment is claimed. Generated source-level and CI reports will record actual final measurements.
