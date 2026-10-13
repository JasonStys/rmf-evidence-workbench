"""Create/check reproducible fictional baseline and remediated evidence workspaces. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 40
# definition: contents — line 47
# parameter: remediated — line 47
# variable: system — line 49
# variable: titles — line 55
# variable: facts — line 63
# variable: output — line 75
# variable: evidence — line 76
# variable: control_id — line 77
# variable: observed_at — line 78
# variable: path — line 85
# variable: payload — line 86
# variable: serialized — line 94
# variable: risks — line 106
# variable: control_id — line 107
# variable: bundle — line 131
# variable: control_id — line 144
# definition: generate — line 153
# parameter: check — line 153
# parameter: remediated — line 153
# parameter: root — line 153
# variable: content — line 155
# variable: relative — line 155
# variable: path — line 156
# definition: main — line 168
# variable: parser — line 170
# variable: arguments — line 172
# END CODE MAP

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rmf.assessment import CHECKS  # noqa: E402
from rmf.contracts import digest, uid  # noqa: E402


def contents(remediated: bool) -> dict[str, str]:
    """Return exact portable fictional bytes, controlled dates and illustrative facts; no host collection/network calls."""
    system = {
        "id": uid("fictional-system"),
        "name": "Meridian Operations — Synthetic Demo",
        "boundary": "One fictional local software component; no production hosts, accounts, networks or sensitive data.",
        "component_id": uid("fictional-component"),
    }
    titles = {
        "ac-2": "Account review",
        "ac-3": "Access denial",
        "au-2": "Audit completeness",
        "au-6": "Audit review",
        "cm-6": "Configuration settings",
        "cp-9": "Backup recovery",
    }
    facts: dict[str, Any] = {
        "ac-2": {"active_accounts": 4, "reviewed_accounts": 4},
        "ac-3": {"unauthorized_denied": True, "cross_tenant_denied": True},
        "au-2": {"source_events": 12, "retained_events": 12},
        "au-6": {"review_completed": True},
        "cm-6": {"drift_count": 0 if remediated else 3},
        "cp-9": {
            "restore_verified": remediated,
            "rpo_seconds": 120,
            "rto_seconds": 600,
        },
    }
    output: dict[str, str] = {}
    evidence = []
    for control_id in CHECKS:
        observed_at = (
            "2026-10-13T11:00:00Z"
            if remediated
            else "2026-10-01T11:00:00Z"
            if control_id == "au-6"
            else "2026-10-12T11:00:00Z"
        )
        path = "evidence/" + control_id + ".json"
        payload = {
            "schema": 1,
            "control_id": control_id,
            "component_id": system["component_id"],
            "observed_at": observed_at,
            "check": CHECKS[control_id],
            "facts": facts[control_id],
        }
        serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        output[path] = serialized
        evidence.append(
            {
                "id": uid("evidence:" + control_id + ":" + str(remediated)),
                "control_id": control_id,
                "component_id": system["component_id"],
                "observed_at": observed_at,
                "path": path,
                "sha256": digest(serialized.encode()),
            }
        )
    risks = []
    for control_id in ("au-6", "cm-6", "cp-9"):
        risks.append(
            {
                "id": uid("risk:" + control_id),
                "control_id": control_id,
                "severity": "high" if control_id == "cp-9" else "moderate",
                "status": "resolved" if remediated else "open",
                "owner": "Fictional Operations Team",
                "description": "Refresh and verify the selected "
                + control_id
                + " lab evidence before review.",
                "opened_at": "2026-10-01T00:00:00Z",
                "due_at": "2026-10-12T12:00:00Z",
                "completed_at": "2026-10-13T11:30:00Z" if remediated else None,
                "milestones": [
                    {
                        "id": uid("milestone:" + control_id),
                        "description": "Produce fresh, verified selected-check evidence",
                        "due_at": "2026-10-12T12:00:00Z",
                        "completed_at": "2026-10-13T11:30:00Z" if remediated else None,
                    }
                ],
            }
        )
    bundle = {
        "schema": 1,
        "system": system,
        "revision": 2 if remediated else 1,
        "controls": [
            {
                "id": control_id,
                "title": titles[control_id],
                "requirement": "Demonstrate only the fictional "
                + CHECKS[control_id]
                + " predicate described in docs/contracts.md; this is not the full NIST control text.",
                "max_age_hours": 24,
            }
            for control_id in CHECKS
        ],
        "evidence": evidence,
        "risks": risks,
    }
    output["bundle.json"] = json.dumps(bundle, indent=2, sort_keys=True) + "\n"
    return output


def generate(root: Path, remediated: bool, check: bool = False) -> None:
    """Write only deterministic generated fictional examples or verify byte equality without overwriting user work."""
    for relative, content in contents(remediated).items():
        path = root / relative
        if check:
            if path.read_bytes() != content.encode():
                raise ValueError("fictional example bytes/digests drifted")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists() and path.read_bytes() != content.encode():
                raise ValueError("refusing to overwrite changed example")
            if not path.exists():
                path.write_text(content, encoding="utf-8", newline="\n")


def main() -> int:
    """Generate/check only the two versioned synthetic sample workspaces in this repository."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    generate(ROOT / "examples/baseline", False, arguments.check)
    generate(ROOT / "examples/remediated", True, arguments.check)
    print("Two fictional workspaces and their exact evidence digests verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
