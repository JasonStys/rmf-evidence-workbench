"""Offline evidence/OSCAL, owner calendar and independently anchored ledger workflows using the real RMF engines. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 106
# variable: PRODUCT — line 107
# variable: PROFILE — line 107
# variable: TITLE — line 108
# variable: VERSION — line 108
# variable: COLUMNS — line 109
# variable: RESOURCES — line 115
# variable: revision — line 118
# variable: name — line 119
# variable: name — line 131
# variable: MODES — line 152
# variable: REVIEW_MODE — line 159
# variable: CHOICES — line 160
# variable: FIELDS — line 161
# variable: ACTIVE_FIELDS — line 179
# variable: SCENARIOS — line 186
# variable: HELP — line 193
# definition: scenario — line 196
# parameter: name — line 196
# variable: values — line 200
# definition: text_bundle — line 222
# parameter: title — line 222
# parameter: value — line 222
# variable: raw — line 224
# variable: page — line 225
# definition: report — line 237
# parameter: path — line 237
# definition: comparison — line 242
# parameter: after — line 242
# parameter: before — line 242
# variable: prior — line 255
# variable: row — line 255
# variable: current — line 256
# variable: row — line 256
# variable: old_risks — line 257
# variable: row — line 259
# variable: new_risks — line 261
# variable: row — line 263
# variable: key — line 276
# variable: key — line 285
# definition: analyze — line 291
# parameter: parameters — line 292
# parameter: stage — line 292
# parameter: state — line 292
# variable: mode — line 295
# variable: result — line 296
# variable: bundle — line 298
# variable: result — line 298
# variable: output — line 299
# variable: summary — line 301
# variable: count — line 302
# variable: key — line 302
# variable: p — line 308
# variable: raw — line 311
# variable: result — line 319
# variable: output — line 322
# variable: p — line 327
# variable: result — line 330
# variable: paths — line 337
# variable: row — line 338
# variable: path — line 342
# variable: reports — line 342
# variable: database — line 343
# variable: receipt — line 345
# variable: value — line 346
# variable: receipt — line 347
# variable: result — line 349
# variable: files — line 356
# variable: source — line 367
# variable: suffix — line 370
# variable: expected — line 373
# variable: database — line 376
# variable: result — line 378
# definition: views — line 391
# parameter: files — line 391
# variable: result — line 394
# variable: k — line 399
# variable: v — line 399
# variable: result — line 403
# variable: k — line 407
# variable: v — line 407
# variable: result — line 410
# variable: k — line 418
# variable: v — line 418
# definition: cells — line 429
# parameter: row — line 429
# END CODE MAP

from __future__ import annotations

import html
import re
import sys
from pathlib import Path
from typing import Any

from . import ledger, monitoring
from .assessment import assess
from .contracts import timestamp
from .desktop_io import Rejected, canonical, json_value, read_bytes
from .desktop_state import Workspace
from .report import publish

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
PRODUCT, PROFILE = "rmf-evidence-workbench", "RmfEvidenceWorkbench"
TITLE, VERSION = "RMF Evidence Workbench", "1.1.1"
COLUMNS = (
    "Control / snapshot",
    "Evidence / work type",
    "Reason / owner",
    "State / timing",
)
RESOURCES = (
    tuple(
        "examples/" + revision + "/" + name
        for revision in ("baseline", "remediated")
        for name in (
            "bundle.json",
            "evidence/ac-2.json",
            "evidence/ac-3.json",
            "evidence/au-2.json",
            "evidence/au-6.json",
            "evidence/cm-6.json",
            "evidence/cp-9.json",
        )
    )
    + tuple(
        "schemas/oscal_" + name + "_schema.json"
        for name in (
            "catalog",
            "profile",
            "ssp",
            "assessment-plan",
            "assessment-results",
            "poam",
        )
    )
    + (
        "schemas/NIST-NOTICE.md",
        "schemas/NOTICE.md",
        "oscal.lock.json",
        "ops/schema.sql",
        "examples/desktop/baseline-assessment.json",
        "examples/desktop/remediated-assessment.json",
        "notices.txt",
        "app.ico",
        "python314.dll",
    )
)
MODES = (
    "Assess evidence and export six OSCAL models",
    "Build owner evidence/remediation calendar",
    "Compare normalized assessment reports",
    "Build new ledger from selected reports",
    "Verify closed ledger against retained tip",
)
REVIEW_MODE = None
CHOICES: dict[str, tuple[str, ...]] = {}
FIELDS = (
    (
        "workspace",
        "Authorized workspace folder (bundle.json and evidence)",
        "directory",
    ),
    ("as_of", "Explicit assessment time (UTC, e.g. 2026-10-12T12:00:00Z)", "text"),
    ("horizon", "Calendar lookahead hours (1–168)", "text"),
    ("before", "Earlier normalized assessment JSON", "file"),
    ("after", "Later normalized assessment JSON", "file"),
    (
        "reports",
        "Chronological assessment files (one path per line; at most 20)",
        "files",
    ),
    ("ledger", "Closed ledger file (no active WAL/journal)", "file"),
    ("tip", "Separately retained expected SHA256 tip (blank = unanchored)", "text"),
)
ACTIVE_FIELDS = {
    MODES[0]: ("workspace", "as_of"),
    MODES[1]: ("workspace", "as_of", "horizon"),
    MODES[2]: ("before", "after"),
    MODES[3]: ("reports",),
    MODES[4]: ("ledger", "tip"),
}
SCENARIOS = (
    "Fictional baseline evidence and OSCAL",
    "Fictional remediated evidence and OSCAL",
    "Fictional owner calendar",
    "Fictional normalized report comparison",
    "Fictional two-snapshot ledger",
)
HELP = "Select an authorized educational RMF workspace; its bundle controls/requirements, freshness limits, evidence hashes and risk owners remain the policy. Six selected predicates are not full NIST control assessments. Missing/stale evidence remains UNKNOWN and every outcome keeps authorization NOT_GRANTED. Assessment exports six real local-schema-validated OSCAL models without embedding raw evidence. Calendar review never grants risk acceptance. Ledger construction creates a new local copy; keep its tip independently. Ledger verification is read-only on a bounded copied closed file; a blank tip means UNANCHORED_LOCAL_CHAIN, not authenticity or truncation protection. No remote imports, host collection, notifications, credentials or enforcement. Prepared fictional scenarios populate the same controls. History/exports are plaintext OS-owner data."


def scenario(name: str) -> dict[str, str]:
    """Prepare actual public fictional project inputs, never automatic approval, authorization or analysis."""
    if name not in SCENARIOS:
        raise Rejected("unknown prepared scenario")
    values = {
        "mode": MODES[0],
        "workspace": str(ROOT / "examples/baseline"),
        "as_of": "2026-10-12T12:00:00Z",
        "horizon": "24",
        "before": str(ROOT / "examples/desktop/baseline-assessment.json"),
        "after": str(ROOT / "examples/desktop/remediated-assessment.json"),
        "reports": str(ROOT / "examples/desktop/baseline-assessment.json")
        + "\n"
        + str(ROOT / "examples/desktop/remediated-assessment.json"),
        "ledger": "",
        "tip": "",
    }
    if name == SCENARIOS[1]:
        values.update(
            workspace=str(ROOT / "examples/remediated"), as_of="2026-10-13T12:00:00Z"
        )
    elif name in SCENARIOS[2:]:
        values["mode"] = MODES[SCENARIOS.index(name) - 1]
    return values


def text_bundle(value: dict[str, Any], title: str) -> dict[str, bytes]:
    """Encode finite normalized metadata and escaped inert HTML; never turn review text into executable markup."""
    raw = canonical(value)
    page = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; base-uri &#39;none&#39;; form-action &#39;none&#39;"><title>'
        + html.escape(title)
        + "</title><main><h1>"
        + html.escape(title)
        + "</h1><p>Jason Stys. Educational selected scope. Authorization: NOT_GRANTED.</p><pre>"
        + html.escape(raw.decode())
        + "</pre></main></html>"
    )
    return {"result.json": raw, "result.html": page.encode()}


def report(path: str) -> dict[str, Any]:
    """Require original core report content identity and closed fields before comparison or ledger append."""
    return ledger.validate_report(json_value(read_bytes(Path(path), 2 * 1024 * 1024)))


def comparison(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Mirror the existing independent reviewer semantics in linear work, retaining NOT_SELECTED/NOT_RECORDED scope changes."""
    ledger.validate_report(before)
    ledger.validate_report(after)
    if before["system_id"] != after["system_id"]:
        raise Rejected("comparison requires the same system boundary")
    if (
        timestamp(before["as_of"]) > timestamp(after["as_of"])
        or before["revision"] > after["revision"]
    ):
        raise Rejected(
            "comparison requires nondecreasing assessment chronology and revision"
        )
    prior = {row["control_id"]: row["state"] for row in before["checks"]}
    current = {row["control_id"]: row["state"] for row in after["checks"]}
    old_risks = {
        row["id"]: row["status"] + ";overdue=" + str(row["overdue"]).lower()
        for row in before["risks"]
    }
    new_risks = {
        row["id"]: row["status"] + ";overdue=" + str(row["overdue"]).lower()
        for row in after["risks"]
    }
    return {
        "author": "Jason Stys",
        "authorization": "NOT_GRANTED",
        "before_assessment_id": before["assessment_id"],
        "after_assessment_id": after["assessment_id"],
        "changes": [
            {
                "control_id": key,
                "before": prior.get(key, "NOT_SELECTED"),
                "after": current.get(key, "NOT_SELECTED"),
            }
            for key in sorted(prior.keys() | current.keys())
            if prior.get(key) != current.get(key)
        ],
        "risk_changes": [
            {
                "id": key,
                "before": old_risks.get(key, "NOT_RECORDED"),
                "after": new_risks.get(key, "NOT_RECORDED"),
            }
            for key in sorted(old_risks.keys() | new_risks.keys())
            if old_risks.get(key) != new_risks.get(key)
        ],
    }


