# Local reviewer and evidence operating runbook

## Reproduce and inspect

Use README quickstart. `scripts/demo.py --output out/new-demo` uses only versioned fictional examples. It validates twelve exported documents with both engines, appends two real SQLite snapshots, verifies the independently retained in-memory demo tip and compares control/risk changes through the compiled TypeScript CLI. The demo stops after the finite job; there is no background service, network listener or Docker dependency.

Open the baseline/remediated HTML files directly in any browser. Attribution, summary/details, quality states, due dates, pending milestones and help references are present. No scripts, external assets, trackers, accounts or active file-upload forms are embedded. JSON keeps consistent fields for all selected checks. Raw source facts remain in the input workspace; no file contents are automatically attached to a public repo or assessment export.

Read quality before interpreting satisfaction. For an integrity error, compare expected vs actual hashes and collection/scope claims. Do not update a trusted hash simply to make an unknown artifact pass. For missing/stale evidence, request a new authorized collection and retain its provenance. This application supplies no production collector or remote-account connector. For a gap, record a meaningful owner/deadline/milestone and obtain fresh appropriate evidence before considering resolution.

## Manual local workflow

Create a **new** ledger explicitly with `python -m rmf init-ledger out/evidence.db`. Assessment takes a workspace, explicit `--as-of` clock and new `--output` directory; optional `--ledger` appends the normalized snapshot. Run `validate-oscal <output>` for original schemas plus the supported semantic chain, and `node scripts/oscal_check.mjs <output>` for independent native schema validation. The standalone Node schema checker is structural; it is not the Python evidence or semantic assessor.

Record append receipts outside the database. Use `verify-ledger <path> --expected-tip <saved-tip>` to verify the externally anchored chain. Without a tip, output says `UNANCHORED_LOCAL_CHAIN`. `history <path> --state NOT_SATISFIED` uses a fixed SQL query with a bound state filter. SQL examples for operators are `SELECT seq,as_of FROM snapshots ORDER BY seq;` and `SELECT control_id,state FROM findings WHERE snapshot_seq=?;` with parameter binding in application code.

The TypeScript reviewer expects two canonical `assessment.json` files produced by this tool. Different system IDs, malformed fields/counts, unexpected keys, invalid calendars, terminal controls and content-ID mismatches fail. It shows status transitions, not a new authorization/risk-acceptance decision. Byte fingerprints and full risk projection history remain in the original files/ledger.

## Failure handling and privacy

An invalid command/input returns nonzero and prints a generic contract error; raw exception instances/private content are not printed. A valid assessment may contain unknown/unsatisfied states while execution succeeds—those states are **expected data**, not a failing software test. A failed export preserves existing output. If a ledger append fails after report publication, its transaction rolls back and the report directory remains available for diagnosis; report publication and database append are not one cross-filesystem atomic transaction.

Data is local plaintext. Best-effort 0700 directories do not replace Windows ACLs, disk encryption, a secure device or proper organization controls. Local administrators can read/rewrite files and drop SQLite triggers. Use synthetic samples only until a reviewed private deployment/collection/storage design is in place. Do not publish real SSPs, assessment results, vulnerabilities, identities, account data, credentials or customer evidence.

## Update, rollback and cleanup

Schema updates require reviewing NIST's release metadata, changing checksums, preserving original notices and rerunning **both** schema engines, mutation tests and semantic checks. The vendoring script is the only explicit schema-download operation; normal assessment/validation never fetches import URIs. Cache keys include immutable verified bytes, so a file changed after a warmup is still hash-checked.

If evidence counts/identity/predicates, privacy, semantic-reference or supply-chain gates fail, stop and investigate before adapting the lab. Revert a reviewed source change via a new commit and rerun validation. Do not weaken assertions, claim certification or automatically close real findings. Preserve needed reports/tips before manually deleting an explicitly inspected demo output. The tool never deletes prior output, runs, caches, accounts or unrelated files.
