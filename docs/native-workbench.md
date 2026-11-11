# Native offline workbench

Created by Jason Stys · [Source and contact](https://github.com/JasonStys).

## Start and select your inputs

The Windows portable application bundles Python 3.14.10, Tcl/Tk 9.0.4, the graphical interface and the actual project engines. Launch the single EXE; no Python/Node setup, terminal command, account or baked password is needed. This is a portable application, not an NSIS installer, signed executable or cross-platform binary. Packaging and source checks do not establish an independent security certification.

Choose an operation in **Inputs and analysis**, browse authorized local files/folders, set the explicit UTC clock and relevant parameters, acknowledge permission, then **Run analysis**. Only fields relevant to that operation are shown. Prepared fictional scenarios fill these same ordinary controls; they do not run automatically or replace the application with a separate demo. Changing a field resets permission acknowledgement. Your own supported inputs and policies can replace the prepared paths.

## Review, filter, export and return

The **Findings and timeline** tab preserves the original project findings. Choose a view, search literal record values and select a row to read its full structured evidence. The table shows at most 5000 rows; exact full retained files remain exportable. A finding or unknown state is a successful analysis result requiring human review, not a clean/security approval. An invalid input is rejected without replacing the previous saved result.

Use **Export selected analysis bundle** to create a new destination containing the exact retained files. Existing destinations are not overwritten. **Saved analyses** reopens earlier immutable bundles; restart uses the same durable profile. Delete is explicit and confirms the exact selected manifest. No automatic eviction or forensic-erasure claim is made. Help, runtime license notices and **Exit application** remain available at the minimum 980×700 window size. Exit waits for the one owned worker and closes its SQLite connection; it does not kill other applications.

## Local data and limits

The default version-independent profile is under `%LOCALAPPDATA%/JasonStys/RmfEvidenceWorkbench`; the source CLI keeps its existing explicit output/path arguments. Profile markers refuse unknown nonempty or linked paths rather than resetting them. A process lock, SQLite foreign keys/FULL synchronization/integrity checks and verified original-byte manifests protect application consistency. They do not provide authentication against another process running as the same OS user, encryption, collector authenticity or protection from an administrator. Keep the whole profile private and back it up only after clean exit. Plaintext history and exports may contain supplied evidence.

Retention is bounded to 20 analyses and 128 MiB of payload, with up to 8 files / 64 MiB per analysis and 32 MiB per file. Oversized inputs, malformed JSON, special files and unsafe links are rejected. There is no HTTP listener, live collector, account change, network lookup, user command/plugin or background upload in this native workflow. Original command-line capabilities remain available separately.

## Evidence, OSCAL and ledger meaning

Use an authorized educational workspace with its `bundle.json`, selected controls, evidence hashes/freshness and owner/risk metadata. Assessment exports canonical JSON/inert HTML plus all six original-schema-validated OSCAL models. Calendar lookahead is 1–168 hours. Compare normalized reports for the same system in nondecreasing chronology/revision; added/removed scope and risks retain NOT_SELECTED/NOT_RECORDED states. TypeScript remains an independently validated reviewer; the portable app uses the tested Python adapter and does not bundle Node.

Construct a **new** metadata ledger from up to 20 chronological normalized reports. Verify an existing **closed** ledger by copying bounded ordinary bytes into owned staging; active WAL/journal companions are refused. A separately retained expected tip detects a truncated/changed chain relative to that trusted tip. Blank means UNANCHORED_LOCAL_CHAIN; the stored tip alone is not independent authentication. No imported ledger or workspace is modified. These are six illustrative selected predicates, not full NIST assessment, risk acceptance or an authorization to operate: every report retains NOT_GRANTED.

The supported `jsonschema[format-nongpl]` extra retains actual URI and Unicode IRI validation using MIT-licensed `rfc3986-validator`, `rfc3987-syntax` and `lark`, replacing the formerly GPL3+ `rfc3987` leaf. All other locked versions/hashes are retained. Both format-family registration and real valid/invalid values are tested; actual installed dependency licenses/grammar data are bundled. This is an inventory and validation statement, not legal advice. See [official format-extra guidance](https://python-jsonschema.readthedocs.io/en/stable/validate/#format).

## Build and validation

Developers install `requirements-dev.lock` and `requirements-native.lock` with `--require-hashes`, then run `python scripts/build_native.py` and `python scripts/test_native_app.py` on Windows using Python 3.14.10. The builder checks runtime DLL identity, collects actual Python/Tcl/Tk and applicable dependency notices, and records source revision/resource hashes. The native consumer launches the actual frozen application twice with a fresh marked synthetic profile and a restricted environment; it drives the same widgets, worker, SQLite engine, core analyzers and exports, checks independent domain oracles and normal owned PID exit. Source-controller tests use inert presentation adapters and are distinct from this real-widget/frozen proof.

The original four OS/Python quality lanes, security gates and project-specific interoperability/collector contracts remain. The added Windows native lane audits its complete hash-locked build graph, builds and exercises the actual EXE. It uploads no package, test profile or Actions cache. Hosted jobs and a clean committed build must be reviewed before release; a local dirty candidate is not a published/installed product.
