# ADR-001: offline, bounded evidence and standards-based exports

Status: accepted. Date: 2026-10-13. Author/implementation reviewer: Jason Stys. No independent approval or official assessment authority is implied.

## Requirements and decision

Show the documentation/assessment dimension of defensive cybersecurity and DevOps: explicit boundaries, selected controls, verified evidence, honest missing-data states, traceable remediation and repeatable delivery. Keep all examples fictional and all operations local. Preserve previous evidence and verify actual standards, not look-alike JSON.

```text
Trusted lab manifest + ordinary evidence bytes
       → bounded contracts + hashes/freshness/predicates
       → normalized assessment → SQLite snapshots / independent chain tip
                 ├→ inert HTML and canonical reviewer JSON → TypeScript comparison
                 └→ catalog → profile → SSP → assessment plan → results → POA&M
                               ↳ original NIST schemas: Python + native Ajv
```

Python is suited to explicit policy/data validation and standard-library SQLite/HTML. TypeScript provides a separately typed reviewer and native ECMAScript schema-engine check. SQL expresses atomic persistence, referential integrity and indexed filters. Bash coordinates fixed commands without shell evaluation. The `regex` library supplies NIST's Unicode property patterns with an evaluation deadline; original schemas are never rewritten. A narrowly typed adapter covers an untyped vendor factory, not an exemption for domain code.

Compared with a hosted GRC app, the local design avoids accounts, tenancy, secret management and deployment obligations, but has no multi-user security boundary. Compared with home-grown schema substitutes, original OSCAL schemas and independent Ajv validation add meaningful interoperability checks at the cost of vendored schema bytes and version maintenance. A full OSCAL profile resolver/Metaschema engine would support more normative constraints and tailoring; this lab instead rejects unsupported multiple imports/results and implements explicit checks for its simple selected-control chain.

## Scope and lifecycle

One fictional software component and six selected illustrative control predicates. Generated root document UUIDs derive from content/revision metadata; shared entities have stable UUIDs. Documents are deep-copied to prevent cross-model mutation aliasing. `UNKNOWN`/`INTEGRITY_ERROR` observations stay undetermined; no core finding is fabricated for them. No risks supplied produces an explicit informational POA&M scope note, not an invented risk or an assertion of safety.

The ledger's trusted content includes manifest fingerprint, expected/actual artifact hashes, detailed checks, risk projections and assessment clock. Writes occur under `BEGIN IMMEDIATE`, after verifying the current chain, and use bound parameters. Duplicate assessments, different-system writes, rollback chronology/revisions and inconsistent derived rows fail. Application triggers prevent ordinary edits/deletes; the external tip is needed to detect malicious history truncation. This is not signed provenance or WORM storage.

## Bounds, complexity and growth

Files cap at 2 MiB; parse trees cap at depth 32 and 50,000 values. Arrays cap at 1,000 entries; control/evidence/risk scope is further limited by the six known predicates. Evidence reading/hashing is O(B) for bytes read. Indexed dictionary joins avoid repeated scope scans; sorting for stable output/review is O(N log N). Ledger verification is O(H × C) in recorded checks and uses local indexed lookups; H caps at 1,000 snapshots and the database caps at 256 MiB. Warm schema compilation is cached by verified **bytes**, while schema hashes are checked on each validator acquisition.

Revisit authenticated collection, secure private storage, richer control tailoring, complete normative Metaschema constraints, signed/timestamped provenance, append-only remote storage, real assessment authority, concurrency/admission limits and long-lived retention before adapting beyond this synthetic lab. No component pretends to complete Prepare/Categorize/Authorize or choose an official baseline automatically.
