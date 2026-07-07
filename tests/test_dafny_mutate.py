"""Phase C, Gate C5: mutation-testing generation logic (fast, no Dafny
invocations - real re-verification is captured once by
run_mutation_suite.py and validated against the committed report in
tests/test_mutation_report.py instead of re-run on every test pass).
"""

import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.dafny_mutate import (  # noqa: E402
    generate_aor_mutants,
    generate_coi_mutants,
    generate_lor_mutants,
    generate_mutants,
    generate_ror_mutants,
    _tokenize_with_spans,
)

ART_DIR = REPO_ROOT / "examples" / "dosage_calculator"


def _dosage_source():
    return (ART_DIR / "dosage.dfy").read_text()


def test_ror_against_real_spec_produces_expected_raw_and_filtered_counts():
    mutants = generate_ror_mutants(_dosage_source(), "CalculateHourlyDose")
    assert len(mutants) == 35
    filtered = [m for m in mutants if m.filtered_reason]
    assert len(filtered) == 4


def test_ror_filters_only_the_two_equality_clauses_weakening_to_le_ge():
    mutants = generate_ror_mutants(_dosage_source(), "CalculateHourlyDose")
    filtered = [m for m in mutants if m.filtered_reason]
    for m in filtered:
        assert m.keyword == "ensures"
        assert "==" in m.description
        assert m.description.endswith("-> <=") or m.description.endswith("-> >=")


def test_lor_finds_the_single_or_site_and_does_not_filter_it():
    mutants = generate_lor_mutants(_dosage_source(), "CalculateHourlyDose")
    assert len(mutants) == 1
    assert mutants[0].mutated_clause == "infusionRateMlPerHr >= 0.0 && dose == 0.0"
    assert mutants[0].filtered_reason is None


def test_aor_returns_empty_against_real_spec():
    """The real spec's one arithmetic operator lives in ExpectedDose's
    function body, not a requires/ensures clause - out of v1's
    clause-mutation scope (named in evidence/dafny_mutate.py's module
    docstring), so this must return [], not raise or silently skip."""
    assert generate_aor_mutants(_dosage_source(), "CalculateHourlyDose") == []


def test_coi_wraps_every_ensures_clause_and_only_ensures_clauses():
    mutants = generate_coi_mutants(_dosage_source(), "CalculateHourlyDose")
    assert len(mutants) == 3
    for m in mutants:
        assert m.keyword == "ensures"
        assert m.mutated_clause == f"!({m.original_clause})"
        assert m.filtered_reason is None


def test_sor_and_hor_not_applicable_confirmed_by_absence_of_syntax():
    """SOR/HOR aren't implemented at all - this confirms the reason is
    real (checked), not assumed: the spec genuinely contains no set
    syntax and no heap/object-state syntax anywhere."""
    source = _dosage_source()
    for set_marker in ("set<", "iset<", "multiset<", "seq<"):
        assert set_marker not in source
    for heap_marker in ("old(", "fresh(", "allocated(", "reads ", "modifies "):
        assert heap_marker not in source


def test_mutated_source_changes_exactly_the_targeted_operator():
    source = _dosage_source()
    mutants = generate_ror_mutants(source, "CalculateHourlyDose")
    m = next(
        mm
        for mm in mutants
        if mm.keyword == "requires"
        and mm.original_clause == "concentrationMgPerMl > 0.0"
        and mm.description.endswith("-> <")
    )
    assert m.mutated_source != source
    assert len(m.mutated_source) == len(source)
    diff_positions = [
        i for i in range(len(source)) if source[i] != m.mutated_source[i]
    ]
    assert diff_positions, "mutation produced no textual change"
    assert source[diff_positions[0]] == ">"
    assert m.mutated_source[diff_positions[0]] == "<"
    assert diff_positions[-1] == diff_positions[0]


def test_generate_mutants_aggregates_all_four_implemented_classes():
    source = _dosage_source()
    total = len(generate_mutants(source, "CalculateHourlyDose"))
    ror = len(generate_ror_mutants(source, "CalculateHourlyDose"))
    lor = len(generate_lor_mutants(source, "CalculateHourlyDose"))
    aor = len(generate_aor_mutants(source, "CalculateHourlyDose"))
    coi = len(generate_coi_mutants(source, "CalculateHourlyDose"))
    assert total == ror + lor + aor + coi == 39


def test_tokenize_with_spans_handles_function_call_commas():
    tokens = _tokenize_with_spans("dose == ExpectedDose(a, b, c)")
    kinds = [k for k, _v, _s, _e in tokens]
    assert kinds.count("COMMA") == 2
    assert "EQ" in kinds


def test_tokenize_with_spans_refuses_unknown_syntax():
    with pytest.raises(SystemExit, match="unsupported syntax"):
        _tokenize_with_spans("x @ y")


def test_ror_polarity_flips_between_requires_and_ensures():
    """The load-bearing, non-obvious design property: strengthening a
    requires clause is trivial (the original proof still applies under a
    narrower hypothesis) while weakening an ensures clause is trivial
    (whatever already satisfies the original satisfies the weaker
    consequence too) - the OPPOSITE mutation direction is trivial for
    each clause role. Tested against a synthetic spec, independent of
    dosage.dfy's specific content."""
    source = """
    method Foo(x: int) returns (r: int)
      requires x >= 0
      ensures r >= 0
    {
      r := x;
    }
    """
    mutants = generate_ror_mutants(source, "Foo")

    req_to_gt = next(
        m for m in mutants if m.keyword == "requires" and m.description.endswith("-> >")
    )
    assert req_to_gt.filtered_reason is not None, (
        "requires x>=0 -> x>0 is a stronger (narrower) precondition; "
        "trivially covered by whatever already worked for x>=0"
    )

    req_to_lt = next(
        m for m in mutants if m.keyword == "requires" and m.description.endswith("-> <")
    )
    assert req_to_lt.filtered_reason is None, (
        "requires x>=0 -> x<0 admits genuinely new inputs; must be tested"
    )

    ens_to_gt = next(
        m for m in mutants if m.keyword == "ensures" and m.description.endswith("-> >")
    )
    assert ens_to_gt.filtered_reason is None, (
        "ensures r>=0 -> r>0 is NOT implied by r>=0 (r could equal 0); must be tested"
    )