def analyze(
    state: Workspace, parameters: dict[str, str], stage: Path
) -> tuple[str, str, dict[str, bytes]]:
    """Run actual assessment/schema/calendar/ledger engines; write only fresh staged output, never imported source files."""
    mode = parameters["mode"]
    result: dict[str, Any]
    if mode == MODES[0]:
        bundle, result = assess(Path(parameters["workspace"]), parameters["as_of"])
        output = stage / "assessment"
        publish(bundle, result, output)
        summary = (
            "; ".join(f"{count} {key}" for key, count in result["summary"].items())
            + "; authorization NOT_GRANTED"
        )
        return (
            mode,
            summary,
            {p.name: read_bytes(p, 32 * 1024 * 1024) for p in output.iterdir()},
        )
    if mode == MODES[1]:
        raw = parameters["horizon"].strip()
        if (
            not raw.isascii()
            or not raw.isdecimal()
            or len(raw) > 3
            or not 1 <= int(raw) <= 168
        ):
            raise Rejected("calendar horizon must be a base-ten integer from 1 to 168")
        result = monitoring.calendar(
            Path(parameters["workspace"]), parameters["as_of"], int(raw)
        )
        output = stage / "calendar"
        monitoring.publish(result, output)
        return (
            mode,
            f"{len(result['events'])} selected-scope owner work items; authorization NOT_GRANTED",
            {p.name: read_bytes(p, 32 * 1024 * 1024) for p in output.iterdir()},
        )
    if mode == MODES[2]:
        result = comparison(report(parameters["before"]), report(parameters["after"]))
        return (
            mode,
            f"{len(result['changes'])} control and {len(result['risk_changes'])} risk transitions; authorization NOT_GRANTED",
            text_bundle(result, "Normalized assessment transitions"),
        )
    if mode == MODES[3]:
        paths = [
            row.strip() for row in parameters["reports"].splitlines() if row.strip()
        ]
        if not 1 <= len(paths) <= 20:
            raise Rejected("select between1 and20 chronological normalized reports")
        reports = [report(path) for path in paths]
        database = stage / "ledger.sqlite"
        ledger.create(database)
        receipt = None
        for value in reports:
            receipt = ledger.append(database, value)
        assert receipt is not None
        result = {
            "authorization": "NOT_GRANTED",
            "receipt": receipt,
            "verification": ledger.verify(database),
            "history": ledger.history(database),
            "scope": "New local chain; save the receipt tip independently. Local verification is not acquisition identity or truncation proof.",
        }
        files = text_bundle(
            result, "New metadata ledger and independent-tip instructions"
        )
        files["ledger.sqlite"] = read_bytes(database, 32 * 1024 * 1024)
        return (
            mode,
            f"{receipt['snapshots']} normalized snapshots; save tip independently; authorization NOT_GRANTED",
            files,
        )
    if mode != MODES[4]:
        raise Rejected("unsupported offline operation")
    source = Path(parameters["ledger"])
    if any(
        source.with_name(source.name + suffix).exists()
        for suffix in ("-wal", "-journal", "-shm")
    ):
        raise Rejected("close the source ledger and checkpoint it before inspection")
    expected = parameters["tip"].strip()
    if expected and not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise Rejected("independent expected tip must be lowercase SHA256")
    database = stage / "imported-ledger.sqlite"
    database.write_bytes(read_bytes(source, 32 * 1024 * 1024))
    result = {
        "authorization": "NOT_GRANTED",
        "verification": ledger.verify(database, expected or None),
        "history": ledger.history(database),
        "scope": "Bounded copied closed input, read-only verification; no acquisition identity or certification. A blank tip is unanchored.",
    }
    return (
        mode,
        f"{result['verification']['snapshots']} snapshots; {result['verification']['assurance']}; authorization NOT_GRANTED",
        text_bundle(result, "Ledger verification and original normalized history"),
    )


