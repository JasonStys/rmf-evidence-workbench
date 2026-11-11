"""Real SQLite atomicity, query binding, immutable triggers and externally anchored chain tests. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_real_history_and_exclusive_creation — line 58
# parameter: tmp_path — line 58
# parameter: workspace — line 58
# variable: path — line 60
# variable: first — line 63
# variable: tip — line 64
# variable: fixed — line 65
# variable: second — line 67
# variable: receipt — line 68
# variable: different — line 81
# variable: key — line 85
# variable: value — line 85
# definition: test_triggers_and_corruption_detection — line 92
# parameter: tmp_path — line 92
# parameter: workspace — line 92
# variable: path — line 94
# variable: connection — line 97
# variable: sql — line 99
# definition: test_external_tip_and_unrelated_database — line 118
# parameter: tmp_path — line 118
# parameter: workspace — line 118
# variable: path — line 120
# variable: receipt — line 122
# variable: connection — line 125
# variable: other — line 137
# variable: connection — line 138
# definition: test_spoofed_application_id_cannot_authorize_query_heavy_views — line 146
# parameter: tmp_path — line 147
# variable: path — line 150
# variable: database — line 153
# variable: original — line 162
# definition: test_imported_database_value_and_work_limits_are_actual_sqlite_limits — line 168
# parameter: tmp_path — line 169
# variable: path — line 172
# variable: connection — line 174
# definition: test_report_validation — line 199
# parameter: field — line 199
# parameter: workspace — line 199
# variable: report — line 201
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


def test_spoofed_application_id_cannot_authorize_query_heavy_views(
    tmp_path: Path,
) -> None:
    """A real SQLite file with the expected application marker must not evaluate an imported recursive view."""
    path = tmp_path / "spoofed.sqlite"
    from contextlib import closing

    with closing(sqlite3.connect(path)) as database, database:
        database.executescript("""
            PRAGMA application_id = 1380795905;
            CREATE TABLE findings(snapshot_seq,control_id,state);
            CREATE VIEW snapshots AS
              WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM n)
              SELECT x AS seq, '' AS payload, '' AS previous_hash, '' AS hash,
                '' AS assessment_id, '' AS as_of FROM n;
        """)
    original = path.read_bytes()
    with pytest.raises(ValueError, match="ordinary"):
        verify(path)
    assert path.read_bytes() == original


def test_imported_database_value_and_work_limits_are_actual_sqlite_limits(
    tmp_path: Path,
) -> None:
    """A connection refuses an oversized generated cell and interrupts real excessive query work without execution plugins."""
    path = tmp_path / "limited.sqlite"
    create(path)
    connection = connect(path)
    try:
        with pytest.raises(sqlite3.DataError, match="too big"):
            connection.execute("SELECT zeroblob(3*1024*1024)").fetchone()
        with pytest.raises(sqlite3.OperationalError, match="interrupted"):
            connection.execute("""
                WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM n WHERE x<100000000)
                SELECT sum(x) FROM n
            """).fetchone()
    finally:
        connection.close()


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
