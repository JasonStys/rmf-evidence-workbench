# Documentation refresh — 2026-11-09

By Jason Stys.

This documentation-only edition describes source `07b1b4973921b831d6eba4a9c7e375d8977863f4`. It does not change application behavior, accounts, private data, installers or published releases.

## Published editions and completed review

| File | Bytes | SHA-256 | Reviewed scope |
| --- | ---: | --- | --- |
| [project-guide.docx](project-guide.docx) | 45097 | `70ec04cc80c70c95324ccf9ef8beaa4d6dd1203f06344a6ba183fac16838503f` | 5 pages, each viewed individually |

Word review checked plain black titles, readable pagination, whole table rows, source references, practical limits and absence of clipping or overflow. Render receipts were matched to the current DOCX digest before approval.

## Evidence and change boundary

- Functional baseline: `07b1b4973921b831d6eba4a9c7e375d8977863f4`.
- Workflow observation: `2026-11-10T05:25:40.628667+00:00`; exact run URLs and source identities remain in [publications.json](publications.json).
- Local document-package validation verifies exact copied bytes, Office ZIP integrity, approved page/tab identities and internal documentation links. Repository-specific documentation and source-policy commands are run separately and recorded in the integration handoff.
- Source/index metadata is regenerated using the repository’s existing tools. Existing privacy, security, coverage and workflow gates are retained.
- PR and later main workflows must pass independently. This record does not claim future or unrun integration CI success.

## Interpretation

The Word files document the cited source; dated source reports retain their original execution scope. A passing workflow is distinct from completed analysis with zero findings, and neither establishes production suitability. Checksums identify exact bytes, not a signature or publisher attestation.

Use the [handbook](../handbook.md) to choose usage, design, security and test documentation. Keep editable Markdown and reviewed editions together; do not replace historical measurements with undated claims.

## Actual integration validation

117 Python tests passed at 95.61% combined coverage retaining the 90% floor; three TypeScript reviewer tests, Ruff/format, strict mypy, exact Python/TS maps, immutable schema/example/workflow guards and exhaustive tracked-file inventory passed. No runtime or Office-reader implementation change; named inventory metadata only.
