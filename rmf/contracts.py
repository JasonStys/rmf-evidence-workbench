"""Closed bounded evidence contracts and safe local reads. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: MAX_BYTES — line 76
# variable: MAX_ITEMS — line 77
# variable: STATES — line 78
# variable: NAMESPACE — line 79
# definition: identifier — line 82
# parameter: value — line 82
# variable: parsed — line 86
# definition: uid — line 92
# parameter: label — line 92
# definition: timestamp — line 97
# parameter: value — line 97
# definition: text — line 106
# parameter: limit — line 106
# parameter: value — line 106
# variable: character — line 114
# definition: integer — line 121
# parameter: maximum — line 121
# parameter: minimum — line 121
# parameter: value — line 121
# definition: obj — line 128
# parameter: fields — line 128
# parameter: value — line 128
# definition: array — line 135
# parameter: minimum — line 135
# parameter: value — line 135
# definition: unique_object — line 142
# parameter: pairs — line 142
# variable: result — line 144
# variable: key — line 145
# variable: value — line 145
# definition: parse_json — line 152
# parameter: content — line 152
# variable: value — line 157
# variable: pending — line 164
# variable: nodes — line 165
# variable: current — line 167
# variable: depth — line 167
# variable: nodes — line 168
# variable: item — line 172
# variable: item — line 174
# definition: reject_constant — line 178
# parameter: value — line 178
# definition: safe_bytes — line 183
# parameter: relative — line 183
# parameter: root — line 183
# variable: part — line 186
# variable: base — line 189
# variable: candidate — line 190
# variable: part — line 191
# variable: candidate — line 192
# variable: info — line 193
# variable: stream — line 202
# variable: info — line 203
# variable: content — line 206
# definition: canonical — line 212
# parameter: value — line 212
# definition: digest — line 219
# parameter: content — line 219
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
    with candidate.open("rb") as stream:
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
