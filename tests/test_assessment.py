"""Evidence-state, schema, chronology, scope and remediation-gate tests. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: AS_OF — line 58
# definition: test_baseline_and_remediation — line 61
# parameter: tmp_path — line 61
# parameter: workspace — line 61
# variable: _ — line 63
# variable: result — line 63
# variable: item — line 71
# variable: item — line 74
# variable: path — line 76
# variable: _ — line 78
# variable: fixed — line 78
# variable: item — line 80
# definition: test_evidence_edge_cases — line 95
# parameter: expected — line 95
# parameter: mode — line 95
# parameter: workspace — line 95
# variable: path — line 97
# variable: bundle — line 101
# variable: item — line 103
# variable: result — line 118
# variable: item — line 120
# definition: test_age_boundary_and_counters — line 125
# parameter: workspace — line 125
# variable: control — line 132
# variable: facts — line 132
# definition: test_manifest_rejection — line 169
# parameter: field — line 169
# parameter: workspace — line 169
# variable: bundle — line 171
# definition: test_resolution_gate — line 220
# parameter: mode — line 220
# parameter: tmp_path — line 220
# variable: root — line 222
# variable: bundle — line 224
# variable: risk — line 225
# variable: bundle — line 228
# definition: test_exact_account_predicate — line 252
# parameter: active — line 252
# parameter: reviewed — line 252
# END CODE MAP

from __future__ import annotations

import copy
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from rmf.assessment import assess, evaluate_facts, load_bundle
from rmf.contracts import uid
from scripts.examples import generate
from tests.conftest import change_evidence, change_manifest

AS_OF = "2026-10-12T12:00:00Z"


def test_baseline_and_remediation(workspace: Path, tmp_path: Path) -> None:
    """Known negative/unknown states persist; fresh evidence and completed milestones permit only lab risk closure."""
    _, result = assess(workspace, AS_OF)
    assert result["summary"] == {
        "SATISFIED": 3,
        "NOT_SATISFIED": 2,
        "UNKNOWN": 1,
        "INTEGRITY_ERROR": 0,
    }
    assert result["authorization"] == "NOT_GRANTED"
    assert not any(item["overdue"] for item in result["risks"])
    assert all(
        item["overdue"]
        for item in assess(workspace, "2026-10-12T12:00:01Z")[1]["risks"]
    )
    path = tmp_path / "fixed"
    generate(path, True)
    _, fixed = assess(path, "2026-10-13T12:00:00Z")
    assert fixed["summary"]["SATISFIED"] == 6
    assert all(item["status"] == "resolved" for item in fixed["risks"])


@pytest.mark.parametrize(
    "mode,expected",
    [
        ("missing", "UNKNOWN"),
        ("missing-record", "UNKNOWN"),
        ("tampered", "INTEGRITY_ERROR"),
        ("future", "UNKNOWN"),
        ("stale", "UNKNOWN"),
        ("wrong-scope", "INTEGRITY_ERROR"),
        ("malformed", "UNKNOWN"),
    ],
)
def test_evidence_edge_cases(workspace: Path, mode: str, expected: str) -> None:
    """Missing/invalid/stale evidence never counts as satisfaction; scope/digest failures are explicitly distinct."""
    path = workspace / "evidence/ac-2.json"
    if mode == "missing":
        path.unlink()
    elif mode == "missing-record":
        bundle = load_bundle(workspace)
        bundle["evidence"] = [
            item for item in bundle["evidence"] if item["control_id"] != "ac-2"
        ]
        change_manifest(workspace, bundle)
    elif mode == "tampered":
        path.write_bytes(path.read_bytes() + b" ")
    elif mode == "future":
        change_evidence(workspace, "ac-2", observed_at="2026-10-13T12:00:00Z")
    elif mode == "stale":
        change_evidence(workspace, "ac-2", observed_at="2026-10-01T12:00:00Z")
    elif mode == "wrong-scope":
        change_evidence(workspace, "ac-2", component_id=uid("outside"))
    else:
        change_evidence(
            workspace, "ac-2", facts={"active_accounts": True, "reviewed_accounts": 4}
        )
    result = assess(workspace, AS_OF)[1]
    assert (
        next(item for item in result["checks"] if item["control_id"] == "ac-2")["state"]
        == expected
    )


def test_age_boundary_and_counters(workspace: Path) -> None:
    """Freshness equality is included, 1 second later is stale; unsampled/zero denominators cannot prove completeness."""
    change_evidence(workspace, "ac-2", observed_at="2026-10-11T12:00:00Z")
    assert assess(workspace, AS_OF)[1]["checks"][0]["state"] == "SATISFIED"
    assert (
        assess(workspace, "2026-10-12T12:00:01Z")[1]["checks"][0]["state"] == "UNKNOWN"
    )
    for control, facts in [
        ("ac-2", {"active_accounts": 0, "reviewed_accounts": 0}),
        ("au-2", {"source_events": 0, "retained_events": 0}),
        ("ac-3", {"unauthorized_denied": 1, "cross_tenant_denied": True}),
        ("au-6", {"review_completed": "yes"}),
        ("cp-9", {"restore_verified": 1, "rpo_seconds": 0, "rto_seconds": 0}),
    ]:
        with pytest.raises(ValueError):
            evaluate_facts(control, facts)
    assert not evaluate_facts(
        "ac-3", {"unauthorized_denied": False, "cross_tenant_denied": True}
    )
    assert not evaluate_facts("au-6", {"review_completed": False})
    assert not evaluate_facts(
        "cp-9", {"restore_verified": True, "rpo_seconds": 301, "rto_seconds": 900}
    )


@pytest.mark.parametrize(
    "field",
    [
        "control-duplicate",
        "control-unknown",
        "component",
        "path",
        "digest",
        "evidence-duplicate",
        "risk-duplicate",
        "milestone-duplicate",
        "risk-state",
        "severity",
        "risk-date",
        "milestone-date",
        "control-age",
        "extra-field",
    ],
)
def test_manifest_rejection(workspace: Path, field: str) -> None:
    """Reject ambiguous manifests, outside-boundary references, unsupported states and invalid chronology."""
    bundle = load_bundle(workspace)
    if field == "control-duplicate":
        bundle["controls"].append(copy.deepcopy(bundle["controls"][0]))
    elif field == "control-unknown":
        bundle["controls"][0]["id"] = "unmapped-control"
    elif field == "component":
        bundle["evidence"][0]["component_id"] = uid("outside")
    elif field == "path":
        bundle["evidence"][0]["path"] = "../../private.json"
    elif field == "digest":
        bundle["evidence"][0]["sha256"] = "invalid"
    elif field == "evidence-duplicate":
        bundle["evidence"].append(copy.deepcopy(bundle["evidence"][0]))
    elif field == "risk-duplicate":
        bundle["risks"].append(copy.deepcopy(bundle["risks"][0]))
    elif field == "milestone-duplicate":
        bundle["risks"][1]["milestones"][0]["id"] = bundle["risks"][0]["milestones"][0][
            "id"
        ]
    elif field == "risk-state":
        bundle["risks"][0]["status"] = "approved"
    elif field == "severity":
        bundle["risks"][0]["severity"] = "arbitrary"
    elif field == "risk-date":
        bundle["risks"][0]["opened_at"] = "2026-11-01T00:00:00Z"
    elif field == "milestone-date":
        bundle["risks"][0]["milestones"][0]["due_at"] = "2026-09-01T00:00:00Z"
    elif field == "control-age":
        bundle["controls"][0]["max_age_hours"] = True
    else:
        bundle["private"] = "fictional secret not accepted"
    change_manifest(workspace, bundle)
    with pytest.raises(ValueError):
        load_bundle(workspace)


@pytest.mark.parametrize(
    "mode",
    [
        "claim-without-evidence",
        "missing-completion",
        "pending-milestone",
        "future",
        "after-risk",
        "unresolved-completion",
        "before-open",
        "milestone-before-open",
    ],
)
def test_resolution_gate(tmp_path: Path, mode: str) -> None:
    """Closing a lab risk requires coherent chronology, completed milestones and fresh satisfied evidence."""
    root = tmp_path / "fixed"
    generate(root, True)
    bundle = load_bundle(root)
    risk = bundle["risks"][0]
    if mode == "claim-without-evidence":
        change_evidence(root, risk["control_id"], facts={"review_completed": False})
        bundle = load_bundle(root)
    elif mode == "missing-completion":
        risk["completed_at"] = None
    elif mode == "pending-milestone":
        risk["milestones"][0]["completed_at"] = None
    elif mode == "future":
        risk["completed_at"] = "2026-10-14T12:00:00Z"
    elif mode == "after-risk":
        risk["milestones"][0]["completed_at"] = "2026-10-13T11:45:00Z"
    elif mode == "unresolved-completion":
        risk["status"] = "open"
    elif mode == "before-open":
        risk["completed_at"] = "2026-09-01T00:00:00Z"
    else:
        risk["milestones"][0]["completed_at"] = "2026-09-01T00:00:00Z"
    change_manifest(root, bundle)
    with pytest.raises(ValueError):
        assess(root, "2026-10-13T12:00:00Z")


@given(
    st.integers(min_value=1, max_value=10000), st.integers(min_value=0, max_value=10000)
)
@settings(max_examples=150, deadline=None)
def test_exact_account_predicate(active: int, reviewed: int) -> None:
    """Randomized counts satisfy the selected review predicate iff every sampled active account is reviewed."""
    assert evaluate_facts(
        "ac-2", {"active_accounts": active, "reviewed_accounts": reviewed}
    ) is (active == reviewed)
