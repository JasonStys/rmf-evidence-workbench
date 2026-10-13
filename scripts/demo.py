"""Execute two real assessments, twelve OSCAL validations, ledger verification and typed review. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 35
# definition: run — line 43
# parameter: output — line 43
# variable: node — line 45
# variable: ledger — line 49
# variable: summaries — line 51
# variable: tip — line 52
# variable: as_of — line 53
# variable: scenario — line 53
# variable: bundle — line 57
# variable: result — line 57
# variable: receipt — line 59
# variable: tip — line 60
# variable: native — line 61
# variable: review — line 75
# variable: changes — line 87
# variable: result — line 92
# definition: main — line 113
# variable: parser — line 115
# variable: arguments — line 117
# END CODE MAP

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rmf.assessment import assess  # noqa: E402
from rmf.ledger import append, create, verify  # noqa: E402
from rmf.report import publish  # noqa: E402


def run(output: Path) -> dict[str, Any]:
    """Use only repository synthetic workspaces; retain prior output and verify independent engines and actual SQL history."""
    node = shutil.which("node")
    if node is None or not (ROOT / "dist/review.js").is_file():
        raise ValueError("build the Node 24 typed reviewer first")
    output.mkdir(parents=True, mode=0o700, exist_ok=False)
    ledger = output / "evidence.db"
    create(ledger)
    summaries = []
    tip = None
    for scenario, as_of in (
        ("baseline", "2026-10-12T12:00:00Z"),
        ("remediated", "2026-10-13T12:00:00Z"),
    ):
        bundle, result = assess(ROOT / "examples" / scenario, as_of)
        publish(bundle, result, output / scenario)
        receipt = append(ledger, result, tip)
        tip = receipt["tip"]
        native = subprocess.run(
            [node, str(ROOT / "scripts/oscal_check.mjs"), str(output / scenario)],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        summaries.append(
            {
                "scenario": scenario,
                "summary": result["summary"],
                "native_validation": json.loads(native.stdout),
            }
        )
    review = subprocess.run(
        [
            node,
            str(ROOT / "dist/review.js"),
            str(output / "baseline/assessment.json"),
            str(output / "remediated/assessment.json"),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    changes = json.loads(review.stdout)
    if len(changes["changes"]) != 3 or len(changes["risk_changes"]) != 3:
        raise ValueError(
            "cross-language change report differs from expected synthetic remediation"
        )
    result = {
        "synthetic": True,
        "authorization": "NOT_GRANTED",
        "scenarios": summaries,
        "ledger": verify(ledger, tip),
        "comparison": changes,
        "oscal_documents": 12,
        "schema_engines": [
            "Python jsonschema with Unicode patterns",
            "native ECMAScript Ajv 8.20.0",
        ],
    }
    (output / "validation.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, sort_keys=True))
    return result


def main() -> int:
    """Run an explicit new local end-to-end example; no network/host collection, credentials or accounts are required."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "out/demo")
    arguments = parser.parse_args()
    run(arguments.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
