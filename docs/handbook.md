# RMF Evidence Workbench handbook

By Jason Stys.

Build owner monitoring calendars and exact component-scoped freshness, integrity, risk and milestone work queues.

Build owner monitoring calendars and exact component-scoped freshness, integrity, risk and milestone work queues.

Helps maintain evidence continuously without claiming that a dashboard grants authorization.

## Read the documentation

| Edition | Audience and contents |
| --- | --- |
| [project-guide.docx](reports/project-guide.docx) | User and developer guide: purpose, current usage, design, boundaries and source references. |

The editable Markdown remains the maintenance source. The Word files are readable editions. See [publication identities and review](reports/publications.json) and the [documentation refresh record](reports/documentation-refresh-2026-11-09.md).

## Current usage and help

[README quick start](../README.md) is the entry point. Use the project-specific guides below before changing inputs, operating modes or deployment assumptions.

### Usage and operations

- [runbook](runbook.md)

### Design and contracts

- [architecture](architecture.md)
- [contracts](contracts.md)
- [research](research.md)

### Security and validation

- [testing](testing.md)

## Historical results and reproduction

The reviewed source is [`07b1b4973921b831d6eba4a9c7e375d8977863f4`](https://github.com/JasonStys/rmf-evidence-workbench/tree/07b1b4973921b831d6eba4a9c7e375d8977863f4). The observed functional workflow baseline is `07b1b4973921b831d6eba4a9c7e375d8977863f4`; those observations are recorded at `2026-11-10T05:25:40.628667+00:00`. They do not certify an unrun later revision.

- [Detailed recorded validation](reports/calendar-2026-11-09.md)
- [Current Actions](https://github.com/JasonStys/rmf-evidence-workbench/actions) records later integration checks separately.
- Preserve dated measurements and follow the existing testing guide to reproduce them; a test-source inventory alone does not establish execution.

## Practical boundaries

- Synthetic selected six-control scope, not certification, authorization to operate or risk acceptance.
- Owner calendars and queues do not collect real evidence or send live notifications.
- Freshness/integrity review supports human monitoring; it does not grant an authorization or waive missing evidence.

## Maintaining these editions

Update the editable usage/design/test documents first. Rebuild and visually review every Word page and workbook tab before replacing an edition; verify the exact binary digests and evidence source in publications.json. Keep account data, logs with secrets, installed-app state and private test stores out of documentation. Source and release assets retain their existing security and licensing boundaries.

## Native workbench 1.1.0

[Native usage, offline data boundary, packaging and real-widget validation](native-workbench.md). The CLI and original validation gates remain; supplied evidence is never live enforcement or a security/authorization approval. Historical report measurements remain dated observations of their recorded sources.
