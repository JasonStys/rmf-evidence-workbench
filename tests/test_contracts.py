"""Bounded parser/file/identifier and terminal privacy boundary tests. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_integer — line 45
# parameter: value — line 45
# definition: test_uuid — line 61
# parameter: value — line 61
# definition: test_timestamp — line 71
# parameter: value — line 71
# definition: test_printable_text — line 80
# parameter: value — line 80
# definition: test_parser — line 108
# parameter: content — line 108
# definition: test_collections_and_node_cap — line 114
# definition: test_paths — line 137
# parameter: relative — line 137
# parameter: tmp_path — line 137
# definition: test_ordinary_file_and_link_guards — line 143
# parameter: tmp_path — line 143
# variable: source — line 145
# END CODE MAP

from __future__ import annotations

import stat
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from rmf.contracts import (
    MAX_BYTES,
    array,
    identifier,
    integer,
    obj,
    parse_json,
    safe_bytes,
    text,
    timestamp,
)


@pytest.mark.parametrize("value", [True, False, "1", 1.2, -1, 1_000_001, None])
def test_integer(value: object) -> None:
    """Strict unit counts never accept bools, floats, strings or values outside supported bounds."""
    with pytest.raises(ValueError):
        integer(value)


@pytest.mark.parametrize(
    "value",
    [
        None,
        "0" * 32,
        "00000000-0000-0000-0000-000000000000",
        "NOT-A-UUID",
        "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA",
    ],
)
def test_uuid(value: object) -> None:
    """UUIDs are canonical nonzero strings, not identity credentials or arbitrary raw identifiers."""
    with pytest.raises(ValueError):
        identifier(value)


@pytest.mark.parametrize(
    "value",
    [None, "", "2026-10-13", "2026-02-30T12:00:00Z", "2026-10-13T12:00:00+00:00"],
)
def test_timestamp(value: object) -> None:
    """Only canonical UTC calendar timestamps enter deadline/freshness calculations."""
    with pytest.raises(ValueError):
        timestamp(value)


@pytest.mark.parametrize(
    "value", [None, "", " ", "x" * 1001, "secret\x1b[31m", "Fictional\u202espoof"]
)
def test_printable_text(value: object) -> None:
    """Reject terminal controls, bidi formatting and unbounded labels; markup remains inert escaped data."""
    with pytest.raises(ValueError):
        text(value)
    assert text("<script>fictional</script>") == "<script>fictional</script>"


@pytest.mark.parametrize(
    "content",
    [
        b'{"key":1,"key":2}',
        b'{"key":NaN}',
        b"\xff",
        b"not JSON",
        b"[" * 40 + b"0" + b"]" * 40,
        b"[" * 1100 + b"0" + b"]" * 1100,
        b"x" * (MAX_BYTES + 1),
    ],
    ids=[
        "duplicate-key",
        "nonfinite",
        "utf8",
        "malformed",
        "depth",
        "recursion",
        "byte-cap",
    ],
)
def test_parser(content: bytes) -> None:
    """Ambiguous/deep/oversized/nonstandard input is rejected without executing or logging its content."""
    with pytest.raises((ValueError, UnicodeError)):
        parse_json(content)


def test_collections_and_node_cap() -> None:
    """Bound collection and parse-tree work rather than relying only on file size."""
    with pytest.raises(ValueError):
        obj({}, {"required"})
    with pytest.raises(ValueError):
        array("not-list")
    with pytest.raises(ValueError):
        array([0] * 1001)
    with pytest.raises(ValueError):
        parse_json(b"[" + b"0," * 50000 + b"0]")


@pytest.mark.parametrize(
    "relative",
    [
        "../private",
        "/absolute",
        "C:/private",
        "https://example.com/file",
        "a\\b",
        "./example.json",
    ],
)
def test_paths(tmp_path: Path, relative: str) -> None:
    """Relative local references cannot turn into traversal, URLs or platform-specific absolute filenames."""
    with pytest.raises(ValueError):
        safe_bytes(tmp_path, relative)


def test_ordinary_file_and_link_guards(tmp_path: Path) -> None:
    """Read actual regular bounded files; reject synthetic link/reparse/special-file metadata without needing admin rights."""
    source = tmp_path / "file.json"
    source.write_bytes(b"{}")
    assert safe_bytes(tmp_path, "file.json") == b"{}"
    with patch.object(
        Path,
        "lstat",
        return_value=SimpleNamespace(st_mode=stat.S_IFLNK, st_file_attributes=0),
    ):
        with pytest.raises(ValueError):
            safe_bytes(tmp_path, "file.json")
    with patch.object(
        Path,
        "lstat",
        return_value=SimpleNamespace(
            st_mode=stat.S_IFREG,
            st_file_attributes=getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 1024),
        ),
    ):
        with patch.object(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 1024, create=True):
            with pytest.raises(ValueError):
                safe_bytes(tmp_path, "file.json")
    source.write_bytes(b"x" * (MAX_BYTES + 1))
    with pytest.raises(ValueError):
        safe_bytes(tmp_path, "file.json")
