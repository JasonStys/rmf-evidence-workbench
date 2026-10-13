"""Validate immutable schema/example pins and storage-free least-privilege CI contracts. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 23
# definition: validate — line 26
# variable: path — line 31
# variable: workflow — line 32
# variable: job — line 35
# variable: step — line 36
# variable: action — line 37
# variable: word — line 43
# END CODE MAP

from __future__ import annotations

import re
from pathlib import Path

import yaml
from vendor_oscal import vendor

from examples import generate

ROOT = Path(__file__).resolve().parents[1]


def validate() -> None:
    """Require exact action SHA pins, credential-free checkout, no privileged PRs and no Actions uploads/caches."""
    vendor(True)
    generate(ROOT / "examples/baseline", False, True)
    generate(ROOT / "examples/remediated", True, True)
    for path in (ROOT / ".github/workflows").glob("*.yml"):
        workflow = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        if "pull_request_target" in workflow["on"]:
            raise ValueError("privileged PR execution forbidden")
        for job in workflow["jobs"].values():
            for step in job["steps"]:
                action = step.get("uses", "")
                if action and not re.fullmatch(
                    r"[A-Za-z0-9_./-]+@[0-9a-f]{40}", action
                ):
                    raise ValueError("GitHub action must use a complete commit pin")
                if any(
                    word in action for word in ("upload-artifact", "/cache@")
                ) or step.get("with", {}).get("cache"):
                    raise ValueError(
                        "this lab must not retain Actions artifacts/caches"
                    )
                if (
                    action.startswith("actions/checkout")
                    and step.get("with", {}).get("persist-credentials") != "false"
                ):
                    raise ValueError("checkout credentials must not persist")
    print("Pinned schemas/examples and storage-free workflow contracts passed")


if __name__ == "__main__":
    validate()
