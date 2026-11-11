"""Independent baseline/OSCAL/calendar/transition and independently retained-tip native workflow oracles. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: state — line 110
# parameter: tmp_path — line 110
# variable: value — line 112
# definition: run — line 119
# parameter: changes — line 119
# parameter: index — line 119
# parameter: state — line 119
# parameter: tmp_path — line 119
# variable: parameters — line 121
# variable: stage — line 122
# variable: files — line 123
# variable: kind — line 123
# variable: summary — line 123
# variable: identity — line 124
# definition: test_actual_baseline_remediation_six_models_and_original_raw_evidence_stays_out — line 129
# parameter: state — line 130
# parameter: tmp_path — line 130
# variable: first — line 133
# variable: summary — line 133
# variable: baseline — line 134
# variable: _ — line 141
# variable: second — line 141
# variable: remediated — line 142
# variable: target — line 153
# variable: name — line 156
# definition: test_calendar_retains_owner_due_work_even_without_authorization — line 161
# parameter: state — line 161
# parameter: tmp_path — line 161
# variable: files — line 163
# variable: summary — line 163
# variable: value — line 164
# variable: row — line 167
# definition: test_normalized_comparison_has_exact_known_transitions_and_source_identities — line 172
# parameter: state — line 173
# parameter: tmp_path — line 173
# variable: _ — line 176
# variable: files — line 176
# variable: value — line 177
# variable: row — line 179
# variable: before — line 181
# variable: after — line 182
# definition: test_new_ledger_is_unanchored_until_an_explicit_external_tip_is_supplied — line 188
# parameter: state — line 189
# parameter: tmp_path — line 189
# variable: _ — line 192
# variable: files — line 192
# variable: value — line 193
# variable: original — line 197
# variable: source — line 198
# variable: parameters — line 200
# variable: stage — line 206
# variable: _ — line 208
# variable: summary — line 208
# variable: verified — line 208
# variable: result — line 209
# variable: other — line 217
# definition: test_retained_tip_detects_a_valid_but_truncated_chain — line 224
# parameter: state — line 224
# parameter: tmp_path — line 224
# variable: _ — line 226
# variable: files — line 226
# variable: tip — line 227
# variable: truncated — line 228
# variable: first — line 230
# variable: parameters — line 233
# variable: stage — line 239
# definition: test_bad_clock_horizon_and_invented_authorization_preserve_saved_evidence — line 256
# parameter: changes — line 257
# parameter: state — line 257
# parameter: tmp_path — line 257
# variable: _ — line 260
# variable: original — line 260
# definition: test_wrong_system_tampered_report_reversed_chronology_and_active_journal_are_refused — line 266
# parameter: state — line 267
# parameter: tmp_path — line 267
# variable: values — line 270
# variable: after — line 271
# variable: before — line 271
# variable: other_system — line 274
# variable: key — line 280
# variable: value — line 280
# variable: broken — line 288
# variable: invalid — line 292
# variable: source — line 296
# variable: stage — line 299
# definition: test_empty_report_set_unknown_prepared_choice_and_markup_are_not_executable — line 310
# parameter: state — line 311
# parameter: tmp_path — line 311
# variable: value — line 318
# END CODE MAP

import copy
import json
import tempfile
from pathlib import Path

import pytest

from rmf import desktop_project as project
from rmf import ledger
from rmf.contracts import canonical, uid
from rmf.desktop_io import Rejected, json_value
from rmf.desktop_state import Workspace
from rmf.oscal import validate_directory


@pytest.fixture
def state(tmp_path):
    """Retain only explicit synthetic normalized metadata in a new real SQLite profile outside installation."""
    value = Workspace(
        tmp_path / "profile", project.PRODUCT, project.ROOT, synthetic=True
    )
    yield value
    value.close()


def run(state, tmp_path, index, **changes):
    """Every operation gets fresh staging; failures cannot accidentally pass because old output already exists."""
    parameters = {**project.scenario(project.SCENARIOS[index]), **changes}
    stage = Path(tempfile.mkdtemp(prefix="owned-stage-", dir=tmp_path))
    kind, summary, files = project.analyze(state, parameters, stage)
    identity = state.save(kind, summary, parameters, files)
    assert state.files(identity) == files
    return files, summary


def test_actual_baseline_remediation_six_models_and_original_raw_evidence_stays_out(
    state, tmp_path
):
    """Known baseline3/2/1 and remediation6/0/0 remain separate snapshots, each with six actual valid OSCAL models."""
    first, summary = run(state, tmp_path, 0)
    baseline = json_value(first["assessment.json"])
    assert baseline["summary"] == {
        "SATISFIED": 3,
        "NOT_SATISFIED": 2,
        "UNKNOWN": 1,
        "INTEGRITY_ERROR": 0,
    }
    second, _ = run(state, tmp_path, 1)
    remediated = json_value(second["assessment.json"])
    assert remediated["summary"] == {
        "SATISFIED": 6,
        "NOT_SATISFIED": 0,
        "UNKNOWN": 0,
        "INTEGRITY_ERROR": 0,
    }
    assert len(first) == len(second) == 8
    assert baseline["authorization"] == remediated["authorization"] == "NOT_GRANTED"
    assert "authorization NOT_GRANTED" in summary
    assert state.files(1) == first and state.files(2) == second
    target = state.export(1, tmp_path, project.PRODUCT)
    validate_directory(target)
    assert not any(
        name.startswith("evidence/") or name == "bundle.json" for name in first
    )
    assert len(project.views(first)["Original evidence predicates"]) == 6


def test_calendar_retains_owner_due_work_even_without_authorization(state, tmp_path):
    """The independently specified fictional baseline schedules14items, including six freshness/gap reviews."""
    files, summary = run(state, tmp_path, 2)
    value = json_value(files["calendar.json"])
    assert len(value["events"]) == 14 and "14 selected-scope" in summary
    assert value["authorization"] == "NOT_GRANTED"
    assert any(row["owner"] == "UNASSIGNED evidence owner" for row in value["events"])
    assert set(files) == {"calendar.json", "calendar.html", "calendar.csv"}
    assert project.views(files)["Owner work calendar"] == value["events"]


def test_normalized_comparison_has_exact_known_transitions_and_source_identities(
    state, tmp_path
):
    """Three actual controls and three risks change; no change in denominator can be presented as authorization."""
    files, _ = run(state, tmp_path, 3)
    value = json_value(files["result.json"])
    assert len(value["changes"]) == len(value["risk_changes"]) == 3
    assert {row["after"] for row in value["changes"]} == {"SATISFIED"}
    assert value["authorization"] == "NOT_GRANTED"
    before = project.report(project.scenario(project.SCENARIOS[3])["before"])
    after = project.report(project.scenario(project.SCENARIOS[3])["after"])
    assert value["before_assessment_id"] == before["assessment_id"]
    assert value["after_assessment_id"] == after["assessment_id"]
    assert len(project.views(files)["Risk transitions"]) == 3


def test_new_ledger_is_unanchored_until_an_explicit_external_tip_is_supplied(
    state, tmp_path
):
    """A new chain is not its own trust anchor; functional matching-tip verification is a distinct operation."""
    files, _ = run(state, tmp_path, 4)
    value = json_value(files["result.json"])
    assert value["verification"]["assurance"] == "UNANCHORED_LOCAL_CHAIN"
    assert value["verification"]["snapshots"] == 2
    assert len(value["history"]) == 2
    original = files.copy()
    source = tmp_path / "closed.sqlite"
    source.write_bytes(files["ledger.sqlite"])
    parameters = {
        **project.scenario(project.SCENARIOS[4]),
        "mode": project.MODES[4],
        "ledger": str(source),
        "tip": value["receipt"]["tip"],
    }
    stage = tmp_path / "verify"
    stage.mkdir()
    _, summary, verified = project.analyze(state, parameters, stage)
    result = json_value(verified["result.json"])
    assert result["verification"]["assurance"] == "EXTERNAL_TIP_MATCH"
    assert result["history"] == value["history"] and "EXTERNAL_TIP_MATCH" in summary
    assert (
        source.read_bytes() == original["ledger.sqlite"] and state.files(1) == original
    )
    assert "ledger.sqlite" not in verified
    parameters["tip"] = "0" * 64
    other = tmp_path / "wrong-tip"
    other.mkdir()
    with pytest.raises(ValueError):
        project.analyze(state, parameters, other)
    assert len(state.history()) == 1


def test_retained_tip_detects_a_valid_but_truncated_chain(state, tmp_path):
    """An internally consistent one-snapshot prefix cannot match the separately retained two-snapshot tip."""
    files, _ = run(state, tmp_path, 4)
    tip = json_value(files["result.json"])["receipt"]["tip"]
    truncated = tmp_path / "prefix.sqlite"
    ledger.create(truncated)
    first = project.report(project.scenario(project.SCENARIOS[4])["before"])
    ledger.append(truncated, first)
    assert ledger.verify(truncated)["snapshots"] == 1
    parameters = {
        **project.scenario(project.SCENARIOS[4]),
        "mode": project.MODES[4],
        "ledger": str(truncated),
        "tip": tip,
    }
    stage = tmp_path / "prefix-review"
    stage.mkdir()
    with pytest.raises(ValueError):
        project.analyze(state, parameters, stage)
    assert state.files(1) == files


@pytest.mark.parametrize(
    "changes",
    [
        {"horizon": "0"},
        {"horizon": "169"},
        {"horizon": "1.5"},
        {"as_of": "2026-02-30T00:00:00Z"},
        {"mode": "grant authorization"},
    ],
)
def test_bad_clock_horizon_and_invented_authorization_preserve_saved_evidence(
    state, tmp_path, changes
):
    """Input mistakes remain rejected operations instead of fabricated satisfied controls or replacement history."""
    original, _ = run(state, tmp_path, 0)
    with pytest.raises((ValueError, OSError)):
        run(state, tmp_path, 2, **changes)
    assert len(state.history()) == 1 and state.files(1) == original


def test_wrong_system_tampered_report_reversed_chronology_and_active_journal_are_refused(
    state, tmp_path
):
    """Content identity, system boundary, chronology and closed-database conditions are independently necessary."""
    values = project.scenario(project.SCENARIOS[3])
    before, after = project.report(values["before"]), project.report(values["after"])
    with pytest.raises(ValueError):
        project.comparison(after, before)
    other_system = copy.deepcopy(after)
    other_system["system_id"] = uid("independent fictional other system")
    other_system["assessment_id"] = uid(
        canonical(
            {
                key: value
                for key, value in other_system.items()
                if key != "assessment_id"
            }
        )
    )
    ledger.validate_report(other_system)
    with pytest.raises(ValueError, match="same system"):
        project.comparison(before, other_system)
    broken = copy.deepcopy(after)
    broken["checks"][0]["state"] = "SATISFIED_BY_USER_CLICK"
    with pytest.raises(ValueError):
        project.comparison(before, broken)
    invalid = tmp_path / "invalid.json"
    invalid.write_text(json.dumps(broken), encoding="utf-8")
    with pytest.raises(ValueError):
        project.report(str(invalid))
    source = tmp_path / "active.sqlite"
    source.write_bytes(b"not used")
    source.with_name(source.name + "-wal").write_bytes(b"active control")
    stage = tmp_path / "active-review"
    stage.mkdir()
    with pytest.raises(ValueError, match="close"):
        project.analyze(
            state,
            {**values, "mode": project.MODES[4], "ledger": str(source), "tip": ""},
            stage,
        )
    assert source.read_bytes() == b"not used"


def test_empty_report_set_unknown_prepared_choice_and_markup_are_not_executable(
    state, tmp_path
):
    """Closed data operations reject invented commands and render literal text without external content."""
    with pytest.raises(ValueError):
        run(state, tmp_path, 4, reports="")
    with pytest.raises(Rejected):
        project.scenario("authorize production")
    value = project.text_bundle({"note": "<script>example()</script>"}, "<img>")
    assert (
        b"&lt;script&gt;" in value["result.html"]
        and b"<script>" not in value["result.html"]
    )
