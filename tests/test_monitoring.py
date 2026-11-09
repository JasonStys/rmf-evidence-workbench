"""Independent calendar expectations across freshness, scope, remediation and safe exports. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: AS_OF — line 56
# definition: test_selected_scope_independent_counts_and_no_mutation — line 59
# parameter: workspace — line 59
# variable: before — line 61
# variable: p — line 61
# variable: result — line 62
# variable: e — line 63
# variable: e — line 71
# variable: e — line 75
# variable: e — line 77
# variable: p — line 79
# definition: test_boundary_and_overdue_are_not_technical_regressions — line 84
# parameter: workspace — line 84
# variable: boundary — line 86
# variable: refresh — line 87
# variable: e — line 88
# variable: e — line 90
# variable: expired — line 91
# variable: e — line 93
# variable: e — line 96
# definition: test_resolved_risks_omit_work_without_omitting_freshness — line 101
# parameter: tmp_path — line 101
# variable: fixed — line 103
# variable: result — line 105
# variable: e — line 107
# definition: test_tampered_evidence_has_immediate_integrity_task — line 112
# parameter: workspace — line 112
# variable: events — line 115
# variable: e — line 116
# definition: test_bounded_explicit_horizon — line 126
# parameter: hours — line 126
# parameter: workspace — line 126
# definition: test_safe_exports_and_actual_cli — line 132
# parameter: tmp_path — line 132
# parameter: workspace — line 132
# variable: manifest — line 134
# variable: target — line 138
# variable: completed — line 139
# variable: before — line 163
# END CODE MAP

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

from rmf.monitoring import calendar, publish
from scripts.examples import generate
from tests.conftest import change_manifest

AS_OF = "2026-10-12T12:00:00Z"


def test_selected_scope_independent_counts_and_no_mutation(workspace: Path):
    """The known six-check baseline has fourteen distinct work items, not an inferred authorization."""
    before = {str(p): p.read_bytes() for p in workspace.rglob("*") if p.is_file()}
    result = calendar(workspace, AS_OF)
    assert Counter(e["kind"] for e in result["events"]) == {
        "evidence_refresh_boundary": 5,
        "milestone_due": 3,
        "risk_due": 3,
        "predicate_remediation_review": 2,
        "evidence_gap": 1,
    }
    assert result["authorization"] == "NOT_GRANTED"
    assert len({e["id"] for e in result["events"]}) == 14
    assert all(
        e["system_id"] == result["system_id"]
        and e["component_id"] == result["component_id"]
        for e in result["events"]
    )
    assert any(e["owner"] == "UNASSIGNED evidence owner" for e in result["events"])
    assert before == {
        str(p): p.read_bytes() for p in workspace.rglob("*") if p.is_file()
    }
    assert result == calendar(workspace, AS_OF)


def test_boundary_and_overdue_are_not_technical_regressions(workspace: Path):
    """Fresh at the exact boundary, unknown one second later; unresolved deadlines remain overdue."""
    boundary = calendar(workspace, "2026-10-13T11:00:00Z", 1)
    refresh = [
        e for e in boundary["events"] if e["kind"] == "evidence_refresh_boundary"
    ]
    assert len(refresh) == 5 and {e["timing"] for e in refresh} == {"DUE_NOW"}
    expired = calendar(workspace, "2026-10-13T11:00:01Z", 1)
    assert expired["assessment_summary"]["UNKNOWN"] == 6
    assert Counter(e["kind"] for e in expired["events"])["evidence_gap"] == 6
    assert all(
        e["timing"] == "OVERDUE"
        for e in expired["events"]
        if e["kind"] in ("risk_due", "milestone_due")
    )


def test_resolved_risks_omit_work_without_omitting_freshness(tmp_path: Path):
    """Resolved synthetic checks retain six refresh deadlines and no remediation/risk/milestone task."""
    fixed = tmp_path / "fixed"
    generate(fixed, True)
    result = calendar(fixed, "2026-10-13T12:00:00Z")
    assert len(result["events"]) == 6
    assert {e["kind"] for e in result["events"]} == {"evidence_refresh_boundary"}
    assert not calendar(fixed, "2026-10-13T12:00:00Z", 1)["events"]
    assert result["authorization"] == "NOT_GRANTED"


def test_tampered_evidence_has_immediate_integrity_task(workspace: Path):
    """Digest failure is not a misleading future refresh or satisfied control."""
    (workspace / "evidence/ac-2.json").write_text("{}")
    events = [
        e for e in calendar(workspace, AS_OF)["events"] if e["control_id"] == "ac-2"
    ]
    assert (
        len(events) == 1
        and events[0]["kind"] == "integrity_review"
        and events[0]["timing"] == "DUE_NOW"
    )


@pytest.mark.parametrize("hours", [0, 169, True, 1.5])
def test_bounded_explicit_horizon(workspace: Path, hours):
    """Reject coerced and unbounded review horizons before creating any output."""
    with pytest.raises(ValueError):
        calendar(workspace, AS_OF, hours)


def test_safe_exports_and_actual_cli(workspace: Path, tmp_path: Path):
    """Real CLI writes new files; escaped HTML and neutral CSV do not execute owner/milestone strings."""
    manifest = json.loads((workspace / "bundle.json").read_text())
    manifest["risks"][0]["owner"] = '=HYPERLINK("https://invalid")'
    manifest["risks"][0]["milestones"][0]["description"] = "<script>alert(1)</script>"
    change_manifest(workspace, manifest)
    target = tmp_path / "calendar"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "rmf",
            "calendar",
            str(workspace),
            "--as-of",
            AS_OF,
            "--output",
            str(target),
        ],
        text=True,
        capture_output=True,
        timeout=20,
    )
    assert completed.returncode == 0, completed.stdout
    assert json.loads(completed.stdout) == {
        "events": 14,
        "authorization": "NOT_GRANTED",
    }
    assert "<script>" not in (target / "calendar.html").read_text()
    assert "&lt;script&gt;" in (target / "calendar.html").read_text()
    assert "'=" in (target / "calendar.csv").read_text()
    before = (target / "calendar.json").read_bytes()
    with pytest.raises(FileExistsError):
        publish(calendar(workspace, AS_OF), target)
    assert (target / "calendar.json").read_bytes() == before
