"""Build six real OSCAL models and verify pinned schemas plus scoped cross-document references. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 146
# variable: MODELS — line 147
# variable: EXTENSION — line 155
# definition: property_value — line 158
# parameter: name — line 158
# parameter: value — line 158
# definition: document — line 163
# parameter: body — line 164
# parameter: model — line 164
# parameter: result — line 164
# variable: metadata — line 167
# variable: payload — line 185
# definition: build — line 189
# parameter: bundle — line 189
# parameter: result — line 189
# parameter: value — line 191
# variable: controls — line 191
# variable: selected — line 192
# variable: value — line 192
# variable: reviewed — line 193
# variable: docs — line 194
# variable: value — line 210
# variable: value — line 222
# variable: component — line 229
# variable: value — line 283
# variable: observations — line 305
# variable: findings — line 306
# variable: check_by_control — line 307
# variable: value — line 307
# variable: risk_by_control — line 308
# variable: value — line 308
# variable: check — line 309
# variable: observation_id — line 310
# variable: finding — line 341
# variable: risks — line 366
# variable: poam_items — line 367
# variable: risk — line 368
# variable: risk_record — line 369
# variable: item — line 412
# variable: item — line 418
# variable: results — line 437
# variable: poam — line 455
# definition: unicode_pattern — line 475
# parameter: instance — line 476
# parameter: pattern — line 476
# parameter: schema — line 476
# parameter: validator — line 476
# definition: regex_format — line 489
# parameter: value — line 489
# variable: FORMAT — line 496
# variable: extend_typed — line 500
# variable: UnicodeDraft7 — line 513
# definition: validator — line 516
# parameter: model — line 516
# variable: lock — line 518
# variable: content — line 519
# definition: compiled — line 526
# parameter: content — line 526
# variable: schema — line 528
# definition: unique_ids — line 534
# parameter: value — line 534
# variable: identities — line 536
# variable: pending — line 537
# variable: current — line 539
# variable: identity — line 542
# definition: validate_documents — line 552
# parameter: docs — line 552
# variable: roots — line 556
# variable: data — line 557
# variable: model — line 557
# variable: root — line 563
# variable: catalog — line 582
# variable: control_ids — line 583
# variable: value — line 583
# variable: selected — line 584
# variable: implementations — line 585
# variable: value — line 590
# variable: components — line 594
# variable: value — line 595
# variable: subject — line 597
# variable: value — line 600
# variable: value — line 603
# variable: statement — line 604
# variable: component — line 607
# variable: assessment — line 610
# variable: reviewed — line 611
# variable: value — line 617
# variable: observations — line 620
# variable: value — line 620
# variable: risks — line 621
# variable: value — line 621
# variable: findings — line 622
# variable: value — line 622
# variable: statements — line 623
# variable: control — line 624
# variable: part — line 624
# variable: implementation_ids — line 626
# variable: value — line 628
# variable: statement — line 629
# variable: parties — line 631
# variable: value — line 633
# variable: roles — line 635
# variable: value — line 637
# variable: states_by_observation — line 639
# variable: observation — line 640
# variable: value — line 643
# variable: properties — line 646
# variable: value — line 648
# variable: origin — line 659
# variable: actor — line 660
# variable: value — line 669
# variable: finding — line 674
# variable: related — line 680
# variable: control — line 686
# variable: state — line 686
# variable: expected — line 687
# variable: item — line 695
# variable: available — line 700
# variable: field — line 700
# variable: key — line 700
# variable: reference — line 706
# definition: validate_directory — line 717
# parameter: root — line 717
# variable: model — line 720
# END CODE MAP

from __future__ import annotations

import copy
import json
from collections.abc import Callable, Iterator
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

import regex
from jsonschema import Draft7Validator, FormatChecker, ValidationError
from jsonschema.protocols import Validator
from jsonschema.validators import extend
from referencing import Registry

from rmf.contracts import canonical, digest, identifier, parse_json, safe_bytes, uid

ROOT = Path(__file__).resolve().parents[1]
MODELS = {
    "catalog": "catalog",
    "profile": "profile",
    "ssp": "system-security-plan",
    "assessment-plan": "assessment-plan",
    "assessment-results": "assessment-results",
    "poam": "plan-of-action-and-milestones",
}
EXTENSION = "https://example.invalid/rmf-evidence-workbench"


def property_value(name: str, value: str) -> dict[str, str]:
    """Namespaced educational properties preserve evidence state without overriding OSCAL core semantics."""
    return {"name": name, "ns": EXTENSION, "value": value}


def document(
    model: str, body: dict[str, Any], result: dict[str, Any]
) -> dict[str, Any]:
    """Create a content-derived document UUID and explicit synthetic revision metadata; child entity UUIDs stay stable."""
    metadata = {
        "title": f"Fictional Meridian Operations — {model} — Jason Stys",
        "last-modified": result["as_of"],
        "version": str(result["revision"]),
        "oscal-version": "1.2.3",
        "props": [
            property_value("synthetic", "true"),
            property_value("authorization", "NOT_GRANTED"),
        ],
        "roles": [{"id": "assessor", "title": "Fictional assessment reviewer"}],
        "parties": [
            {
                "uuid": uid("fictional-assessor"),
                "type": "organization",
                "name": "Fictional Assessment Team",
            }
        ],
    }
    payload = {"metadata": metadata, **copy.deepcopy(body)}
    return {MODELS[model]: {"uuid": uid(model + canonical(payload)), **payload}}


def build(bundle: dict[str, Any], result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Build a supported simple profile/SSP/AP/AR/POA&M chain with honest undetermined observations and linked risks."""
    controls = sorted(bundle["controls"], key=lambda value: value["id"])
    selected = [{"control-id": value["id"]} for value in controls]
    reviewed = {"control-selections": [{"include-controls": selected}]}
    docs: dict[str, dict[str, Any]] = {}
    docs["catalog"] = document(
        "catalog",
        {
            "controls": [
                {
                    "id": value["id"],
                    "title": value["title"],
                    "parts": [
                        {
                            "id": value["id"] + "_lab",
                            "name": "statement",
                            "prose": value["requirement"],
                        }
                    ],
                }
                for value in controls
            ]
        },
        result,
    )
    docs["profile"] = document(
        "profile",
        {
            "imports": [
                {
                    "href": "catalog.json",
                    "include-controls": [
                        {"with-ids": [value["id"] for value in controls]}
                    ],
                }
            ]
        },
        result,
    )
    component = bundle["system"]["component_id"]
    docs["ssp"] = document(
        "ssp",
        {
            "import-profile": {"href": "profile.json"},
            "system-characteristics": {
                "system-ids": [
                    {"identifier-type": EXTENSION, "id": bundle["system"]["id"]}
                ],
                "system-name": bundle["system"]["name"],
                "description": "Fictional local evidence system; no real sensitive information or authorization.",
                "system-information": {
                    "information-types": [
                        {
                            "uuid": uid("fictional-information"),
                            "title": "Synthetic operations records",
                            "description": "Invented non-sensitive test records only.",
                        }
                    ]
                },
                "status": {"state": "under-development"},
                "authorization-boundary": {"description": bundle["system"]["boundary"]},
            },
            "system-implementation": {
                "components": [
                    {
                        "uuid": component,
                        "type": "software",
                        "title": "Fictional local operations component",
                        "description": "Owned synthetic evidence producer; not a deployed service.",
                        "status": {"state": "operational"},
                    }
                ]
            },
            "control-implementation": {
                "description": "Selected illustrative predicates, not a complete NIST baseline or control determination.",
                "implemented-requirements": [
                    {
                        "uuid": uid("implementation:" + value["id"]),
                        "control-id": value["id"],
                        "statements": [
                            {
                                "uuid": uid("statement:" + value["id"]),
                                "statement-id": value["id"] + "_lab",
                                "by-components": [
                                    {
                                        "component-uuid": component,
                                        "uuid": uid("by-component:" + value["id"]),
                                        "description": value["requirement"],
                                    }
                                ],
                            }
                        ],
                    }
                    for value in controls
                ],
            },
        },
        result,
    )
    docs["assessment-plan"] = document(
        "assessment-plan",
        {
            "import-ssp": {"href": "ssp.json"},
            "reviewed-controls": reviewed,
            "assessment-subjects": [
                {
                    "type": "component",
                    "include-subjects": [
                        {"subject-uuid": component, "type": "component"}
                    ],
                }
            ],
        },
        result,
    )
    observations = []
    findings = []
    check_by_control = {value["control_id"]: value for value in result["checks"]}
    risk_by_control = {value["control_id"]: value for value in bundle["risks"]}
    for check in result["checks"]:
        observation_id = uid(
            result["assessment_id"] + ":observation:" + check["control_id"]
        )
        observations.append(
            {
                "uuid": observation_id,
                "title": check["title"],
                "description": check["reason"],
                "methods": ["EXAMINE"],
                "collected": result["as_of"],
                "subjects": [{"subject-uuid": component, "type": "component"}],
                "origins": [
                    {
                        "actors": [
                            {
                                "type": "party",
                                "actor-uuid": uid("fictional-assessor"),
                                "role-id": "assessor",
                            }
                        ]
                    }
                ],
                "props": [
                    property_value("control-id", check["control_id"]),
                    property_value("evidence-state", check["state"]),
                ],
            }
        )
        # OSCAL has no core UNKNOWN target status. Preserve undetermined observations
        # and do not fabricate a satisfied/not-satisfied determination for them.
        if check["state"] in {"SATISFIED", "NOT_SATISFIED"}:
            finding: dict[str, Any] = {
                "uuid": uid(
                    result["assessment_id"] + ":finding:" + check["control_id"]
                ),
                "title": check["title"] + " illustrative check",
                "description": "Assessment applies to the stated lab predicate only, not the entire NIST control.",
                "target": {
                    "type": "statement-id",
                    "target-id": check["control_id"] + "_lab",
                    "status": {
                        "state": "satisfied"
                        if check["state"] == "SATISFIED"
                        else "not-satisfied"
                    },
                },
                "implementation-statement-uuid": uid(
                    "statement:" + check["control_id"]
                ),
                "related-observations": [{"observation-uuid": observation_id}],
            }
            if check["control_id"] in risk_by_control:
                finding["related-risks"] = [
                    {"risk-uuid": risk_by_control[check["control_id"]]["id"]}
                ]
            findings.append(finding)
    risks = []
    poam_items = []
    for risk in bundle["risks"]:
        risk_record = {
            "uuid": risk["id"],
            "title": risk["control_id"] + " lab remediation",
            "description": risk["description"],
            "statement": "Fictional selected-check gap requiring human review; not an official risk acceptance.",
            "status": "closed"
            if risk["status"] == "resolved"
            else "remediating"
            if risk["status"] == "in-progress"
            else "open",
            "deadline": risk["due_at"],
            "props": [
                property_value("control-id", risk["control_id"]),
                property_value("severity", risk["severity"]),
                property_value("owner", risk["owner"]),
            ],
            "related-observations": [
                {
                    "observation-uuid": uid(
                        result["assessment_id"] + ":observation:" + risk["control_id"]
                    )
                }
            ],
            "remediations": [
                {
                    "uuid": uid("remediation:" + risk["id"]),
                    "lifecycle": "completed"
                    if risk["status"] == "resolved"
                    else "planned",
                    "title": "Fictional remediation milestones",
                    "description": risk["description"],
                    "tasks": [
                        {
                            "uuid": item["id"],
                            "type": "milestone",
                            "title": item["description"],
                            "timing": {"on-date": {"date": item["due_at"]}},
                            "props": [
                                property_value(
                                    "completion", item["completed_at"] or "pending"
                                )
                            ],
                        }
                        for item in risk["milestones"]
                    ],
                }
            ],
        }
        risks.append(risk_record)
        item: dict[str, Any] = {
            "uuid": uid("poam-item:" + risk["id"]),
            "title": risk_record["title"],
            "description": risk["description"],
            "related-risks": [{"risk-uuid": risk["id"]}],
            "related-observations": risk_record["related-observations"],
        }
        if check_by_control[risk["control_id"]]["state"] in {
            "SATISFIED",
            "NOT_SATISFIED",
        }:
            item["related-findings"] = [
                {
                    "finding-uuid": uid(
                        result["assessment_id"] + ":finding:" + risk["control_id"]
                    )
                }
            ]
        poam_items.append(item)
    results: dict[str, Any] = {
        "uuid": uid(result["assessment_id"] + ":result"),
        "title": "Fictional point-in-time selected-check assessment",
        "description": "Educational observations are not an authorization to operate.",
        "start": result["as_of"],
        "end": result["as_of"],
        "reviewed-controls": reviewed,
        "observations": observations,
    }
    if findings:
        results["findings"] = findings
    if risks:
        results["risks"] = risks
    docs["assessment-results"] = document(
        "assessment-results",
        {"import-ap": {"href": "assessment-plan.json"}, "results": [results]},
        result,
    )
    poam: dict[str, Any] = {
        "import-ssp": {"href": "ssp.json"},
        "observations": observations,
    }
    if risks:
        poam.update({"risks": risks, "poam-items": poam_items})
    else:
        poam["poam-items"] = [
            {
                "uuid": uid(result["assessment_id"] + ":scope-note"),
                "title": "No risk records supplied",
                "description": "Informational scope note only; missing risk records do not prove that this system is risk-free or authorized.",
                "props": [property_value("record-type", "scope-note")],
            }
        ]
    docs["poam"] = document("poam", poam, result)
    validate_documents(docs)
    return docs


