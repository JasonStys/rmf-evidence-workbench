"""Actual required URI/Unicode IRI checker and no-silent-downgrade contracts for distributable native validation. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_actual_supported_format_checks_are_present_and_do_not_silently_pass — line 33
# parameter: name — line 34
# parameter: valid — line 34
# parameter: value — line 34
# definition: test_missing_required_checker_fails_even_with_cached_schemas — line 42
# parameter: missing — line 42
# parameter: monkeypatch — line 42
# definition: test_fresh_distribution_uses_supported_nongpl_dependencies — line 50
# END CODE MAP

import importlib.util

import pytest

from rmf.oscal import FORMAT, validator


@pytest.mark.parametrize(
    "name,value,valid",
    [
        ("uri", "https://example.test/report", True),
        ("uri", "https://bad host/report", False),
        ("uri-reference", "../reports/first.json#section", True),
        ("uri-reference", "bad path with spaces", False),
        ("iri", "https://例え.テスト/資料", True),
        ("iri", "https://例え.テスト/bad path", False),
        ("iri-reference", "資料/報告#節", True),
        ("iri-reference", "bad\x00reference", False),
    ],
)
def test_actual_supported_format_checks_are_present_and_do_not_silently_pass(
    name, value, valid
):
    """Check real installed format behavior, including valid Unicode and invalid controls/spaces, not merely package names."""
    assert name in FORMAT.checkers
    assert bool(FORMAT.conforms(value, name)) is valid


@pytest.mark.parametrize("missing", ["uri", "uri-reference", "iri", "iri-reference"])
def test_missing_required_checker_fails_even_with_cached_schemas(monkeypatch, missing):
    """An optional-dependency packaging omission must fail closed before any cached validator can accept input."""
    validator("catalog")
    monkeypatch.delitem(FORMAT.checkers, missing)
    with pytest.raises(ValueError, match="unavailable"):
        validator("catalog")


def test_fresh_distribution_uses_supported_nongpl_dependencies():
    """Do not leave the old optional GPL module active and accidentally bypass the independently tested replacement."""
    assert importlib.util.find_spec("rfc3987") is None
    assert importlib.util.find_spec("rfc3987_syntax") is not None
    assert importlib.util.find_spec("rfc3986_validator") is not None
