# Evidence and assessment contracts

## Supported predicates, not full control assessments

| Mapping | Illustrative selected predicate |
| --- | --- |
| AC-2 | Positive sampled active-account count equals reviewed-account count |
| AC-3 | Explicit boolean outcomes deny both unauthorized and cross-tenant access |
| AU-2 | Positive sampled source-event count equals retained-event count |
| AU-6 | Explicit boolean confirms the selected audit review was performed |
| CM-6 | Reported configuration drift count equals zero |
| CP-9 | Restore verified, RPO ≤300 seconds, RTO ≤900 seconds |

These authored educational checks do not reproduce the complete NIST control text or establish actual implementation. Counts/booleans are supplied synthetic facts, not measurements collected by this tool. Zero sample denominators are invalid/unknown, not proof of completeness. A human assessor must decide relevance, sufficient evidence and any real authorization/risk acceptance separately.

## Closed workspace

`bundle.json` has exactly schema/system/revision/controls/evidence/risks. The system defines a UUID, printable name/boundary and one component UUID. Controls select known IDs, title, requirement and 1–168 hour freshness limit. Each selected control has at most one evidence record. Evidence records identify their own UUID, control/component, fixed `evidence/<safe-name>.json` path, exact-byte SHA-256 and claimed UTC timestamp.

Fact files have exactly schema/control_id/component_id/observed_at/check/facts. Field types, known check name, manifest/source timestamps and component/control scope must agree. Strict integers exclude bool/coercible strings/floats. Duplicate JSON keys/record IDs, unknown fields, linked/reparse descendants, unsafe paths, special files, overlarge arrays/files/trees and terminal/bidi controls are rejected. JSON is parsed as data; it is never code, SQL, an import to execute or a URL to fetch. Local source files must not be mutated concurrently; portable path checks are not a protection against a privileged filesystem adversary.

Canonical UTC seconds (`YYYY-MM-DDTHH:MM:SSZ`) govern freshness and deadlines. Age equality at the maximum is fresh; one second beyond is stale. Future/stale evidence, missing records/files and malformed facts are `UNKNOWN`. Exact-byte or provenance/scope mismatches are `INTEGRITY_ERROR`. Only verified, fresh facts can become `SATISFIED`/`NOT_SATISFIED`. Reports record both expected and actual byte fingerprints and the source manifest fingerprint; they do not hide failures by filtering the denominator.

## Risks and milestones

Risks have explicit IDs, selected control, fictional owner, description, low/moderate/high severity, open/in-progress/resolved status, opening/deadline/completion times and bounded unique milestone IDs. Milestone deadlines stay within risk opening/deadline bounds. Completion cannot precede opening, exceed the assessment clock or precede its required milestone completions. Resolved status requires a completion timestamp, completed milestones and fresh satisfied evidence observed no later than completion. Risk severity is a supplied qualitative label, not an objective risk score; late closure does not retroactively meet the due date. Missing risk records are never interpreted as absence of real risk.

## Normalized history/review

Schema 1 reports include fixed scope/revision/clock, `synthetic: true`, `authorization: NOT_GRANTED`, content-derived UUID, manifest fingerprint, detailed checks and matching state counts, and risk projections. Python-compatible sorted ASCII canonical JSON is required by the Node reader: this also rejects duplicate/shadow keys and encoding ambiguities. UTF-8 is strict. TypeScript independently verifies report shape, count/reference consistency, content UUID and same-system comparisons; its status-transition diff does not claim to authenticate facts. Full fingerprints remain in the original reports.

Ledger hashes use SHA-256 over sequence, previous hash and canonical payload. UUIDv5 is a standards-based **non-security identifier** via Python/official UUID library, not a signature. Trusted-manifest integrity, an unsigned local chain and a content UUID do not prove collector identity, observation truth or security authorization. Keep a trusted expected chain tip outside the ledger to detect truncation/rewrite. The app never changes an authorization state.
