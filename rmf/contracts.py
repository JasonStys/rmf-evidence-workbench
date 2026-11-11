"""Closed bounded evidence contracts and safe local reads. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: MAX_BYTES — line 77
# variable: MAX_ITEMS — line 78
# variable: STATES — line 79
# variable: NAMESPACE — line 80
# definition: identifier — line 83
# parameter: value — line 83
# variable: parsed — line 87
# definition: uid — line 93
# parameter: label — line 93
# definition: timestamp — line 98
# parameter: value — line 98
# definition: text — line 107
# parameter: limit — line 107
# parameter: value — line 107
# variable: character — line 115
# definition: integer — line 122
# parameter: maximum — line 122
# parameter: minimum — line 122
# parameter: value — line 122
# definition: obj — line 129
# parameter: fields — line 129
# parameter: value — line 129
# definition: array — line 136
# parameter: minimum — line 136
# parameter: value — line 136
# definition: unique_object — line 143
# parameter: pairs — line 143
# variable: result — line 145
# variable: key — line 146
# variable: value — line 146
# definition: parse_json — line 153
# parameter: content — line 153
# variable: value — line 158
# variable: pending — line 165
# variable: nodes — line 166
# variable: current — line 168
# variable: depth — line 168
# variable: nodes — line 169
# variable: item — line 173
# variable: item — line 175
# definition: reject_constant — line 179
# parameter: value — line 179
# definition: safe_bytes — line 184
# parameter: relative — line 184
# parameter: root — line 184
# variable: part — line 187
# variable: base — line 190
# variable: candidate — line 191
# variable: part — line 192
# variable: candidate — line 193
# variable: info — line 194
# variable: descriptor — line 203
# variable: stream — line 210
# variable: info — line 211
# variable: content — line 214
# definition: canonical — line 220
# parameter: value — line 220
# definition: digest — line 227
# parameter: content — line 227
# END CODE MAP

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import unicodedata
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

MAX_BYTES = 2 * 1024 * 1024
MAX_ITEMS = 1000
STATES = {"SATISFIED", "NOT_SATISFIED", "UNKNOWN", "INTEGRITY_ERROR"}
NAMESPACE = uuid.UUID("6a11b4cd-6f31-5b49-8c05-05735e979260")


def identifier(value: object) -> str:
    """Require canonical nonzero lower-case UUIDs; return the original validated string."""
    if not isinstance(value, str):
        raise ValueError("UUID string required")
    parsed = uuid.UUID(value)
    if str(parsed) != value or parsed.int == 0:
        raise ValueError("canonical nonzero UUID required")
    return value


def uid(label: str) -> str:
    """Create a deterministic UUID for a fictional entity or content-addressed document revision."""
    return str(uuid.uuid5(NAMESPACE, label))


def timestamp(value: object) -> datetime:
    """Require canonical UTC second-resolution RFC3339, rejecting ambiguous local times and malformed dates."""
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value
    ):
        raise ValueError("UTC timestamp required")
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)


def text(value: object, limit: int = 1000) -> str:
    """Require nonempty bounded printable text; reject terminal controls while preserving markup as inert data."""
    if (
        not isinstance(value, str)
        or not 1 <= len(value) <= limit
        or not value.strip()
        or any(
            unicodedata.category(character) in {"Cc", "Cf", "Cs", "Zl", "Zp"}
            for character in value
        )
    ):
        raise ValueError("bounded printable text required")
    return value


def integer(value: object, minimum: int = 0, maximum: int = 1_000_000) -> int:
    """Require an exact bounded integer and exclude bool/string/float coercion."""
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError("bounded integer required")
    return value


def obj(value: object, fields: set[str]) -> dict[str, Any]:
    """Require exactly the expected record keys; reject extras instead of silently retaining private fields."""
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError("closed record fields do not match")
    return value


def array(value: object, minimum: int = 0) -> list[Any]:
    """Require a bounded list, not a scalar or unbounded evidence/control collection."""
    if not isinstance(value, list) or not minimum <= len(value) <= MAX_ITEMS:
        raise ValueError("bounded array required")
    return value


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON keys rather than accepting attacker-chosen shadow values."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def parse_json(content: bytes) -> Any:
    """Decode bounded UTF-8 JSON data without code execution; reject nonstandard numeric constants."""
    if len(content) > MAX_BYTES:
        raise ValueError("JSON byte cap exceeded")
    try:
        value = json.loads(
            content.decode("utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except RecursionError as error:
        raise ValueError("JSON nesting exceeds parser limits") from error
    pending = [(value, 0)]
    nodes = 0
    while pending:
        current, depth = pending.pop()
        nodes += 1
        if depth > 32 or nodes > 50_000:
            raise ValueError("JSON structural cap exceeded")
        if isinstance(current, dict):
            pending.extend((item, depth + 1) for item in current.values())
        elif isinstance(current, list):
            pending.extend((item, depth + 1) for item in current)
    return value


def reject_constant(value: str) -> None:
    """Reject JSON NaN/Infinity tokens; value is intentionally not included in errors/logs."""
    raise ValueError("nonstandard JSON constant")


def safe_bytes(root: Path, relative: str) -> bytes:
    """Read a bounded ordinary local file beneath root; reject traversal, links/reparse points and special files."""
    if not re.fullmatch(r"(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_.-]+", relative) or any(
        part in {".", ".."} for part in relative.split("/")
    ):
        raise ValueError("unsafe local reference")
    base = root.resolve(strict=True)
    candidate = base
    for part in relative.split("/"):
        candidate = candidate / part
        info = candidate.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(
            info, "st_file_attributes", 0
        ) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
            raise ValueError("linked evidence is not supported")
    if not candidate.resolve(strict=True).is_relative_to(base):
        raise ValueError("evidence escaped workspace")
    if not stat.S_ISREG(info.st_mode):
        raise ValueError("ordinary evidence file required")
    descriptor = os.open(
        candidate,
        os.O_RDONLY
        | getattr(os, "O_NONBLOCK", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_BINARY", 0),
    )
    with os.fdopen(descriptor, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_BYTES:
            raise ValueError("bounded ordinary evidence file required")
        content = stream.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        raise ValueError("evidence byte cap exceeded")
    return content


def canonical(value: object) -> str:
    """Serialize deterministic finite JSON for revision IDs and chain hashing; it is not a digital signature."""
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False, ensure_ascii=True
    )


def digest(content: bytes) -> str:
    """Return SHA-256 of exact bytes for evidence-integrity checks against a separately trusted manifest."""
    return hashlib.sha256(content).hexdigest()
