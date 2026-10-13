# Measured validation and author review

Author: Jason Stys. Date: 2026-10-13. The executable-source commit [2c92133653b4ac8775931a5ea6b7e77e35a6d496](https://github.com/JasonStys/rmf-evidence-workbench/commit/2c92133653b4ac8775931a5ea6b7e77e35a6d496) passed all eight actual CI jobs. Publication acceptance also requires every check on the documentation-only follow-up commit to pass; the README badges and Actions page show current main, while [ci.json](ci.json) records this immutable source snapshot.

The local Windows suite currently passes 108 Python tests and three TypeScript tests, with 96.70% branch-inclusive coverage. Strict mypy/Ruff/TypeScript and complete dependency audits pass. Actual synthetic end-to-end execution validates twelve exported OSCAL documents in both Python and Ajv, stores/verifies two SQLite snapshots and reviews three control plus three risk transitions. Baseline: three satisfied, two unsatisfied, one unknown. Remediation: six satisfied predicates and three bounded lab risk closures. Neither scenario authorizes a system.

## Actual GitHub Actions evidence

[Validate run 38482960574](https://github.com/JasonStys/rmf-evidence-workbench/actions/runs/38482960574) completed successfully at 2026-10-13T23:15:43Z. Each lane ran the complete checks, including the real schema engines and SQLite integration; none skipped tests or lowered the 90% coverage gate.

| Lane | Python tests | TypeScript tests | Statement/branch coverage |
| --- | --- | --- | --- |
| Ubuntu 24.04 / Python 3.12 | 108 passed | 3 passed | 96.70% |
| Ubuntu 24.04 / Python 3.14 | 108 passed | 3 passed | 96.70% |
| Windows / Python 3.14 | 108 passed | 3 passed | 96.70% |
| macOS Intel / Python 3.14 | 108 passed | 3 passed | 96.70% |

The separate OSCAL job reproduced the twelve-document/two-snapshot demonstration, including an external-tip match and three control/three risk transitions. The security job passed complete runtime and development Python advisory audits, the complete npm audit, Gitleaks history scan, hash-verified native tools, actionlint and ShellCheck. Trivy detected the npm lockfile and reported zero vulnerabilities; Python lock graphs are covered separately by pip-audit, not claimed as Trivy coverage.

[CodeQL run 38482960498](https://github.com/JasonStys/rmf-evidence-workbench/actions/runs/38482960498) completed both security-extended language jobs successfully. The open-alert API returned zero findings at 2026-10-13T23:16:27Z. These are point-in-time checks, not proof that all defects or future vulnerabilities are impossible.

This repository had zero Actions artifacts and zero Actions caches after the source runs. No artifact-upload/cache-creation steps are configured; test and security results remain in job logs/summaries, with selected synthetic measurements versioned under this folder. Account-wide billing data is not published here.

## Local measurements and browser check

[benchmark.json](benchmark.json) records five warmed batches of ten snapshots, with six controls and six genuinely schema-validated OSCAL models per snapshot. Median: 43.760 ms/snapshot; peak Python allocation: 2,349,624 bytes on Windows/Python 3.14.6. This includes local evidence reads, excludes Node startup/SQLite/production collection and is informational, not a capacity SLA or cross-machine regression threshold.

The generated baseline HTML was opened in a real browser: the selected system/revision/clock, six evidence rows, three fictional remediation records, author/contact/help text and `NOT_GRANTED` disclaimer were visibly correct. The stale audit-review row remained `UNKNOWN`; normalized data preserved the manifest and expected/actual evidence hashes. This was a static report check, not a hosted application or an accessibility certification. The temporary loopback-only preview server was used only for inspection.

## Review and development findings

Security review: source/clock/manifest trust assumptions, no URI/executable fetch, terminal/path/JSON bounds, closed fields, escaped inert HTML, raw-evidence exclusion, bound SQL, trigger/tip limits, schema/tool/action integrity and workflow permission/storage behavior. Correctness review: no fabricated findings for unknown states, linked statement/entity identity, coherent milestone closure, cross-model isolation, preserved actual/expected artifact hashes, exact summaries and chronological/atomic history. Performance review: dictionary joins, bounded work, schema-cache keys by verified bytes, stable sorting and actual warmed validation benchmark.

Actual prototype findings were corrected and regression-tested: official NIST Unicode patterns need compatible Python validation; native Ajv validates those same bytes independently. Shared AR/POA&M data needed deep copies so modifying one model cannot alter the other invisibly. Giant adversarial test inputs need bounded test IDs for portable logging. The initial Codex Windows sandbox denied pytest-owned temp creation; authorized normal test execution did not weaken application controls. No schema rewrites, vulnerability suppressions, assertion removals, local Docker repair or official authorization occurred.

All claims are scoped: selected fictional predicates, supported simple OSCAL chain, unsigned local plaintext history and informational timings. No independent reviewer, full government baseline assessment, certification, production use, host/account collection, or paid infrastructure deployment is claimed. Authored files pass whitespace checks; pinned NIST schema/notice bytes retain upstream formatting, including original trailing whitespace, to preserve source integrity and attribution.