def unicode_pattern(
    validator: Validator, pattern: str, instance: object, schema: object
) -> Iterator[ValidationError]:
    """Honor official NIST Unicode property patterns with a bounded regex engine; do not edit/relax schema bytes."""
    if isinstance(instance, str):
        try:
            if not regex.search(pattern, instance, flags=regex.VERSION1, timeout=0.1):
                yield ValidationError(
                    "value does not satisfy the official Unicode pattern"
                )
        except TimeoutError as error:
            raise ValueError("schema pattern evaluation deadline exceeded") from error


def regex_format(value: object) -> bool:
    """Check Unicode-aware regex syntax for the schema metaschema instead of Python re's narrower syntax."""
    if isinstance(value, str):
        regex.compile(value, flags=regex.VERSION1)
    return True


FORMAT = FormatChecker()
FORMAT.checks("regex", raises=regex.error)(regex_format)
# Narrow the vendor's untyped factory API at this tested boundary; domain types
# and every official pattern remain strictly checked.
extend_typed = cast(
    Callable[
        [
            type[Draft7Validator],
            dict[
                str,
                Callable[[Validator, str, object, object], Iterator[ValidationError]],
            ],
        ],
        type[Draft7Validator],
    ],
    extend,
)
UnicodeDraft7 = extend_typed(Draft7Validator, {"pattern": unicode_pattern})


