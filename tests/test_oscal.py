"""Real schema, Unicode, semantic-reference and no-authorization regression tests. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_real_schemas_and_unknown_observations — line 60
# parameter: tmp_path — line 60
# parameter: workspace — line 60
# variable: bundle — line 62
# variable: result — line 62
# variable: documents — line 63
# variable: assessment — line 64
# variable: item — line 68
# variable: value — line 73
# variable: later — line 75
# definition: test_schema_and_reference_mutations — line 101
# parameter: case — line 101
# parameter: workspace — line 101
# variable: bundle — line 103
# variable: result — line 103
# variable: documents — line 104
# variable: ssp — line 105
# variable: assessment — line 106
# definition: test_unicode_pattern_pin_and_no_remote_fetch — line 149
# parameter: workspace — line 149
# variable: bundle — line 151
# variable: result — line 151
# variable: documents — line 152
# variable: catalog — line 153
# definition: test_no_risks_and_all_unknown — line 170
# parameter: workspace — line 170
# variable: bundle — line 172
# variable: bundle — line 176
# variable: result — line 176
# variable: documents — line 177
# variable: item — line 183
# END CODE MAP

from __future__ import annotations

import copy
import json
from pathlib import Path
from unittest.mock import patch

import pytest
from referencing import Registry
from referencing.exceptions import NoSuchResource

from rmf.assessment import assess
from rmf.contracts import uid
from rmf.oscal import (
    build,
    unique_ids,
    validate_directory,
    validate_documents,
    validator,
)
from rmf.report import publish
from tests.conftest import change_manifest


def test_real_schemas_and_unknown_observations(workspace: Path, tmp_path: Path) -> None:
    """All six original NIST schemas validate exports; undetermined evidence has observations but no invented finding."""
    bundle, result = assess(workspace, "2026-10-12T12:00:00Z")
    documents = build(bundle, result)
    assessment = documents["assessment-results"]["assessment-results"]["results"][0]
    assert len(assessment["observations"]) == 6
    assert len(assessment["findings"]) == 5
    assert not any(
        item["target"]["target-id"] == "au-6_lab" for item in assessment["findings"]
    )
    publish(bundle, result, tmp_path / "export")
    validate_directory(tmp_path / "export")
    assert (
        len({next(iter(value.values()))["uuid"] for value in documents.values()}) == 6
    )
    later = copy.deepcopy(result)
    later["as_of"] = "2026-10-12T12:00:01Z"
    assert (
        build(bundle, later)["ssp"]["system-security-plan"]["uuid"]
        != documents["ssp"]["system-security-plan"]["uuid"]
    )


@pytest.mark.parametrize(
    "case",
    [
        "root-field",
        "document-id",
        "import",
        "control",
        "component",
        "review-scope",
        "subject",
        "target",
        "statement",
        "observation",
        "risk",
        "poam-drift",
        "uuid-duplicate",
    ],
)
def test_schema_and_reference_mutations(workspace: Path, case: str) -> None:
    """Schema-shaped but inconsistent references cannot silently produce a credible assessment chain."""
    bundle, result = assess(workspace, "2026-10-12T12:00:00Z")
    documents = build(bundle, result)
    ssp = documents["ssp"]["system-security-plan"]
    assessment = documents["assessment-results"]["assessment-results"]["results"][0]
    if case == "root-field":
        ssp["private-unknown"] = "do not retain"
    elif case == "document-id":
        ssp["uuid"] = documents["catalog"]["catalog"]["uuid"]
    elif case == "import":
        ssp["import-profile"]["href"] = "https://example.com/untrusted.json"
    elif case == "control":
        ssp["control-implementation"]["implemented-requirements"][0]["control-id"] = (
            "outside"
        )
    elif case == "component":
        ssp["control-implementation"]["implemented-requirements"][0]["statements"][0][
            "by-components"
        ][0]["component-uuid"] = uid("outside")
    elif case == "review-scope":
        assessment["reviewed-controls"]["control-selections"][0]["include-controls"] = [
            {"control-id": "outside"}
        ]
    elif case == "subject":
        assessment["observations"][0]["subjects"][0]["subject-uuid"] = uid("outside")
    elif case == "target":
        assessment["findings"][0]["target"]["target-id"] = "outside_lab"
    elif case == "statement":
        assessment["findings"][0]["implementation-statement-uuid"] = uid("outside")
    elif case == "observation":
        assessment["findings"][0]["related-observations"][0]["observation-uuid"] = uid(
            "outside"
        )
    elif case == "risk":
        documents["poam"]["plan-of-action-and-milestones"]["poam-items"][0][
            "related-risks"
        ][0]["risk-uuid"] = uid("outside")
    elif case == "poam-drift":
        documents["poam"]["plan-of-action-and-milestones"]["risks"][0]["status"] = (
            "closed"
        )
    else:
        assessment["observations"][1]["uuid"] = assessment["observations"][0]["uuid"]
    with pytest.raises(ValueError):
        validate_documents(documents)


def test_unicode_pattern_pin_and_no_remote_fetch(workspace: Path) -> None:
    """Native Unicode token patterns stay enforced, cached validators recheck schema pins and the registry cannot fetch URLs."""
    bundle, result = assess(workspace, "2026-10-12T12:00:00Z")
    documents = build(bundle, result)
    catalog = documents["catalog"]["catalog"]
    catalog["controls"][0]["id"] = "α_control"
    assert validator("catalog").is_valid(documents["catalog"])
    catalog["controls"][0]["id"] = "invalid whitespace"
    assert not validator("catalog").is_valid(documents["catalog"])
    with patch("rmf.oscal.safe_bytes", return_value=b"{}"):
        with pytest.raises(ValueError):
            validator("catalog")
    with pytest.raises(NoSuchResource):
        Registry().get_or_retrieve("https://example.com/never-fetched")
    assert unique_ids({"item": [{"uuid": uid("a")}]}) == {uid("a")}
    with pytest.raises(ValueError):
        unique_ids({"item": [{"uuid": uid("a")}, {"uuid": uid("a")}]})
    with pytest.raises(ValueError):
        validate_documents({})


def test_no_risks_and_all_unknown(workspace: Path) -> None:
    """No supplied risks creates only an informational scope note; missing evidence never invents core findings."""
    bundle = json.loads((workspace / "bundle.json").read_text(encoding="utf-8"))
    bundle["risks"] = []
    bundle["evidence"] = []
    change_manifest(workspace, bundle)
    bundle, result = assess(workspace, "2026-10-12T12:00:00Z")
    documents = build(bundle, result)
    assert result["summary"]["UNKNOWN"] == 6
    assert (
        "findings"
        not in documents["assessment-results"]["assessment-results"]["results"][0]
    )
    item = documents["poam"]["plan-of-action-and-milestones"]["poam-items"][0]
    assert item["title"] == "No risk records supplied"
    assert "related-risks" not in item
