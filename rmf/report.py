"""Render escaped inert reviewer evidence and six validated OSCAL exports. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: publish — line 31
# parameter: bundle — line 31
# parameter: output — line 31
# parameter: result — line 31
# variable: documents — line 34
# variable: rows — line 39
# variable: field — line 43
# variable: check — line 46
# variable: risk_rows — line 48
# variable: field — line 52
# variable: risk — line 63
# variable: page — line 65
# variable: document — line 83
# variable: model — line 83
# END CODE MAP

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from rmf.contracts import canonical
from rmf.ledger import validate_report
from rmf.oscal import build


def publish(bundle: dict[str, Any], result: dict[str, Any], output: Path) -> None:
    """Validate before creating exclusive output, then write offline JSON/HTML/models without embedding raw evidence."""
    validate_report(result)
    documents = build(bundle, result)
    output.mkdir(parents=True, mode=0o700, exist_ok=False)
    (output / "assessment.json").write_text(
        canonical(result) + "\n", encoding="utf-8", newline="\n"
    )
    rows = "".join(
        "<tr>"
        + "".join(
            "<td>" + html.escape(str(check[field])) + "</td>"
            for field in ("control_id", "title", "state", "reason", "observed_at")
        )
        + "</tr>"
        for check in result["checks"]
    )
    risk_rows = "".join(
        "<tr>"
        + "".join(
            "<td>" + html.escape(str(risk[field])) + "</td>"
            for field in (
                "control_id",
                "severity",
                "status",
                "owner",
                "due_at",
                "overdue",
                "pending_milestones",
            )
        )
        + "</tr>"
        for risk in result["risks"]
    )
    page = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; base-uri \'none\'; form-action \'none\'"><title>RMF evidence — Jason Stys</title><body><h1>RMF Evidence Workbench</h1><p>Created by Jason Stys · github.com/JasonStys · LinkedIn: jason-stys-31b30b351</p><p>Fictional educational evidence only. Authorization: NOT_GRANTED. Selected lab predicates are not complete NIST control assessments or a compliance certification.</p><h2>System and snapshot</h2><p>'
        + html.escape(
            result["system_name"]
            + " · revision "
            + str(result["revision"])
            + " · "
            + result["as_of"]
        )
        + "</p><h2>Evidence checks</h2><table><caption>Missing/stale evidence is unknown, not satisfied</caption><thead><tr><th>Control</th><th>Title</th><th>State</th><th>Reason</th><th>Claimed observation</th></tr></thead><tbody>"
        + rows
        + "</tbody></table><h2>Remediation</h2><table><caption>Fictional risk owners and milestones</caption><thead><tr><th>Control</th><th>Severity</th><th>Status</th><th>Owner</th><th>Due</th><th>Overdue</th><th>Pending milestones</th></tr></thead><tbody>"
        + risk_rows
        + "</tbody></table><h2>Normalized reviewer data</h2><pre>"
        + html.escape(json.dumps(result, indent=2, sort_keys=True))
        + "</pre><p>Help: README and docs/runbook.md. Source evidence stays in the input workspace; this report does not embed private raw files.</p></body></html>"
    )
    (output / "assessment.html").write_text(page, encoding="utf-8", newline="\n")
    for model, document in documents.items():
        (output / f"{model}.json").write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