def views(files: dict[str, bytes]) -> dict[str, list[dict[str, Any]]]:
    """Present exact original selected-control states, owners and anchored/unanchored evidence without granting authorization."""
    if "assessment.json" in files:
        result = json_value(files["assessment.json"])
        return {
            "Original evidence predicates": result["checks"],
            "Risk owners and milestones": result["risks"],
            "Assessment scope and identity": [
                {k: v for k, v in result.items() if k not in {"checks", "risks"}}
            ],
        }
    if "calendar.json" in files:
        result = json_value(files["calendar.json"])
        return {
            "Owner work calendar": result["events"],
            "Exact calendar scope": [
                {k: v for k, v in result.items() if k != "events"}
            ],
        }
    result = json_value(files["result.json"])
    if "changes" in result:
        return {
            "Control transitions": result["changes"],
            "Risk transitions": result["risk_changes"],
            "Compared identities": [
                {
                    k: v
                    for k, v in result.items()
                    if k not in {"changes", "risk_changes"}
                }
            ],
        }
    return {
        "Ledger assurance": [result["verification"]],
        "Original normalized snapshots": result["history"],
    }


def cells(row: dict[str, Any]) -> tuple[str, str, str, str]:
    """Keep table cells compact; full literal records, hashes, chronology and uncertainty remain inspectable."""
    return (
        str(row.get("control_id", row.get("assessment_id", row.get("id", "scope")))),
        str(row.get("kind", row.get("reason", row.get("title", "evidence")))),
        str(row.get("owner", row.get("due_at", "inspect full scope"))),
        str(
            row.get(
                "state",
                row.get(
                    "timing", row.get("assurance", row.get("after", "NOT_GRANTED"))
                ),
            )
        ),
    )
