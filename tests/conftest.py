"""Owned synthetic workspace fixtures with precise digest maintenance. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: workspace — line 34
# parameter: tmp_path — line 34
# variable: path — line 36
# definition: change_manifest — line 41
# parameter: data — line 41
# parameter: root — line 41
# definition: change_evidence — line 46
# parameter: changes — line 46
# parameter: control_id — line 46
# parameter: root — line 46
# variable: path — line 48
# variable: value — line 49
# variable: content — line 51
# variable: manifest — line 53
# variable: entry — line 54
# variable: item — line 55
# END CODE MAP

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from rmf.contracts import digest
from scripts.examples import generate


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Create a baseline in the current test's new temporary directory; no existing/user evidence is changed."""
    path = tmp_path / "workspace"
    generate(path, False)
    return path


def change_manifest(root: Path, data: dict[str, Any]) -> None:
    """Write explicitly synthetic test manifest data; tests never edit the versioned example bytes."""
    (root / "bundle.json").write_text(json.dumps(data), encoding="utf-8")


def change_evidence(root: Path, control_id: str, **changes: Any) -> None:
    """Change only one synthetic fact record and update its trusted test manifest digest/time for semantic tests."""
    path = root / "evidence" / f"{control_id}.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value.update(changes)
    content = json.dumps(value).encode()
    path.write_bytes(content)
    manifest = json.loads((root / "bundle.json").read_text(encoding="utf-8"))
    entry = next(
        item for item in manifest["evidence"] if item["control_id"] == control_id
    )
    entry["sha256"] = digest(content)
    entry["observed_at"] = value["observed_at"]
    change_manifest(root, manifest)
