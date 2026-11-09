"""Owner work calendar for exact evidence freshness, risk and milestone scope. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: calendar — line 62
# parameter: as_of — line 62
# parameter: horizon_hours — line 62
# parameter: workspace — line 62
# variable: instant — line 65
# variable: assessment — line 66
# variable: bundle — line 66
# variable: horizon — line 68
# variable: controls — line 71
# variable: row — line 71
# variable: risks — line 72
# variable: row — line 72
# variable: events — line 73
# definition: event — line 75
# parameter: control — line 76
# parameter: due — line 76
# parameter: kind — line 76
# parameter: reason — line 76
# parameter: reference — line 76
# variable: check — line 102
# variable: control — line 103
# variable: expires — line 116
# variable: risk — line 138
# variable: milestone — line 147
# parameter: row — line 172
# definition: publish — line 178
# parameter: output — line 178
# parameter: result — line 178
# variable: absolute — line 180
# variable: part — line 183
# variable: columns — line 186
# variable: rows — line 187
# variable: column — line 189
# variable: row — line 191
# variable: text — line 193
# variable: page — line 194
# variable: column — line 196
# variable: stream — line 203
# variable: writer — line 204
# variable: event — line 206
# variable: column — line 207
# variable: values — line 207
# variable: value — line 213
# END CODE MAP

from __future__ import annotations

import csv
import html
import io
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from rmf.assessment import assess
from rmf.contracts import canonical, integer, timestamp, uid


def calendar(workspace: Path, as_of: str, horizon_hours: int = 24) -> dict[str, Any]:
    """Assess current claims first,then schedule bounded selected-control evidence/risk work;never grant authorization."""
    integer(horizon_hours, 1, 168)
    instant = timestamp(as_of)
    bundle, assessment = assess(workspace, as_of)
    try:
        horizon = instant + timedelta(hours=horizon_hours)
    except OverflowError as error:
        raise ValueError("calendar horizon outside supported dates") from error
    controls = {row["id"]: row for row in bundle["controls"]}
    risks = {row["control_id"]: row for row in bundle["risks"]}
    events = []

    def event(
        kind: str, control: str, due: datetime, reference: str, reason: str
    ) -> None:
        """Include overdue work and bounded upcoming events with explicit unassigned ownership and exact scope."""
        if due > horizon:
            return
        events.append(
            {
                "id": uid(kind + ":" + reference + ":" + due.isoformat()),
                "kind": kind,
                "system_id": bundle["system"]["id"],
                "component_id": bundle["system"]["component_id"],
                "control_id": control,
                "reference": reference,
                "owner": risks[control]["owner"]
                if control in risks
                else "UNASSIGNED evidence owner",
                "due_at": due.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "timing": "OVERDUE"
                if due < instant
                else "DUE_NOW"
                if due == instant
                else "UPCOMING",
                "reason": reason,
            }
        )

    for check in assessment["checks"]:
        control = check["control_id"]
        if check["state"] in ("UNKNOWN", "INTEGRITY_ERROR"):
            event(
                "integrity_review"
                if check["state"] == "INTEGRITY_ERROR"
                else "evidence_gap",
                control,
                instant,
                check["evidence_id"] or control,
                check["reason"],
            )
        else:
            try:
                expires = timestamp(check["observed_at"]) + timedelta(
                    hours=controls[control]["max_age_hours"]
                )
            except OverflowError as error:
                raise ValueError(
                    "evidence freshness outside supported dates"
                ) from error
            event(
                "evidence_refresh_boundary",
                control,
                expires,
                check["evidence_id"],
                "Fresh through this instant;stale after it unless replaced by verified current evidence.",
            )
            if check["state"] == "NOT_SATISFIED":
                event(
                    "predicate_remediation_review",
                    control,
                    instant,
                    check["evidence_id"],
                    check["reason"],
                )
    for risk in bundle["risks"]:
        if risk["status"] != "resolved":
            event(
                "risk_due",
                risk["control_id"],
                timestamp(risk["due_at"]),
                risk["id"],
                "Unresolved selected lab risk;owner review is required,not automatic acceptance.",
            )
            for milestone in risk["milestones"]:
                if milestone["completed_at"] is None:
                    event(
                        "milestone_due",
                        risk["control_id"],
                        timestamp(milestone["due_at"]),
                        milestone["id"],
                        milestone["description"],
                    )
    return {
        "schema": 1,
        "kind": "continuous_monitoring_work_calendar",
        "author": "Jason Stys",
        "synthetic": True,
        "authorization": "NOT_GRANTED",
        "system_id": assessment["system_id"],
        "component_id": bundle["system"]["component_id"],
        "revision": assessment["revision"],
        "assessment_id": assessment["assessment_id"],
        "manifest_sha256": assessment["manifest_sha256"],
        "as_of": as_of,
        "horizon_hours": horizon_hours,
        "assessment_summary": assessment["summary"],
        "events": sorted(
            events,
            key=lambda row: (row["due_at"], row["control_id"], row["kind"], row["id"]),
        ),
        "scope": "Exact fictional system/component/control scope;expiry is evidence freshness,not necessarily technical regression. This is a review calendar,not risk acceptance,certification,authorization or a notification service. Current assessment gates remain mandatory.",
    }


def publish(result: dict[str, Any], output: Path) -> None:
    """Create new private JSON/escaped HTML/formula-neutral CSV;never embed raw evidence or send notifications."""
    absolute = output.absolute()
    if any(
        part.is_symlink() or part.is_junction()
        for part in (absolute, *absolute.parents)
    ):
        raise ValueError("linked monitoring output refused")
    columns = ("due_at", "timing", "kind", "control_id", "owner", "reason")
    rows = "".join(
        "<tr>"
        + "".join(f"<td>{html.escape(str(row[column]))}</td>" for column in columns)
        + "</tr>"
        for row in result["events"]
    )
    text = json.dumps(result, sort_keys=True, indent=2)
    page = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; base-uri \'none\'; form-action \'none\'"><title>Evidence work calendar — Jason Stys</title><main><h1>Evidence freshness and remediation calendar</h1><p>Created by Jason Stys. Fictional selected scope. Authorization: NOT_GRANTED.</p><table><caption>Owner review work;freshness gaps are not automatically technical regressions</caption><tr>'
        + "".join(f"<th>{column}</th>" for column in columns)
        + "</tr>"
        + rows
        + "</table><details><summary>Exact assessment scope,hashes and boundaries</summary><pre>"
        + html.escape(text)
        + "</pre></details></main></html>"
    )
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(columns)
    for event in result["events"]:
        values = [str(event[column]) for column in columns]
        writer.writerow(
            [
                "'" + value
                if value.lstrip().startswith(("=", "+", "-", "@"))
                else value
                for value in values
            ]
        )
    absolute.mkdir(mode=0o700)
    (absolute / "calendar.json").write_text(canonical(result) + "\n", encoding="utf-8")
    (absolute / "calendar.html").write_text(page, encoding="utf-8")
    (absolute / "calendar.csv").write_text(
        stream.getvalue(), encoding="utf-8", newline=""
    )
