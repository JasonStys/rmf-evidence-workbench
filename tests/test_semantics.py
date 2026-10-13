"""Supported OSCAL scope, reviewer identity and evidence/determination consistency tests. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_supported_semantics — line 49
# parameter: case — line 49
# parameter: workspace — line 49
# variable: documents — line 51
# variable: result — line 52
# variable: duplicate — line 58
# definition: test_independent_native_negative — line 85
# parameter: tmp_path — line 85
# parameter: workspace — line 85
# variable: output — line 87
# variable: path — line 89
# variable: data — line 90
# variable: node — line 93
# variable: script — line 95
# variable: result — line 96
# END CODE MAP

from __future__ import annotations

import copy
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from rmf.assessment import assess
from rmf.contracts import uid
from rmf.oscal import build, validate_documents
from rmf.report import publish


@pytest.mark.parametrize(
    "case",
    [
        "imports",
        "results",
        "ap-subject",
        "actor",
        "evidence-state",
        "duplicate-scope",
        "false-determination",
        "wrong-control",
    ],
)
def test_supported_semantics(workspace: Path, case: str) -> None:
    """Structural validation alone cannot authorize unsupported scope or contradictory assessment claims."""
    documents = build(*assess(workspace, "2026-10-12T12:00:00Z"))
    result = documents["assessment-results"]["assessment-results"]["results"][0]
    if case == "imports":
        documents["profile"]["profile"]["imports"].append(
            copy.deepcopy(documents["profile"]["profile"]["imports"][0])
        )
    elif case == "results":
        duplicate = copy.deepcopy(result)
        duplicate["uuid"] = uid("new-result")
        documents["assessment-results"]["assessment-results"]["results"].append(
            duplicate
        )
    elif case == "ap-subject":
        documents["assessment-plan"]["assessment-plan"]["assessment-subjects"][0][
            "include-subjects"
        ][0]["subject-uuid"] = uid("outside")
    elif case == "actor":
        result["observations"][0]["origins"][0]["actors"][0]["actor-uuid"] = uid(
            "unknown-reviewer"
        )
    elif case == "evidence-state":
        result["observations"][0]["props"][1]["value"] = "UNREVIEWED_PASS"
    elif case == "duplicate-scope":
        result["observations"][1]["props"][0]["value"] = result["observations"][0][
            "props"
        ][0]["value"]
    elif case == "false-determination":
        result["findings"][0]["target"]["status"]["state"] = "not-satisfied"
    else:
        result["findings"][0]["target"]["target-id"] = "cp-9_lab"
    with pytest.raises(ValueError):
        validate_documents(documents)


def test_independent_native_negative(workspace: Path, tmp_path: Path) -> None:
    """The real native AJV engine rejects malformed official-schema input and never prints private error instances."""
    output = tmp_path / "export"
    publish(*assess(workspace, "2026-10-12T12:00:00Z"), output)
    path = output / "catalog.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["catalog"]["private-unknown"] = "FICTIONAL_PRIVATE_INSTANCE"
    path.write_text(json.dumps(data), encoding="utf-8")
    node = shutil.which("node")
    assert node
    script = Path(__file__).resolve().parents[1] / "scripts/oscal_check.mjs"
    result = subprocess.run(
        [node, str(script), str(output)], capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 2
    assert "FICTIONAL_PRIVATE_INSTANCE" not in result.stdout + result.stderr
