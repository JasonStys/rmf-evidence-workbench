"""Transactional parameterized SQLite snapshots with integrity chains and explicit trust limits. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 106
# variable: ZERO — line 107
# definition: validate_report — line 110
# parameter: value — line 110
# variable: report — line 112
# variable: controls — line 141
# variable: raw — line 142
# variable: check — line 143
# variable: control_id — line 156
# variable: state — line 157
# variable: field — line 167
# variable: state — line 174
# variable: check — line 176
# variable: risks — line 179
# variable: raw — line 180
# variable: risk — line 181
# variable: identity — line 194
# variable: key — line 207
# variable: original — line 207
# variable: value — line 207
# definition: create — line 213
# parameter: path — line 213
# variable: connection — line 218
# definition: connect — line 226
# parameter: path — line 226
# parameter: writable — line 226
# variable: mode — line 234
# variable: connection — line 235
# variable: remaining — line 240
# definition: bounded_work — line 242
# variable: remaining — line 245
# variable: tables — line 253
# variable: _ — line 260
# variable: kind — line 260
# variable: sql — line 260
# definition: verify_connection — line 269
# parameter: connection — line 270
# parameter: expected_tip — line 270
# variable: rows — line 273
# variable: previous — line 278
# variable: system — line 279
# variable: last_as_of — line 280
# variable: expected_sequence — line 281
# variable: sequence — line 282
# variable: payload — line 283
# variable: parent — line 284
# variable: stored — line 285
# variable: assessment_id — line 286
# variable: recorded_time — line 287
# variable: report — line 289
# variable: actual — line 305
# variable: expected — line 309
# variable: check — line 310
# variable: last_as_of — line 314
# variable: previous — line 314
# variable: system — line 314
# definition: verify — line 326
# parameter: expected_tip — line 326
# parameter: path — line 326
# variable: connection — line 328
# definition: append — line 335
# parameter: expected_tip — line 336
# parameter: path — line 336
# parameter: result — line 336
# variable: connection — line 340
# variable: state — line 343
# variable: previous — line 346
# variable: last — line 350
# variable: payload — line 359
# variable: sequence — line 360
# variable: tip — line 361
# variable: check — line 377
# definition: history — line 393
# parameter: path — line 393
# parameter: state — line 393
# variable: connection — line 397
# variable: rows — line 401
# variable: rows — line 405
# variable: row — line 409
# END CODE MAP

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any

from rmf.contracts import (
    MAX_BYTES,
    STATES,
    array,
    canonical,
    digest,
    identifier,
    integer,
    obj,
    parse_json,
    text,
    timestamp,
    uid,
)

ROOT = Path(__file__).resolve().parents[1]
ZERO = "0" * 64


def validate_report(value: object) -> dict[str, Any]:
    """Validate a normalized report before persistence/comparison; summaries and content-derived identity must agree."""
    report = obj(
        value,
        {
            "schema",
            "synthetic",
            "authorization",
            "system_id",
            "system_name",
            "revision",
            "as_of",
            "checks",
            "risks",
            "summary",
            "assessment_id",
            "manifest_sha256",
        },
    )
    integer(report["schema"], 1, 1)
    if report["synthetic"] is not True or report["authorization"] != "NOT_GRANTED":
        raise ValueError("report must remain educational and unauthorized")
    identifier(report["system_id"])
    text(report["system_name"], 120)
    identifier(report["assessment_id"])
    if not isinstance(report["manifest_sha256"], str) or not re.fullmatch(
        r"[0-9a-f]{64}", report["manifest_sha256"]
    ):
        raise ValueError("source manifest fingerprint required")
    integer(report["revision"], 1, 100_000)
    timestamp(report["as_of"])
    controls: set[str] = set()
    for raw in array(report["checks"], 1):
        check = obj(
            raw,
            {
                "control_id",
                "title",
                "state",
                "reason",
                "evidence_id",
                "observed_at",
                "expected_sha256",
                "actual_sha256",
            },
        )
        control_id = text(check["control_id"], 32)
        state = text(check["state"], 32)
        if control_id in controls or state not in STATES:
            raise ValueError("duplicate control or unsupported finding state")
        controls.add(control_id)
        text(check["title"], 120)
        text(check["reason"])
        if check["evidence_id"] is not None:
            identifier(check["evidence_id"])
        if check["observed_at"] is not None:
            timestamp(check["observed_at"])
        for field in ("expected_sha256", "actual_sha256"):
            if check[field] is not None and (
                not isinstance(check[field], str)
                or not re.fullmatch(r"[0-9a-f]{64}", check[field])
            ):
                raise ValueError("evidence fingerprint malformed")
    obj(report["summary"], STATES)
    for state in STATES:
        if integer(report["summary"][state], 0, 1000) != sum(
            check["state"] == state for check in report["checks"]
        ):
            raise ValueError("summary differs from detailed checks")
    risks: set[str] = set()
    for raw in array(report["risks"]):
        risk = obj(
            raw,
            {
                "id",
                "control_id",
                "severity",
                "status",
                "owner",
                "due_at",
                "overdue",
                "pending_milestones",
            },
        )
        identity = identifier(risk["id"])
        if identity in risks or text(risk["control_id"], 32) not in controls:
            raise ValueError("duplicate or dangling report risk")
        risks.add(identity)
        if (
            text(risk["severity"], 32) not in {"low", "moderate", "high"}
            or text(risk["status"], 32) not in {"open", "in-progress", "resolved"}
            or type(risk["overdue"]) is not bool
        ):
            raise ValueError("invalid report risk fields")
        text(risk["owner"], 120)
        timestamp(risk["due_at"])
        integer(risk["pending_milestones"], 0, 1000)
    original = {key: value for key, value in report.items() if key != "assessment_id"}
    if report["assessment_id"] != uid(canonical(original)):
        raise ValueError("report content identity mismatch")
    return report


def create(path: Path) -> None:
    """Create a new owned evidence database only; never overwrite an existing file or import user SQL."""
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    with path.open("xb"):
        pass
    connection = sqlite3.connect(path)
    try:
        connection.executescript((ROOT / "ops/schema.sql").read_text(encoding="utf-8"))
        connection.commit()
    finally:
        connection.close()


def connect(path: Path, writable: bool = False) -> sqlite3.Connection:
    """Open an existing ordinary lab database in explicit ro/rw mode; refuse unrelated database application IDs."""
    if (
        path.is_symlink()
        or not path.is_file()
        or path.stat().st_size > 256 * 1024 * 1024
    ):
        raise ValueError("bounded ordinary existing database required")
    mode = "rw" if writable else "ro"
    connection = sqlite3.connect(
        path.resolve().as_uri() + "?mode=" + mode, uri=True, timeout=5
    )
    try:
        connection.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, MAX_BYTES + 8192)
        remaining = 20_000

        def bounded_work() -> int:
            """Interrupt after at most twenty million VM instructions per connection, including imported metadata queries."""
            nonlocal remaining
            remaining -= 1
            return int(remaining <= 0)

        connection.set_progress_handler(bounded_work, 1000)
        connection.execute("PRAGMA trusted_schema = OFF")
        connection.execute("PRAGMA foreign_keys = ON")
        if connection.execute("PRAGMA application_id").fetchone()[0] != 0x524D4601:
            raise ValueError("database is not an RMF workbench ledger")
        tables = connection.execute(
            "SELECT name,type,sql FROM sqlite_schema WHERE name IN ('snapshots','findings')"
        ).fetchall()
        if len(tables) != 2 or any(
            kind != "table"
            or not isinstance(sql, str)
            or re.match(r"\s*CREATE\s+VIRTUAL\b", sql, re.I)
            for _, kind, sql in tables
        ):
            raise ValueError("ledger requires ordinary snapshot and finding tables")
    except BaseException:
        connection.close()
        raise
    return connection


def verify_connection(
    connection: sqlite3.Connection, expected_tip: str | None = None
) -> dict[str, Any]:
    """Verify each payload/derived row and chain link; external expected_tip detects truncation, not just internal corruption."""
    rows = connection.execute(
        "SELECT seq,payload,previous_hash,hash,assessment_id,as_of FROM snapshots ORDER BY seq LIMIT 1001"
    ).fetchall()
    if len(rows) > 1000:
        raise ValueError("snapshot cap exceeded")
    previous = ZERO
    system = None
    last_as_of = None
    for expected_sequence, (
        sequence,
        payload,
        parent,
        stored,
        assessment_id,
        recorded_time,
    ) in enumerate(rows, 1):
        report = validate_report(parse_json(payload.encode("utf-8")))
        if (
            sequence != expected_sequence
            or report["assessment_id"] != assessment_id
            or report["as_of"] != recorded_time
            or parent != previous
            or stored != digest(f"{sequence}\n{parent}\n{payload}".encode())
        ):
            raise ValueError("ledger chain is inconsistent")
        if (
            system is not None
            and system != report["system_id"]
            or last_as_of is not None
            and timestamp(report["as_of"]) < timestamp(last_as_of)
        ):
            raise ValueError("ledger system or chronology changed")
        actual = connection.execute(
            "SELECT control_id,state FROM findings WHERE snapshot_seq=? ORDER BY control_id",
            (sequence,),
        ).fetchall()
        expected = sorted(
            (check["control_id"], check["state"]) for check in report["checks"]
        )
        if actual != expected:
            raise ValueError("derived findings differ from hashed evidence")
        system, last_as_of, previous = report["system_id"], report["as_of"], stored
    if expected_tip is not None and expected_tip != previous:
        raise ValueError("ledger does not match the independently supplied chain tip")
    return {
        "snapshots": len(rows),
        "tip": previous,
        "assurance": "EXTERNAL_TIP_MATCH"
        if expected_tip is not None
        else "UNANCHORED_LOCAL_CHAIN",
    }


def verify(path: Path, expected_tip: str | None = None) -> dict[str, Any]:
    """Perform read-only verification; an unsigned local hash chain is not proof of collector identity/authenticity."""
    connection = connect(path)
    try:
        return verify_connection(connection, expected_tip)
    finally:
        connection.close()


def append(
    path: Path, result: dict[str, Any], expected_tip: str | None = None
) -> dict[str, Any]:
    """Append one validated point-in-time snapshot atomically after verifying the existing chain under a write lock."""
    validate_report(result)
    connection = connect(path, writable=True)
    try:
        connection.execute("BEGIN IMMEDIATE")
        state = verify_connection(connection, expected_tip)
        if state["snapshots"] >= 1000:
            raise ValueError("ledger snapshot cap reached")
        previous = connection.execute(
            "SELECT payload FROM snapshots ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        if previous:
            last = parse_json(previous[0].encode())
            if (
                last["system_id"] != result["system_id"]
                or timestamp(last["as_of"]) > timestamp(result["as_of"])
                or last["revision"] > result["revision"]
            ):
                raise ValueError(
                    "cannot append a different system or rolled-back snapshot"
                )
        payload = canonical(result)
        sequence = state["snapshots"] + 1
        tip = digest(f"{sequence}\n{state['tip']}\n{payload}".encode())
        connection.execute(
            "INSERT INTO snapshots(seq,assessment_id,as_of,payload,previous_hash,hash) VALUES (?,?,?,?,?,?)",
            (
                sequence,
                result["assessment_id"],
                result["as_of"],
                payload,
                state["tip"],
                tip,
            ),
        )
        connection.executemany(
            "INSERT INTO findings(snapshot_seq,control_id,state) VALUES (?,?,?)",
            [
                (sequence, check["control_id"], check["state"])
                for check in result["checks"]
            ],
        )
        connection.commit()
        return {
            "snapshots": sequence,
            "tip": tip,
            "assurance": "SAVE_TIP_SEPARATELY_FOR_TRUNCATION_DETECTION",
        }
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()


def history(path: Path, state: str | None = None) -> list[dict[str, Any]]:
    """Return verified bounded chronological snapshots; optional state filtering uses bind parameters, never SQL text."""
    if state is not None and state not in STATES:
        raise ValueError("unsupported state filter")
    connection = connect(path)
    try:
        verify_connection(connection)
        if state is None:
            rows = connection.execute(
                "SELECT seq,payload FROM snapshots ORDER BY seq"
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT DISTINCT snapshots.seq,snapshots.payload FROM snapshots JOIN findings ON snapshot_seq=seq WHERE state=? ORDER BY seq",
                (state,),
            ).fetchall()
        return [parse_json(row[1].encode()) for row in rows]
    finally:
        connection.close()