def validator(model: str) -> Validator:
    """Load and hash-verify an official vendored Draft-07 schema; local refs only and format checks enabled."""
    lock = json.loads((ROOT / "oscal.lock.json").read_text(encoding="utf-8"))
    content = safe_bytes(ROOT / "schemas", f"oscal_{model}_schema.json")
    if digest(content) != lock["schemas"][model]:
        raise ValueError("OSCAL schema pin mismatch")
    return compiled(content)


@lru_cache(maxsize=6)
def compiled(content: bytes) -> Validator:
    """Cache compiled immutable verified bytes, not a pathname that could hide later schema tampering."""
    schema = parse_json(content)
    UnicodeDraft7.check_schema(schema, format_checker=FORMAT)
    # Registry defaults to _fail_to_retrieve: no network resolver is installed.
    return UnicodeDraft7(schema, registry=Registry(), format_checker=FORMAT)


def unique_ids(value: object) -> set[str]:
    """Reject duplicate declaration UUIDs within one OSCAL document while allowing references/shared entities across files."""
    identities: set[str] = set()
    pending = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            if "uuid" in current:
                identity = identifier(current["uuid"])
                if identity in identities:
                    raise ValueError("duplicate OSCAL UUID declaration")
                identities.add(identity)
            pending.extend(current.values())
        elif isinstance(current, list):
            pending.extend(current)
    return identities


