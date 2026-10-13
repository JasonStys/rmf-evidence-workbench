"""Assess selected lab checks with evidence integrity, freshness and gated remediation. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: CHECKS — line 104
# definition: load_bundle — line 114
# parameter: root — line 114
# variable: bundle — line 116
# variable: system — line 122
# variable: controls — line 128
# variable: selected — line 129
# variable: value — line 130
# variable: control — line 131
# variable: seen — line 139
# variable: evidence_controls — line 140
# variable: value — line 141
# variable: evidence — line 142
# variable: identity — line 145
# variable: risk_controls — line 166
# variable: value — line 167
# variable: risk — line 168
# variable: identity — line 183
# variable: due — line 199
# variable: opened — line 199
# variable: item — line 209
# variable: milestone — line 210
# variable: milestone_id — line 211
# variable: milestone_due — line 216
# definition: evaluate_facts — line 227
# parameter: control_id — line 227
# parameter: facts — line 227
# variable: data — line 230
# variable: active — line 231
# variable: data — line 234
# variable: value — line 235
# variable: data — line 239
# variable: source — line 240
# variable: data — line 243
# variable: data — line 248
# variable: data — line 250
# variable: rpo — line 253
# variable: rto — line 253
# definition: evidence_result — line 257
# parameter: root — line 258
# parameter: evidence — line 259
# parameter: control — line 260
# parameter: component_id — line 261
# parameter: as_of — line 262
# variable: content — line 268
# variable: actual_hash — line 271
# variable: data — line 279
# variable: age — line 295
# variable: satisfied — line 298
# definition: assess — line 308
# parameter: as_of — line 308
# parameter: root — line 308
# variable: instant — line 310
# variable: bundle — line 311
# variable: evidence_by_control — line 312
# variable: value — line 312
# variable: checks — line 313
# parameter: value — line 314
# variable: control — line 314
# variable: evidence — line 315
# variable: actual_hash — line 316
# variable: reason — line 316
# variable: state — line 316
# variable: by_control — line 331
# variable: value — line 331
# variable: risks — line 332
# parameter: value — line 333
# variable: risk — line 333
# variable: completed — line 334
# variable: milestone_times — line 335
# variable: value — line 337
# variable: value — line 340
# variable: value — line 345
# variable: check — line 351
# variable: value — line 355
# variable: value — line 373
# variable: result — line 376
# variable: value — line 388
# variable: state — line 389
# END CODE MAP

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from rmf.contracts import (
    array,
    canonical,
    digest,
    identifier,
    integer,
    obj,
    parse_json,
    safe_bytes,
    text,
    timestamp,
    uid,
)

CHECKS = {
    "ac-2": "account-review",
    "ac-3": "access-denial",
    "au-2": "audit-completeness",
    "au-6": "audit-review",
    "cm-6": "configuration-drift",
    "cp-9": "restore-check",
}


def load_bundle(root: Path) -> dict[str, Any]:
    """Validate the closed educational workspace manifest and reject dangling or duplicate scope/record IDs."""
    bundle = obj(
        parse_json(safe_bytes(root, "bundle.json")),
        {"schema", "system", "revision", "controls", "evidence", "risks"},
    )
    if integer(bundle["schema"], 1, 1) != 1:
        raise ValueError("unsupported bundle schema")
    system = obj(bundle["system"], {"id", "name", "boundary", "component_id"})
    identifier(system["id"])
    identifier(system["component_id"])
    text(system["name"], 120)
    text(system["boundary"])
    integer(bundle["revision"], 1, 100_000)
    controls = array(bundle["controls"], 1)
    selected = set()
    for value in controls:
        control = obj(value, {"id", "title", "requirement", "max_age_hours"})
        text(control["id"], 32)
        if control["id"] not in CHECKS or control["id"] in selected:
            raise ValueError("unknown or duplicate selected lab control")
        selected.add(control["id"])
        text(control["title"], 120)
        text(control["requirement"])
        integer(control["max_age_hours"], 1, 168)
    seen: set[str] = set()
    evidence_controls: set[str] = set()
    for value in array(bundle["evidence"]):
        evidence = obj(
            value, {"id", "control_id", "component_id", "path", "sha256", "observed_at"}
        )
        identity = identifier(evidence["id"])
        text(evidence["control_id"], 32)
        if (
            identity in seen
            or evidence["control_id"] in evidence_controls
            or evidence["control_id"] not in selected
        ):
            raise ValueError("duplicate or out-of-scope evidence")
        if identifier(evidence["component_id"]) != system["component_id"]:
            raise ValueError("evidence component is outside this system")
        if not isinstance(evidence["sha256"], str) or not re.fullmatch(
            r"[0-9a-f]{64}", evidence["sha256"]
        ):
            raise ValueError("evidence digest required")
        if not isinstance(evidence["path"], str) or not re.fullmatch(
            r"evidence/[a-z0-9_-]+\.json", evidence["path"]
        ):
            raise ValueError("evidence references must be fixed local JSON paths")
        timestamp(evidence["observed_at"])
        seen.add(identity)
        evidence_controls.add(evidence["control_id"])
    risk_controls: set[str] = set()
    for value in array(bundle["risks"]):
        risk = obj(
            value,
            {
                "id",
                "control_id",
                "severity",
                "status",
                "owner",
                "description",
                "opened_at",
                "due_at",
                "completed_at",
                "milestones",
            },
        )
        identity = identifier(risk["id"])
        text(risk["control_id"], 32)
        text(risk["severity"], 32)
        text(risk["status"], 32)
        if (
            identity in seen
            or risk["control_id"] not in selected
            or risk["control_id"] in risk_controls
        ):
            raise ValueError("duplicate or dangling risk")
        if risk["severity"] not in {"low", "moderate", "high"} or risk[
            "status"
        ] not in {"open", "in-progress", "resolved"}:
            raise ValueError("unsupported risk classification/state")
        text(risk["owner"], 120)
        text(risk["description"])
        opened, due = timestamp(risk["opened_at"]), timestamp(risk["due_at"])
        if opened > due:
            raise ValueError("risk due before opening")
        if (
            risk["completed_at"] is not None
            and timestamp(risk["completed_at"]) < opened
        ):
            raise ValueError("risk completed before opening")
        seen.add(identity)
        risk_controls.add(risk["control_id"])
        for item in array(risk["milestones"], 1):
            milestone = obj(item, {"id", "description", "due_at", "completed_at"})
            milestone_id = identifier(milestone["id"])
            if milestone_id in seen:
                raise ValueError("duplicate milestone UUID")
            seen.add(milestone_id)
            text(milestone["description"])
            milestone_due = timestamp(milestone["due_at"])
            if not opened <= milestone_due <= due:
                raise ValueError("milestone outside risk time window")
            if (
                milestone["completed_at"] is not None
                and timestamp(milestone["completed_at"]) < opened
            ):
                raise ValueError("milestone completed before risk opening")
    return bundle


def evaluate_facts(control_id: str, facts: object) -> bool:
    """Evaluate only six authored illustrative predicates; do not infer full NIST-control implementation."""
    if control_id == "ac-2":
        data = obj(facts, {"active_accounts", "reviewed_accounts"})
        active = integer(data["active_accounts"], 1)
        return integer(data["reviewed_accounts"]) == active
    if control_id == "ac-3":
        data = obj(facts, {"unauthorized_denied", "cross_tenant_denied"})
        if any(type(value) is not bool for value in data.values()):
            raise ValueError("exact boolean access outcomes required")
        return all(data.values())
    if control_id == "au-2":
        data = obj(facts, {"source_events", "retained_events"})
        source = integer(data["source_events"], 1)
        return integer(data["retained_events"]) == source
    if control_id == "au-6":
        data = obj(facts, {"review_completed"})
        if type(data["review_completed"]) is not bool:
            raise ValueError("exact review boolean required")
        return bool(data["review_completed"])
    if control_id == "cm-6":
        data = obj(facts, {"drift_count"})
        return integer(data["drift_count"]) == 0
    data = obj(facts, {"restore_verified", "rpo_seconds", "rto_seconds"})
    if type(data["restore_verified"]) is not bool:
        raise ValueError("exact restore boolean required")
    rpo, rto = integer(data["rpo_seconds"]), integer(data["rto_seconds"])
    return bool(data["restore_verified"]) and rpo <= 300 and rto <= 900


def evidence_result(
    root: Path,
    evidence: dict[str, Any] | None,
    control: dict[str, Any],
    component_id: str,
    as_of: str,
) -> tuple[str, str, str | None]:
    """Require exact bytes, matching provenance/scope and fresh facts; missing/stale/invalid facts are UNKNOWN."""
    if evidence is None:
        return "UNKNOWN", "No evidence record supplied", None
    try:
        content = safe_bytes(root, evidence["path"])
    except FileNotFoundError:
        return "UNKNOWN", "Referenced evidence file is missing", None
    actual_hash = digest(content)
    if actual_hash != evidence["sha256"]:
        return (
            "INTEGRITY_ERROR",
            "Evidence bytes do not match trusted manifest digest",
            actual_hash,
        )
    try:
        data = obj(
            parse_json(content),
            {"schema", "control_id", "component_id", "observed_at", "check", "facts"},
        )
        if (
            integer(data["schema"], 1, 1) != 1
            or data["control_id"] != control["id"]
            or data["component_id"] != component_id
            or data["observed_at"] != evidence["observed_at"]
            or data["check"] != CHECKS[control["id"]]
        ):
            return (
                "INTEGRITY_ERROR",
                "Evidence scope/provenance differs from manifest",
                actual_hash,
            )
        age = (timestamp(as_of) - timestamp(data["observed_at"])).total_seconds()
        if age < 0 or age > control["max_age_hours"] * 3600:
            return "UNKNOWN", "Evidence timestamp is future-dated or stale", actual_hash
        satisfied = evaluate_facts(control["id"], data["facts"])
    except (ValueError, UnicodeError):
        return "UNKNOWN", "Evidence facts are malformed or incomplete", actual_hash
    return (
        ("SATISFIED", "Selected lab predicate satisfied", actual_hash)
        if satisfied
        else ("NOT_SATISFIED", "Selected lab predicate not satisfied", actual_hash)
    )


def assess(root: Path, as_of: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build deterministic control/risk assessments; resolved risks require fresh satisfied evidence and completed milestones."""
    instant = timestamp(as_of)
    bundle = load_bundle(root)
    evidence_by_control = {value["control_id"]: value for value in bundle["evidence"]}
    checks = []
    for control in sorted(bundle["controls"], key=lambda value: value["id"]):
        evidence = evidence_by_control.get(control["id"])
        state, reason, actual_hash = evidence_result(
            root, evidence, control, bundle["system"]["component_id"], as_of
        )
        checks.append(
            {
                "control_id": control["id"],
                "title": control["title"],
                "state": state,
                "reason": reason,
                "evidence_id": evidence["id"] if evidence else None,
                "observed_at": evidence["observed_at"] if evidence else None,
                "expected_sha256": evidence["sha256"] if evidence else None,
                "actual_sha256": actual_hash,
            }
        )
    by_control = {value["control_id"]: value for value in checks}
    risks = []
    for risk in sorted(bundle["risks"], key=lambda value: value["id"]):
        completed = timestamp(risk["completed_at"]) if risk["completed_at"] else None
        milestone_times = [
            timestamp(value["completed_at"]) if value["completed_at"] else None
            for value in risk["milestones"]
        ]
        if timestamp(risk["opened_at"]) > instant or any(
            value is not None and value > instant for value in milestone_times
        ):
            raise ValueError("risk or milestone is future-dated")
        if completed and (
            completed > instant
            or any(value is not None and value > completed for value in milestone_times)
        ):
            raise ValueError(
                "risk completion contradicts assessment/milestone chronology"
            )
        if risk["status"] == "resolved":
            check = by_control[risk["control_id"]]
            if (
                not completed
                or check["state"] != "SATISFIED"
                or any(value is None for value in milestone_times)
                or timestamp(check["observed_at"]) > completed
            ):
                raise ValueError(
                    "risk resolution lacks fresh satisfied evidence and completed milestones"
                )
        elif completed:
            raise ValueError("unresolved risk cannot claim a completed timestamp")
        risks.append(
            {
                "id": risk["id"],
                "control_id": risk["control_id"],
                "severity": risk["severity"],
                "status": risk["status"],
                "owner": risk["owner"],
                "due_at": risk["due_at"],
                "overdue": risk["status"] != "resolved"
                and instant > timestamp(risk["due_at"]),
                "pending_milestones": sum(value is None for value in milestone_times),
            }
        )
    result = {
        "schema": 1,
        "synthetic": True,
        "authorization": "NOT_GRANTED",
        "system_id": bundle["system"]["id"],
        "manifest_sha256": digest(canonical(bundle).encode()),
        "system_name": bundle["system"]["name"],
        "revision": bundle["revision"],
        "as_of": as_of,
        "checks": checks,
        "risks": risks,
        "summary": {
            state: sum(value["state"] == state for value in checks)
            for state in sorted(
                {"SATISFIED", "NOT_SATISFIED", "UNKNOWN", "INTEGRITY_ERROR"}
            )
        },
    }
    result["assessment_id"] = uid(canonical(result))
    return bundle, result
