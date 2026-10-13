# Primary sources and design rationale

Reviewed 2026-10-13. Third-party technical references provide information, not authorization to access actual systems or accept risk.

- [NIST RMF overview](https://csrc.nist.gov/projects/risk-management/about-rmf) informed the distinction between selection/implementation/assessment/monitoring and actual authorization authority. This project helps organize educational evidence; it does not implement the full RMF or grant an ATO.
- [NIST OSCAL assessment layer](https://pages.nist.gov/OSCAL/learn/concepts/layer/assessment/) informed the assessment-plan/results/POA&M relationship and risk transfer.
- [NIST OSCAL SSP](https://pages.nist.gov/OSCAL/learn/concepts/layer/implementation/ssp/) informed system boundaries, selected controls, component/statement identity and document revision UUIDs.
- [Official OSCAL 1.2.3 release](https://github.com/usnistgov/OSCAL/releases/tag/v1.2.3) supplies the exact unchanged schema bytes and release asset digests in `oscal.lock.json`; [upstream notice](https://github.com/usnistgov/OSCAL/blob/v1.2.3/LICENSE.md) is preserved intact locally.
- [JSON Schema string/pattern reference](https://json-schema.org/understanding-json-schema/reference/string) informed pattern/format validation. Original NIST patterns use Unicode property escapes; Python validation uses bounded Unicode-capable regex support and native Ajv checks independent ECMAScript behavior.
- [python-jsonschema validators](https://python-jsonschema.readthedocs.io/en/stable/creating/) documents the public extension API used only for Unicode pattern compatibility.
- [Ajv JSON Schema validation](https://ajv.js.org/json-schema.html) informs the independent, strictly configured native engine; no asynchronous/remote schema loader is installed.
- [referencing registry behavior](https://referencing.readthedocs.io/en/stable/api/#referencing.Registry) informed the explicit no-network default registry.
- [SQLite transaction documentation](https://www.sqlite.org/lang_transaction.html) informed write locking/atomic append; [indexes](https://www.sqlite.org/lang_createindex.html) informed state/sequence filters.
- [UUID library](https://github.com/uuidjs/uuid) supplies standards-based non-security UUIDv5 identity parity with Python's standard library. Integrity gates use SHA-256; neither IDs nor unsigned hashes are signatures.

Use clear names, explicit units, cohesive contracts, exact symbol maps, strict input types, closed data models and meaningful negative tests. Hash/version pins support reproducibility, not indefinite vendor security or official endorsement. Advisory sources change; rescan dependencies before adaptation. Selected control predicates are authored examples, not copied normative control assessments.
