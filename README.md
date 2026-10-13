# RMF Evidence Workbench

[![Validate](https://github.com/JasonStys/rmf-evidence-workbench/actions/workflows/ci.yml/badge.svg)](https://github.com/JasonStys/rmf-evidence-workbench/actions/workflows/ci.yml)
[![CodeQL](https://github.com/JasonStys/rmf-evidence-workbench/actions/workflows/codeql.yml/badge.svg)](https://github.com/JasonStys/rmf-evidence-workbench/actions/workflows/codeql.yml)

An offline, runnable evidence-and-remediation workbench for a **fictional** information system. It connects selected control predicates, exact artifact hashes, assessment observations, risk milestones, reviewer reports, and a verifiable history to six actual OSCAL JSON models.

Created by **[Jason Stys](https://github.com/JasonStys)** · [Professional contact](https://www.linkedin.com/in/jason-stys-31b30b351/).

This is an educational portfolio lab, **not** a compliance certification, full NIST baseline, government authorization, FedRAMP submission tool, production GRC platform, or risk-acceptance decision. Every report says `authorization: NOT_GRANTED`. It never collects host/account data, changes system security, contacts a production service or fetches a document import URI.

## Features

- **Evidence-aware assessment:** six explicit illustrative predicates mapped to AC-2, AC-3, AU-2, AU-6, CM-6 and CP-9. Digest/scope mismatches are `INTEGRITY_ERROR`; absent, stale, future-dated or malformed evidence is `UNKNOWN`, never a pass.
- **Real OSCAL exports:** catalog, profile, system security plan, assessment plan, assessment results and POA&M. All six unmodified official NIST 1.2.3 schemas are hash-pinned and vendored. Python Unicode-aware validation and independent native ECMAScript Ajv validation run against actual exports.
- **Semantic consistency:** validate the supported local import chain, unique UUID declarations, selected control scope, components/subjects, reviewer actors, observation/finding determinations, and risk/remediation references. Undetermined observations do not invent core satisfied/not-satisfied findings.
- **Remediation:** explicit fictional owners, severity, deadlines and milestones. Resolved lab risks require fresh satisfied predicates and completed milestones with coherent chronology. This cannot grant authorization or accept actual risk.
- **History and review:** parameterized SQLite with append-only triggers, atomic writes, recorded manifest/actual evidence fingerprints, chain verification, chronological state filters and an independently retained tip for truncation detection. TypeScript validates normalized reports and compares control/risk transitions for the same system.
- **Readable evidence:** escaped network-inert HTML, canonical normalized JSON, reproducible before/after examples, measured benchmarks and detailed operating/security/test documentation.
- **Delivery:** strict types/lint, negative/property tests, four OS/Python test lanes, two schema engines, dependency/history-secret checks, actionlint/ShellCheck and both CodeQL languages. No Actions artifact/cache uploads.

## Quick start

Requires Python 3.12+ and Node.js 24. From the repository root on Windows:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install --require-hashes -r requirements-dev.lock
npm.cmd ci --ignore-scripts
npm.cmd run build
.venv/Scripts/python scripts/demo.py --output out/my-first-demo
```

On Linux/macOS, use `.venv/bin/python` and `npm` instead. The demo runs both schema engines, writes two real SQLite snapshots and invokes the compiled TypeScript reviewer. No Docker, paid host, credentials or cloud account is required. Output directories must be **new**; reusing one fails instead of replacing prior evidence.

Open `out/my-first-demo/baseline/assessment.html` in a browser. The baseline deliberately shows three satisfied checks, two unsatisfied checks, and one stale/unknown check. The later synthetic revision shows six satisfied checks and three resolved **lab** risk records; it still does not authorize the system. Example timestamps are fixed fictional dates for reproducibility, not live observations of this PC.

## Commands

```powershell
.venv/Scripts/python -m rmf init-ledger out/evidence.db
.venv/Scripts/python -m rmf assess examples/baseline --as-of 2026-10-12T12:00:00Z --output out/baseline --ledger out/evidence.db
.venv/Scripts/python -m rmf assess examples/remediated --as-of 2026-10-13T12:00:00Z --output out/remediated --ledger out/evidence.db
.venv/Scripts/python -m rmf validate-oscal out/baseline
node scripts/oscal_check.mjs out/baseline
node dist/review.js out/baseline/assessment.json out/remediated/assessment.json
.venv/Scripts/python -m rmf history out/evidence.db --state NOT_SATISFIED
.venv/Scripts/python -m rmf verify-ledger out/evidence.db --expected-tip YOUR_INDEPENDENTLY_SAVED_SHA256_TIP
```

Save each append receipt's tip separately from the database. Without that independent value, verification checks only internal consistency; a local administrator can rewrite/truncate an unsigned ledger. A matching manifest hash is not proof of a collector's identity or the truth of its observations. Evidence file paths are constrained and hashed; raw files remain in the input workspace and are **not** automatically embedded in reports or uploaded anywhere.

## Validation and documentation

```powershell
npm.cmd test
.venv/Scripts/python -m pytest --cov --cov-report=term-missing --tb=short
.venv/Scripts/python -m mypy
.venv/Scripts/python -m ruff check .
.venv/Scripts/python -m ruff format --check .
.venv/Scripts/python scripts/vendor_oscal.py --check
.venv/Scripts/python scripts/examples.py --check
.venv/Scripts/python scripts/code_map.py --check
npm.cmd run maps:check
.venv/Scripts/python scripts/file_guide.py --check
.venv/Scripts/python scripts/validate_repo.py
.venv/Scripts/python scripts/benchmark.py
```

[Runbook](docs/runbook.md) · [contracts/predicates](docs/contracts.md) · [architecture/ADR](docs/architecture.md) · [testing strategy](docs/testing.md) · [measured validation](docs/reports/validation.md) · [security](SECURITY.md) · [primary research](docs/research.md).

Python handles evidence policy, schema orchestration, reports and persistence. TypeScript handles typed offline review. SQL provides indexed transactional evidence storage; Bash orchestrates portable validation. Authored code has descriptive contracts and exact generated header maps for definitions, parameters and assigned variables. JSON/lock/vendor files retain their natural format and are individually described below. See [contribution rules](CONTRIBUTING.md).

## Every tracked file

<!-- BEGIN FILE GUIDE -->

| File | Purpose |
| --- | --- |
| [.gitattributes](.gitattributes) | Portable LF text handling. |
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | Jason Stys: actual offline OSCAL/evidence validation on four OS/Python lanes plus security gates. |
| [.github/workflows/codeql.yml](.github/workflows/codeql.yml) | Jason Stys: security-extended static analysis; database uploads disabled, findings are not Actions artifacts. |
| [.gitignore](.gitignore) | Keeps private local evidence, databases, tools and generated build/cache output out of Git. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution and coding conventions. |
| [LICENSE](LICENSE) | MIT terms for authored code, not the unmodified NIST schemas. |
| [README.md](README.md) | RMF Evidence Workbench. |
| [SECURITY.md](SECURITY.md) | Security boundary and reporting. |
| [docs/architecture.md](docs/architecture.md) | ADR-001: offline, bounded evidence and standards-based exports. |
| [docs/contracts.md](docs/contracts.md) | Evidence and assessment contracts. |
| [docs/reports/baseline.html](docs/reports/baseline.html) | Escaped network-inert rendered synthetic assessment. |
| [docs/reports/baseline.json](docs/reports/baseline.json) | Canonical measured baseline with unknown/failing states and exact evidence fingerprints. |
| [docs/reports/benchmark.json](docs/reports/benchmark.json) | Actual warmed assessment/schema timing and allocation measurements. |
| [docs/reports/demo.json](docs/reports/demo.json) | Actual cross-language synthetic assessment, schema and ledger validation results. |
| [docs/reports/remediated.json](docs/reports/remediated.json) | Canonical measured remediation with fresh predicates and bounded risk closure. |
| [docs/reports/validation.md](docs/reports/validation.md) | Measured validation and author review. |
| [docs/research.md](docs/research.md) | Primary sources and design rationale. |
| [docs/runbook.md](docs/runbook.md) | Local reviewer and evidence operating runbook. |
| [docs/testing.md](docs/testing.md) | Risk-based testing strategy. |
| [examples/baseline/bundle.json](examples/baseline/bundle.json) | Fictional bundle evidence/manifest; no real identities, credentials, account data or host collection. |
| [examples/baseline/evidence/ac-2.json](examples/baseline/evidence/ac-2.json) | Fictional ac-2 evidence/manifest; no real identities, credentials, account data or host collection. |
| [examples/baseline/evidence/ac-3.json](examples/baseline/evidence/ac-3.json) | Fictional ac-3 evidence/manifest; no real identities, credentials, account data or host collection. |
| [examples/baseline/evidence/au-2.json](examples/baseline/evidence/au-2.json) | Fictional au-2 evidence/manifest; no real identities, credentials, account data or host collection. |
| [examples/baseline/evidence/au-6.json](examples/baseline/evidence/au-6.json) | Fictional au-6 evidence/manifest; no real identities, credentials, account data or host collection. |
| [examples/baseline/evidence/cm-6.json](examples/baseline/evidence/cm-6.json) | Fictional cm-6 evidence/manifest; no real identities, credentials, account data or host collection. |
| [examples/baseline/evidence/cp-9.json](examples/baseline/evidence/cp-9.json) | Fictional cp-9 evidence/manifest; no real identities, credentials, account data or host collection. |
| [examples/remediated/bundle.json](examples/remediated/bundle.json) | Fictional bundle evidence/manifest; no real identities, credentials, account data or host collection. |
| [examples/remediated/evidence/ac-2.json](examples/remediated/evidence/ac-2.json) | Fictional ac-2 evidence/manifest; no real identities, credentials, account data or host collection. |
| [examples/remediated/evidence/ac-3.json](examples/remediated/evidence/ac-3.json) | Fictional ac-3 evidence/manifest; no real identities, credentials, account data or host collection. |
| [examples/remediated/evidence/au-2.json](examples/remediated/evidence/au-2.json) | Fictional au-2 evidence/manifest; no real identities, credentials, account data or host collection. |
| [examples/remediated/evidence/au-6.json](examples/remediated/evidence/au-6.json) | Fictional au-6 evidence/manifest; no real identities, credentials, account data or host collection. |
| [examples/remediated/evidence/cm-6.json](examples/remediated/evidence/cm-6.json) | Fictional cm-6 evidence/manifest; no real identities, credentials, account data or host collection. |
| [examples/remediated/evidence/cp-9.json](examples/remediated/evidence/cp-9.json) | Fictional cp-9 evidence/manifest; no real identities, credentials, account data or host collection. |
| [ops/schema.sql](ops/schema.sql) | Owned append-only synthetic assessment ledger and indexed derived findings. Created by Jason Stys. |
| [oscal.lock.json](oscal.lock.json) | Official NIST OSCAL version and six untouched release-schema checksums. |
| [package-lock.json](package-lock.json) | Complete npm dependency graph with registry integrity hashes. |
| [package.json](package.json) | Pinned native schema/review dependencies and Node scripts. |
| [pyproject.toml](pyproject.toml) | Strict Python lint/type/tests and branch-inclusive coverage configuration. |
| [requirements-dev.in](requirements-dev.in) | Exact direct validation dependencies plus the runtime graph. |
| [requirements-dev.lock](requirements-dev.lock) | Complete hash-pinned portable validation graph. |
| [requirements.in](requirements.in) | Exact reviewed runtime dependencies with real JSON format and Unicode support. |
| [requirements.lock](requirements.lock) | Complete hash-pinned portable runtime graph. |
| [review/review.test.ts](review/review.test.ts) | Typed review parser, privacy boundaries and snapshot-diff regression tests. Created by Jason Stys. |
| [review/review.ts](review/review.ts) | Typed offline snapshot comparison; data is parsed, never executed or sent remotely. Created by Jason Stys. |
| [rmf/\_\_init\_\_.py](rmf/__init__.py) | Educational offline RMF evidence tools by Jason Stys; https://github.com/JasonStys. |
| [rmf/\_\_main\_\_.py](rmf/__main__.py) | Offline assessment, OSCAL validation and evidence-ledger CLI. Created by Jason Stys. |
| [rmf/assessment.py](rmf/assessment.py) | Assess selected lab checks with evidence integrity, freshness and gated remediation. Created by Jason Stys. |
| [rmf/contracts.py](rmf/contracts.py) | Closed bounded evidence contracts and safe local reads. Created by Jason Stys. |
| [rmf/ledger.py](rmf/ledger.py) | Transactional parameterized SQLite snapshots with integrity chains and explicit trust limits. Jason Stys. |
| [rmf/oscal.py](rmf/oscal.py) | Build six real OSCAL models and verify pinned schemas plus scoped cross-document references. Jason Stys. |
| [rmf/report.py](rmf/report.py) | Render escaped inert reviewer evidence and six validated OSCAL exports. Created by Jason Stys. |
| [schemas/NIST-NOTICE.md](schemas/NIST-NOTICE.md) | Intact original NIST public-domain/CC0 notice for the unmodified schemas. |
| [schemas/NOTICE.md](schemas/NOTICE.md) | Original NIST OSCAL schemas. |
| [schemas/oscal\_assessment-plan\_schema.json](schemas/oscal_assessment-plan_schema.json) | Unmodified NIST OSCAL 1.2.3 assessment-plan JSON schema; pinned and checked in both Unicode-capable engines. |
| [schemas/oscal\_assessment-results\_schema.json](schemas/oscal_assessment-results_schema.json) | Unmodified NIST OSCAL 1.2.3 assessment-results JSON schema; pinned and checked in both Unicode-capable engines. |
| [schemas/oscal\_catalog\_schema.json](schemas/oscal_catalog_schema.json) | Unmodified NIST OSCAL 1.2.3 catalog JSON schema; pinned and checked in both Unicode-capable engines. |
| [schemas/oscal\_poam\_schema.json](schemas/oscal_poam_schema.json) | Unmodified NIST OSCAL 1.2.3 poam JSON schema; pinned and checked in both Unicode-capable engines. |
| [schemas/oscal\_profile\_schema.json](schemas/oscal_profile_schema.json) | Unmodified NIST OSCAL 1.2.3 profile JSON schema; pinned and checked in both Unicode-capable engines. |
| [schemas/oscal\_ssp\_schema.json](schemas/oscal_ssp_schema.json) | Unmodified NIST OSCAL 1.2.3 ssp JSON schema; pinned and checked in both Unicode-capable engines. |
| [scripts/benchmark.py](scripts/benchmark.py) | Measure actual assessment plus warmed OSCAL validation, not production certification. Created by Jason Stys. |
| [scripts/code\_map.py](scripts/code_map.py) | Generate/check exact Python, SQL, shell and YAML symbol positions. Created by Jason Stys. |
| [scripts/demo.py](scripts/demo.py) | Execute two real assessments, twelve OSCAL validations, ledger verification and typed review. Jason Stys. |
| [scripts/examples.py](scripts/examples.py) | Create/check reproducible fictional baseline and remediated evidence workspaces. Created by Jason Stys. |
| [scripts/file\_guide.py](scripts/file_guide.py) | Maintain exhaustive tracked-file README summaries without reading ignored drill outputs. Jason Stys. |
| [scripts/oscal\_check.mjs](scripts/oscal_check.mjs) | Independent native ECMAScript Unicode-schema validation using pinned Ajv. Created by Jason Stys. |
| [scripts/scanners.py](scripts/scanners.py) | Install only hash-pinned official Linux scanner binaries. Created by Jason Stys. |
| [scripts/ts\_map.mjs](scripts/ts_map.mjs) | Generate/check exact TypeScript and JavaScript AST symbol headers. Created by Jason Stys. |
| [scripts/validate.sh](scripts/validate.sh) | Cross-platform strict checks, actual schema engines and local evidence verification. Created by Jason Stys. |
| [scripts/validate\_repo.py](scripts/validate_repo.py) | Validate immutable schema/example pins and storage-free least-privilege CI contracts. Created by Jason Stys. |
| [scripts/vendor\_oscal.py](scripts/vendor_oscal.py) | Fetch only six official hash-pinned NIST OSCAL schemas for offline validation. Created by Jason Stys. |
| [tests/\_\_init\_\_.py](tests/__init__.py) | Reproducible synthetic workbench regression tests. Created by Jason Stys. |
| [tests/conftest.py](tests/conftest.py) | Owned synthetic workspace fixtures with precise digest maintenance. Created by Jason Stys. |
| [tests/test\_assessment.py](tests/test_assessment.py) | Evidence-state, schema, chronology, scope and remediation-gate tests. Created by Jason Stys. |
| [tests/test\_cli\_report.py](tests/test_cli_report.py) | CLI, escaped reporting and real cross-language native schema/review workflow tests. Created by Jason Stys. |
| [tests/test\_contracts.py](tests/test_contracts.py) | Bounded parser/file/identifier and terminal privacy boundary tests. Created by Jason Stys. |
| [tests/test\_ledger.py](tests/test_ledger.py) | Real SQLite atomicity, query binding, immutable triggers and externally anchored chain tests. Jason Stys. |
| [tests/test\_oscal.py](tests/test_oscal.py) | Real schema, Unicode, semantic-reference and no-authorization regression tests. Created by Jason Stys. |
| [tests/test\_semantics.py](tests/test_semantics.py) | Supported OSCAL scope, reviewer identity and evidence/determination consistency tests. Created by Jason Stys. |
| [tools.lock.json](tools.lock.json) | Official scanner release URLs and archive SHA-256 digests. |
| [tsconfig.json](tsconfig.json) | Strict Node TypeScript compiler settings. |

<!-- END FILE GUIDE -->
