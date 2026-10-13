# Security boundary and reporting

Created by Jason Stys. [GitHub](https://github.com/JasonStys) · [Professional contact](https://www.linkedin.com/in/jason-stys-31b30b351/). Do not publish actual vulnerabilities, SSPs, personal/account details, credentials or private evidence in an issue. Author-led review is not an independent security/compliance audit.

## Trust boundaries

Offline **fictional** workspaces only. No host collection, remote-account lookup, automatic risk acceptance, government authorization, shell execution from data, public listener, database server, AI provider or paid infrastructure. Input is data, not instructions. Reports remain local; nothing is automatically uploaded. Docker Desktop and host security settings are unchanged.

The caller supplies the trusted manifest/clock and must determine collection authenticity. Exact-byte SHA-256 detects a file change relative to that manifest; an attacker replacing both can forge a new consistent claim. The unsigned ledger and UUIDv5 IDs do not authenticate a collector or prove observed facts. Internal chain verification cannot detect a rewritten/deleted history without an independently retained trusted tip. Even an external tip is not a signing/timestamping/authorization system.

## Controls and limitations

- Closed bounded JSON and strict types/IDs/UTC dates. Reject duplicate keys, unsafe paths, links/reparse descendants, special files, deep/wide payloads, terminal/bidi controls and unknown fields.
- Verified freshness/scope/digests before satisfaction. Explicit unknown/integrity states and required fresh evidence/milestones before lab risk closure. No fixed “approval score.”
- Untouched official schema digests checked before use; Unicode pattern deadlines and independent Ajv validation. No schema/import URI fetcher or user-selected executable/plugin.
- Escaped inert HTML/CSP, no scripts/assets/external popups or raw-file embedding. Normalized CLI data does not retain arbitrary private fields.
- Parameterized SQL, checked application ID, atomic append, immutable triggers, derived-row verification, exclusive file outputs, readonly history/verification and bounded retention.
- Hash-locked dependency graphs, exact action/tool pins, nonpersistent checkout credentials, least-scoped CodeQL permissions, dependency/history-secret scans and no suppressions/artifact/cache uploads.

Data is plaintext; local administrators or approved device users may access it. Best-effort Unix modes do not guarantee private inherited Windows ACLs. File checks assume no privileged concurrent source-tree mutation; they are not a hardened upload sandbox or authenticated multi-tenant service. Schema/semantic coverage is explicitly limited to the exported simple lab chain, not every OSCAL normative constraint. Source/report publication and ledger append are separate operations; a failed append preserves the report and rolls back only the database transaction. No destructive cleanup runs automatically.