def validate_documents(docs: dict[str, dict[str, Any]]) -> None:
    """Validate six official schemas then enforce this lab's supported imports, controls, entities and risk/finding links."""
    if set(docs) != set(MODELS):
        raise ValueError("all six supported OSCAL models are required")
    roots: dict[str, dict[str, Any]] = {}
    for model, data in docs.items():
        if not validator(model).is_valid(data):
            # Do not echo schema error instances containing untrusted/private data.
            raise ValueError(f"OSCAL schema validation failed: {model}")
        unique_ids(data)
        roots[model] = data[MODELS[model]]
    if len({root["uuid"] for root in roots.values()}) != 6:
        raise ValueError("document revisions must have distinct UUIDs")
    if (
        len(roots["profile"]["imports"]) != 1
        or len(roots["profile"]["imports"][0].get("include-controls", [])) != 1
        or "modify" in roots["profile"]
        or len(roots["assessment-results"]["results"]) != 1
    ):
        raise ValueError(
            "unsupported profile/result shape; this lab validates a single explicit selection"
        )
    if (
        roots["profile"]["imports"][0]["href"] != "catalog.json"
        or roots["ssp"]["import-profile"]["href"] != "profile.json"
        or roots["assessment-plan"]["import-ssp"]["href"] != "ssp.json"
        or roots["assessment-results"]["import-ap"]["href"] != "assessment-plan.json"
        or roots["poam"]["import-ssp"]["href"] != "ssp.json"
    ):
        raise ValueError("imports must stay in the supported local document chain")
    catalog = roots["catalog"]["controls"]
    control_ids = {value["id"] for value in catalog}
    selected = roots["profile"]["imports"][0]["include-controls"][0]["with-ids"]
    implementations = roots["ssp"]["control-implementation"]["implemented-requirements"]
    if (
        len(control_ids) != len(catalog)
        or len(set(selected)) != len(selected)
        or set(selected) != control_ids
        or {value["control-id"] for value in implementations} != control_ids
        or len(implementations) != len(control_ids)
    ):
        raise ValueError("catalog/profile/implementation control scope differs")
    components = {
        value["uuid"] for value in roots["ssp"]["system-implementation"]["components"]
    }
    for subject in roots["assessment-plan"].get("assessment-subjects", []):
        if subject["type"] != "component" or any(
            value["subject-uuid"] not in components
            for value in subject.get("include-subjects", [])
        ):
            raise ValueError("planned assessment subject outside boundary")
    for value in implementations:
        for statement in value.get("statements", []):
            if any(
                component["component-uuid"] not in components
                for component in statement.get("by-components", [])
            ):
                raise ValueError("implementation references unknown component")
    assessment = roots["assessment-results"]["results"][0]
    for reviewed in (
        roots["assessment-plan"]["reviewed-controls"],
        assessment["reviewed-controls"],
    ):
        if {
            value["control-id"]
            for value in reviewed["control-selections"][0]["include-controls"]
        } != control_ids:
            raise ValueError("assessment control selection differs")
    observations = {value["uuid"] for value in assessment["observations"]}
    risks = {value["uuid"] for value in assessment.get("risks", [])}
    findings = {value["uuid"] for value in assessment.get("findings", [])}
    statements = {
        part["id"] for control in catalog for part in control.get("parts", [])
    }
    implementation_ids = {
        statement["uuid"]
        for value in implementations
        for statement in value.get("statements", [])
    }
    parties = {
        value["uuid"]
        for value in roots["assessment-results"]["metadata"].get("parties", [])
    }
    roles = {
        value["id"]
        for value in roots["assessment-results"]["metadata"].get("roles", [])
    }
    states_by_observation: dict[str, tuple[str, str]] = {}
    for observation in assessment["observations"]:
        if any(
            value["subject-uuid"] not in components
            for value in observation.get("subjects", [])
        ):
            raise ValueError("observation subject outside system boundary")
        properties = {
            value["name"]: value["value"]
            for value in observation.get("props", [])
            if value.get("ns") == EXTENSION
        }
        if properties.get("control-id") not in control_ids or properties.get(
            "evidence-state"
        ) not in {"SATISFIED", "NOT_SATISFIED", "UNKNOWN", "INTEGRITY_ERROR"}:
            raise ValueError("observation has unknown control/evidence semantics")
        states_by_observation[observation["uuid"]] = (
            properties["control-id"],
            properties["evidence-state"],
        )
        for origin in observation.get("origins", []):
            for actor in origin["actors"]:
                if (
                    actor["type"] != "party"
                    or actor["actor-uuid"] not in parties
                    or actor.get("role-id", "assessor") not in roles
                ):
                    raise ValueError("unknown observation actor/role")
    if (
        len(states_by_observation) != len(control_ids)
        or {value[0] for value in states_by_observation.values()} != control_ids
    ):
        raise ValueError(
            "every selected control needs exactly one explicit evidence observation"
        )
    for finding in assessment.get("findings", []):
        if (
            finding["target"]["target-id"] not in statements
            or finding["implementation-statement-uuid"] not in implementation_ids
        ):
            raise ValueError("finding target/implementation is unknown")
        related = finding.get("related-observations", [])
        if (
            len(related) != 1
            or related[0]["observation-uuid"] not in states_by_observation
        ):
            raise ValueError("finding must reference one known evidence observation")
        control, state = states_by_observation[related[0]["observation-uuid"]]
        expected = "satisfied" if state == "SATISFIED" else "not-satisfied"
        if (
            state not in {"SATISFIED", "NOT_SATISFIED"}
            or finding["target"]["status"]["state"] != expected
            or finding["target"]["target-id"] != control + "_lab"
            or finding["implementation-statement-uuid"] != uid("statement:" + control)
        ):
            raise ValueError("finding determination contradicts its evidence/control")
    for item in [
        *assessment.get("findings", []),
        *assessment.get("risks", []),
        *roots["poam"].get("poam-items", []),
    ]:
        for field, key, available in (
            ("related-observations", "observation-uuid", observations),
            ("related-risks", "risk-uuid", risks),
            ("related-findings", "finding-uuid", findings),
        ):
            if any(
                reference[key] not in available for reference in item.get(field, [])
            ):
                raise ValueError("dangling assessment/remediation reference")
    if canonical(assessment.get("risks", [])) != canonical(
        roots["poam"].get("risks", [])
    ) or canonical(assessment["observations"]) != canonical(
        roots["poam"]["observations"]
    ):
        raise ValueError("POA&M changed the assessment's risk/evidence identity")


def validate_directory(root: Path) -> None:
    """Read only six fixed local JSON filenames; no import URI or user content can trigger network access."""
    validate_documents(
        {model: parse_json(safe_bytes(root, model + ".json")) for model in MODELS}
    )
