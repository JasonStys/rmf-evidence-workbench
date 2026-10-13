"""CLI, escaped reporting and real cross-language native schema/review workflow tests. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: invoke — line 39
# parameter: arguments — line 39
# definition: test_cli_commands — line 45
# parameter: tmp_path — line 45
# parameter: workspace — line 45
# variable: ledger — line 47
# variable: output — line 49
# definition: test_inert_html_and_exclusive_outputs — line 85
# parameter: tmp_path — line 85
# parameter: workspace — line 85
# variable: bundle — line 87
# variable: original — line 87
# variable: report — line 88
# variable: key — line 92
# variable: value — line 92
# variable: page — line 97
# definition: test_real_native_demo — line 105
# parameter: tmp_path — line 105
# variable: result — line 107
# END CODE MAP

from __future__ import annotations

import copy
from pathlib import Path
from unittest.mock import patch

import pytest

from rmf.__main__ import main
from rmf.assessment import assess
from rmf.contracts import canonical, uid
from rmf.report import publish
from scripts.demo import run


def invoke(arguments: list[str]) -> int:
    """Invoke the actual CLI parser in-process so warning/branch coverage includes its command contracts."""
    with patch("sys.argv", ["rmf", *arguments]):
        return main()


def test_cli_commands(workspace: Path, tmp_path: Path) -> None:
    """Exercise exclusive ledger/output creation, export validation, verified history and sanitized nonzero errors."""
    ledger = tmp_path / "evidence.db"
    assert invoke(["init-ledger", str(ledger)]) == 0
    output = tmp_path / "assessment"
    assert (
        invoke(
            [
                "assess",
                str(workspace),
                "--output",
                str(output),
                "--as-of",
                "2026-10-12T12:00:00Z",
                "--ledger",
                str(ledger),
            ]
        )
        == 0
    )
    assert invoke(["validate-oscal", str(output)]) == 0
    assert invoke(["verify-ledger", str(ledger)]) == 0
    assert invoke(["history", str(ledger), "--state", "NOT_SATISFIED"]) == 0
    assert invoke(["init-ledger", str(ledger)]) == 2
    assert (
        invoke(
            [
                "assess",
                str(workspace),
                "--output",
                str(output),
                "--as-of",
                "invalid date",
            ]
        )
        == 2
    )
    assert invoke(["validate-oscal", str(tmp_path / "missing")]) == 2


def test_inert_html_and_exclusive_outputs(workspace: Path, tmp_path: Path) -> None:
    """Render hostile markup as data with restrictive CSP/no scripts/assets; preserve previous evidence on conflict."""
    bundle, original = assess(workspace, "2026-10-12T12:00:00Z")
    report = copy.deepcopy(original)
    report["system_name"] = "<script>fictional()</script>"
    report["assessment_id"] = uid(
        canonical(
            {key: value for key, value in report.items() if key != "assessment_id"}
        )
    )
    bundle["system"]["name"] = report["system_name"]
    publish(bundle, report, tmp_path / "report")
    page = (tmp_path / "report/assessment.html").read_text(encoding="utf-8")
    assert "<script>" not in page and "&lt;script&gt;" in page
    assert "default-src 'none'" in page and "https://" not in page
    assert "Jason Stys" in page and "NOT_GRANTED" in page
    with pytest.raises(FileExistsError):
        publish(bundle, report, tmp_path / "report")


def test_real_native_demo(tmp_path: Path) -> None:
    """Execute actual Python/AJV validation, SQL chain storage and TypeScript comparison on two synthetic scenarios."""
    result = run(tmp_path / "demo")
    assert result["oscal_documents"] == 12
    assert result["ledger"]["snapshots"] == 2
    assert result["ledger"]["assurance"] == "EXTERNAL_TIP_MATCH"
    assert len(result["comparison"]["changes"]) == 3
    assert result["scenarios"][0]["summary"]["UNKNOWN"] == 1
    assert result["scenarios"][1]["summary"]["SATISFIED"] == 6
