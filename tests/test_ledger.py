"""Real SQLite atomicity, query binding, immutable triggers and externally anchored chain tests. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_real_history_and_exclusive_creation — line 49
# parameter: tmp_path — line 49
# parameter: workspace — line 49
# variable: path — line 51
# variable: first — line 54
# variable: tip — line 55
# variable: fixed — line 56
# variable: second — line 58
# variable: receipt — line 59
# variable: different — line 72
# variable: key — line 76
# variable: value — line 76
# definition: test_triggers_and_corruption_detection — line 83
# parameter: tmp_path — line 83
# parameter: workspace — line 83
# variable: path — line 85
# variable: connection — line 88
# variable: sql — line 90
# definition: test_external_tip_and_unrelated_database — line 109
# parameter: tmp_path — line 109
# parameter: workspace — line 109
# variable: path — line 111
# variable: receipt — line 113
# variable: connection — line 116
# variable: other — line 128
# variable: connection — line 129
# definition: test_report_validation — line 149
# parameter: field — line 149
# parameter: workspace — line 149
# variable: report — line 151
# END CODE MAP

from __future__ import annotations

import copy
import sqlite3
from pathlib import Path

import pytest

from rmf.assessment import assess
from rmf.contracts import canonical, uid
from rmf.ledger import append, connect, create, history, validate_report, verify
from scripts.examples import generate


def test_real_history_and_exclusive_creation(workspace: Path, tmp_path: Path) -> None:
    """Append two actual assessments, verify the saved tip, preserve chronological history and bind state filters."""
    path = tmp_path / "evidence.db"
    create(path)
    assert verify(path)["snapshots"] == 0
    first = assess(workspace, "2026-10-12T12:00:00Z")[1]
    tip = append(path, first)["tip"]
    fixed = tmp_path / "fixed"
    generate(fixed, True)
    second = assess(fixed, "2026-10-13T12:00:00Z")[1]
    receipt = append(path, second, tip)
    assert verify(path, receipt["tip"])["snapshots"] == 2
    assert history(path) == [first, second]
    assert history(path, "NOT_SATISFIED") == [first]
    with pytest.raises(ValueError):
        history(path, "SATISFIED' OR 1=1--")
    with pytest.raises(FileExistsError):
        create(path)
    with pytest.raises(sqlite3.IntegrityError):
        append(path, second)
    assert verify(path)["snapshots"] == 2
    with pytest.raises(ValueError):
        append(path, first)
    different = copy.deepcopy(second)
    different["system_id"] = uid("different-system")
    different["assessment_id"] = uid(
        canonical(
            {key: value for key, value in different.items() if key != "assessment_id"}
        )
    )
    with pytest.raises(ValueError):
        append(path, different)


def test_triggers_and_corruption_detection(workspace: Path, tmp_path: Path) -> None:
    """Normal SQL updates are blocked; even a deliberate local-admin trigger bypass is detected by payload/derived checks."""
    path = tmp_path / "evidence.db"
    create(path)
    append(path, assess(workspace, "2026-10-12T12:00:00Z")[1])
    connection = connect(path, True)
    try:
        for sql in (
            "UPDATE snapshots SET hash='bad'",
            "DELETE FROM snapshots",
            "UPDATE findings SET state='SATISFIED'",
            "DELETE FROM findings",
        ):
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(sql)
        connection.execute("DROP TRIGGER findings_no_update")
        connection.execute(
            "UPDATE findings SET state='SATISFIED' WHERE control_id='cp-9'"
        )
        connection.commit()
    finally:
        connection.close()
    with pytest.raises(ValueError):
        verify(path)


def test_external_tip_and_unrelated_database(workspace: Path, tmp_path: Path) -> None:
    """Internal consistency alone cannot detect deleted history; an independently retained tip detects truncation."""
    path = tmp_path / "evidence.db"
    create(path)
    receipt = append(path, assess(workspace, "2026-10-12T12:00:00Z")[1])
    with pytest.raises(ValueError):
        verify(path, "0" * 64)
    connection = connect(path, True)
    try:
        connection.execute("DROP TRIGGER findings_no_delete")
        connection.execute("DROP TRIGGER snapshots_no_delete")
        connection.execute("DELETE FROM findings")
        connection.execute("DELETE FROM snapshots")
        connection.commit()
    finally:
        connection.close()
    assert verify(path)["snapshots"] == 0
    with pytest.raises(ValueError):
        verify(path, receipt["tip"])
    other = tmp_path / "unrelated.db"
    connection = sqlite3.connect(other)
    connection.close()
    with pytest.raises(ValueError):
        connect(other)
    with pytest.raises(ValueError):
        connect(tmp_path / "missing.db")


@pytest.mark.parametrize(
    "field",
    [
        "synthetic",
        "authorization",
        "state",
        "summary",
        "id",
        "reference",
        "risk-status",
    ],
)
def test_report_validation(workspace: Path, field: str) -> None:
    """Normalized reports cannot conceal contradictory state/counts, identities, references or authorization claims."""
    report = assess(workspace, "2026-10-12T12:00:00Z")[1]
    if field == "synthetic":
        report["synthetic"] = False
    elif field == "authorization":
        report["authorization"] = "APPROVED"
    elif field == "state":
        report["checks"][0]["state"] = "MAYBE"
    elif field == "summary":
        report["summary"]["UNKNOWN"] = 999
    elif field == "id":
        report["assessment_id"] = uid("not-content")
    elif field == "reference":
        report["risks"][0]["control_id"] = "outside"
    else:
        report["risks"][0]["status"] = "approved"
    with pytest.raises(ValueError):
        validate_report(report)
