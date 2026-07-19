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
    generate_lvr_mutants,
    generate_mutants,
    generate_ror_mutants,
    _ar_group_incompatible,
    _chain_incompatible,
    _format_literal_mutant,
    _is_int_literal,
    _locate_clause_numeric_literal_sites,
    _locate_clause_sites,
    _locate_function_body_arithmetic_sites,
    _locate_function_body_numeric_literal_sites,
    _lvr_trivial,
    _tokenize_with_spans,
)

ART_DIR = REPO_ROOT / "examples" / "dosage_calculator"


def _dosage_source():
    return (ART_DIR / "dosage.dfy").read_text()


def test_ror_against_real_spec_produces_expected_raw_and_filtered_counts():
    mutants = generate_ror_mutants(_dosage_source(), "CalculateHourlyDose")
    assert len(mutants) == 35
    filtered = [m for m in mutants if m.filtered_reason]
    assert len(filtered) == 10


def test_ror_filters_equality_clauses_and_the_tightened_reverse_flow_clause():
    """The pinning/second-disjunct '==' clauses filter their weakenings to
    <=/>=; REQ-GIP-1-8-1's tightened '>' clause (post Gate C5 fix) filters
    its own weakenings to >=/!= - a proof of `x > 0` universally implies
    both, so the pass-1 filter now catches these before Dafny ever runs
    (previously, when this clause read `>=`, these same two mutations
    were NOT trivial and were real mutation-testing survivors)."""
    mutants = generate_ror_mutants(_dosage_source(), "CalculateHourlyDose")
    filtered = [m for m in mutants if m.filtered_reason and "statically weaker" in m.filtered_reason]
    assert len(filtered) == 6
    for m in filtered:
        assert m.keyword == "ensures"
        assert m.description.endswith("-> <=") or m.description.endswith(
            "-> >="
        ) or m.description.endswith("-> !=")
    reverse_flow_filtered = {
        m.description for m in filtered if "': > ->" in m.description
    }
    assert reverse_flow_filtered == {
        "ROR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': > -> >=",
        "ROR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': > -> !=",
    }


def test_ror_filters_chain_direction_incompatible_mutants_on_the_chained_clause():
    """Built 2026-07-07 from external research: naively mutating one side
    of the chained `0.0 <= dose <= maxSafeDoseMgPerHr` to a descending
    operator (>=, >) produces a Dafny PARSE error, not a semantic test
    (Dafny Reference Manual Sec 5.2.1-5.2.2: chained relational operators
    must stay the same direction). These 4 candidates (2 links x 2
    incompatible operators each) must be filtered before generation
    reaches real verification, not sent to Dafny and misclassified."""
    mutants = generate_ror_mutants(_dosage_source(), "CalculateHourlyDose")
    chain_filtered = [
        m
        for m in mutants
        if m.filtered_reason and "chain-direction incompatible" in m.filtered_reason
    ]
    assert len(chain_filtered) == 4
    for m in chain_filtered:
        assert m.original_clause == "0.0 <= dose <= maxSafeDoseMgPerHr"
        assert m.description.endswith("-> >=") or m.description.endswith("-> >")
    # LT/EQ/NE candidates for the same clause must NOT be chain-filtered -
    # only the direction-incompatible ones.
    same_clause = [m for m in mutants if m.original_clause == "0.0 <= dose <= maxSafeDoseMgPerHr"]
    compatible = [
        m
        for m in same_clause
        if not m.filtered_reason
        or "chain-direction incompatible" not in m.filtered_reason
    ]
    assert len(compatible) == 6  # 2 links x 3 compatible candidates (<, ==, !=)


def test_lor_finds_the_single_or_site_and_does_not_filter_it():
    mutants = generate_lor_mutants(_dosage_source(), "CalculateHourlyDose")
    assert len(mutants) == 1
    assert mutants[0].mutated_clause == "infusionRateMlPerHr > 0.0 && dose == 0.0"
    assert mutants[0].filtered_reason is None


def test_aor_returns_empty_against_real_spec_clauses_alone():
    """No requires/ensures clause of CalculateHourlyDose contains
    arithmetic - confirmed by an empty result, not just left
    unexercised, when no companion function_name is given."""
    assert generate_aor_mutants(_dosage_source(), "CalculateHourlyDose") == []


def test_aor_against_expecteddose_body_restricts_to_plus_minus_only():
    """Built 2026-07-07 from external research: MutDafny's own AOR
    restriction (+/-/* freely interchange; / only with %, not present in
    this spec) means the one `*` in ExpectedDose's body never gets a `/`
    candidate sent to real verification - eliminating the
    division-by-zero false-kill risk named when this was deferred, by
    construction rather than post-hoc attribution."""
    mutants = generate_aor_mutants(
        _dosage_source(), "CalculateHourlyDose", function_name="ExpectedDose"
    )
    assert len(mutants) == 3
    by_target = {m.description.rsplit(" ", 1)[-1]: m for m in mutants}
    assert set(by_target) == {"+", "-", "/"}
    assert by_target["+"].filtered_reason is None
    assert by_target["-"].filtered_reason is None
    assert by_target["/"].filtered_reason is not None
    assert "group incompatible" in by_target["/"].filtered_reason
    for m in mutants:
        assert m.keyword == "function_body"


def test_aor_never_touches_the_method_body_only_the_function_body():
    """Mutation testing perturbs the SPEC (ExpectedDose, referenced by a
    pinning ensures clause), never CalculateHourlyDose's own trusted
    `{...}` implementation, which recomputes the same multiplication but
    must never be mutated."""
    source = _dosage_source()
    mutants = generate_aor_mutants(source, "CalculateHourlyDose", function_name="ExpectedDose")
    for m in mutants:
        # every mutated_source must still contain the METHOD's own body
        # line unchanged - the only multiplication touched is inside
        # ExpectedDose, which appears earlier in the file.
        assert "dose := rawDose;" in m.mutated_source


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


def test_generate_mutants_aggregates_all_five_implemented_classes():
    source = _dosage_source()
    total = len(generate_mutants(source, "CalculateHourlyDose"))
    ror = len(generate_ror_mutants(source, "CalculateHourlyDose"))
    lor = len(generate_lor_mutants(source, "CalculateHourlyDose"))
    aor = len(generate_aor_mutants(source, "CalculateHourlyDose"))
    lvr = len(generate_lvr_mutants(source, "CalculateHourlyDose"))
    coi = len(generate_coi_mutants(source, "CalculateHourlyDose"))
    assert total == ror + lor + aor + lvr + coi == 49


def test_generate_mutants_with_function_name_includes_body_aor_and_lvr():
    source = _dosage_source()
    total = len(generate_mutants(source, "CalculateHourlyDose", function_name="ExpectedDose"))
    assert total == 49 + 3 + 4  # +3 function-body AOR, +4 function-body LVR


def test_tokenize_with_spans_handles_function_call_commas():
    tokens = _tokenize_with_spans("dose == ExpectedDose(a, b, c)")
    kinds = [k for k, _v, _s, _e in tokens]
    assert kinds.count("COMMA") == 2
    assert "EQ" in kinds


def test_tokenize_with_spans_refuses_unknown_syntax():
    with pytest.raises(SystemExit, match="unsupported syntax"):
        _tokenize_with_spans("x @ y")


def test_tokenize_with_spans_handles_assignment_and_semicolon():
    """Needed for function-body scanning (`var rawDose := a * b;`) -
    requires/ensures clauses never contain `:=` or `;`, so this wasn't
    needed before the AOR function-body extension."""
    tokens = _tokenize_with_spans("var rawDose := a * b;")
    kinds = [k for k, _v, _s, _e in tokens]
    assert "ASSIGN" in kinds
    assert "SEMI" in kinds
    assert "STAR" in kinds


def test_chain_incompatible_matches_dafny_direction_rule():
    """Direct unit test of the pure helper, independent of the real
    spec: ascending (</<=) and descending (>/>=) can't mix in one chain;
    EQ/NE are always compatible with either direction; a chain link with
    no directional siblings (empty or all-EQ/NE) is unconstrained."""
    assert _chain_incompatible("GE", ["LE"]) is True
    assert _chain_incompatible("GT", ["LE"]) is True
    assert _chain_incompatible("LT", ["LE"]) is False
    assert _chain_incompatible("EQ", ["LE"]) is False
    assert _chain_incompatible("NE", ["LE"]) is False
    assert _chain_incompatible("GE", ["LT"]) is True  # descending vs ascending
    assert _chain_incompatible("LE", ["GT"]) is True  # ascending vs descending
    assert _chain_incompatible("GT", []) is False  # no siblings, unconstrained
    assert _chain_incompatible("GT", ["EQ", "NE"]) is False  # only neutral siblings


def test_ar_group_incompatible_matches_mutdafny_restriction():
    """Direct unit test of the pure helper: +/-/* freely interchange;
    / is only compatible with % (not present in _AR_TEXT at all), so
    every +/-/*  <-> / crossing is incompatible in both directions."""
    assert _ar_group_incompatible("STAR", "PLUS") is False
    assert _ar_group_incompatible("STAR", "MINUS") is False
    assert _ar_group_incompatible("PLUS", "MINUS") is False
    assert _ar_group_incompatible("STAR", "SLASH") is True
    assert _ar_group_incompatible("SLASH", "STAR") is True
    assert _ar_group_incompatible("SLASH", "PLUS") is True


def test_locate_function_body_arithmetic_sites_finds_exactly_the_one_star():
    source = _dosage_source()
    sites = _locate_function_body_arithmetic_sites(source, "ExpectedDose")
    assert len(sites) == 1
    abs_start, abs_end, kind = sites[0]
    assert kind == "STAR"
    assert source[abs_start:abs_end] == "*"


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


def test_locate_clause_numeric_literal_sites_finds_every_zero_with_correct_role():
    """Every literal in dosage.dfy's real clauses is exactly 0.0, at 5
    sites, each immediately adjacent to a comparison operator - verified
    directly against the real spec, not assumed."""
    source = _dosage_source()
    total_sites = 0
    for keyword in ("requires", "ensures"):
        for _start, _end, code_text in _locate_clause_sites(
            source, "CalculateHourlyDose", keyword
        ):
            sites = _locate_clause_numeric_literal_sites(code_text)
            for _tstart, _tend, value, op_kind, _is_lhs in sites:
                assert value == "0.0"
                assert op_kind in ("LE", "GT", "EQ")
            total_sites += len(sites)
    assert total_sites == 5


def test_locate_clause_numeric_literal_sites_accepts_arithmetic_embedded_literal():
    """Pinning fix, 2026-07-19 (Gate C5 finding against
    renal_adjustment.dfy's RoundHalfUp and CockcroftGaultCrClMlPerMin,
    both of which have real literals in exactly this shape - `140` in
    `(140 - ageYears) as real) == ...` and `0.5` in
    `RoundHalfUp(x) as real) - 0.5 <= x`). This case used to raise
    SystemExit here; that was over-refusal, not correct caution -
    refusing to guess a literal's comparison ROLE (needed only for the
    magnitude-implication static filter) does not require refusing to
    mutate it at all. `1.0` here is adjacent to `+`, and the clause has
    a comparison (`==`) elsewhere, so it's now returned as a legitimate
    site with op_kind/literal_is_lhs both None - the sentinel that
    tells generate_lvr_mutants to send it straight to real verification,
    never statically filter it (see _locate_clause_numeric_literal_sites'
    and generate_lvr_mutants' docstrings for why: an intervening +/-/*//
    can invert or rescale the narrowing/widening direction in ways this
    module does not attempt to infer, so never filtering is the only
    safe choice, not a relaxed one)."""
    sites = _locate_clause_numeric_literal_sites("x == y + 1.0")
    assert len(sites) == 1
    _tstart, _tend, value, op_kind, literal_is_lhs = sites[0]
    assert value == "1.0"
    assert op_kind is None
    assert literal_is_lhs is None


def test_locate_clause_numeric_literal_sites_still_refuses_truly_ambiguous_literal():
    """The narrowed refusal this module still makes after the 2026-07-19
    fix above: a literal adjacent to neither a comparison NOR an
    arithmetic operator - here, a bare function-call argument - has no
    comparison-relevant role established by either recognized case, and
    mutating it would test something categorically different (changing
    what's computed, not a magnitude within a proven relation)."""
    with pytest.raises(
        SystemExit, match="not adjacent to a comparison or arithmetic operator"
    ):
        _locate_clause_numeric_literal_sites("x == Foo(5)")


def test_locate_clause_numeric_literal_sites_still_refuses_when_no_comparison_present():
    """A second still-refused shape: an arithmetic-adjacent literal in a
    clause with NO comparison operator anywhere. The arithmetic-embedded
    exception above requires `has_comparison` precisely so a literal
    genuinely unrelated to any proven relation (e.g. inside a bare
    boolean combinator with no `==`/`<=`/etc.) is not silently accepted
    as a site."""
    with pytest.raises(
        SystemExit, match="not adjacent to a comparison or arithmetic operator"
    ):
        _locate_clause_numeric_literal_sites("SomeBoolFn(y + 1.0)")


def test_locate_function_body_numeric_literal_sites_finds_both_zeros():
    source = _dosage_source()
    sites = _locate_function_body_numeric_literal_sites(source, "ExpectedDose")
    assert len(sites) == 2
    for abs_start, abs_end, value in sites:
        assert value == "0.0"
        assert source[abs_start:abs_end] == "0.0"


def test_lvr_trivial_matches_the_magnitude_implication_principle():
    """Direct unit test of the pure helper, independent of the real
    spec. GT with the literal on the right (`x > L`): increasing L
    narrows (trivial for requires, informative for ensures); decreasing
    L widens (informative for requires, trivial for ensures). LE with
    the literal on the left (`L <= x`, i.e. `x >= L`): same shape as GT.
    EQ/NE: never trivial, regardless of direction or role."""
    assert _lvr_trivial("requires", "GT", False, +0.01) is True  # narrows
    assert _lvr_trivial("requires", "GT", False, -0.01) is False  # widens
    assert _lvr_trivial("ensures", "GT", False, +0.01) is False  # narrows
    assert _lvr_trivial("ensures", "GT", False, -0.01) is True  # widens

    assert _lvr_trivial("ensures", "LE", True, +0.01) is False  # narrows
    assert _lvr_trivial("ensures", "LE", True, -0.01) is True  # widens

    assert _lvr_trivial("requires", "EQ", False, +0.01) is False
    assert _lvr_trivial("ensures", "EQ", False, -0.01) is False
    assert _lvr_trivial("requires", "NE", True, +0.01) is False


def test_lvr_against_real_spec_matches_the_hand_derived_prediction():
    """The scoping session's own hand-worked prediction (roadmap doc's
    Gate C5 LVR sub-plan): 14 raw mutants (7 sites x 2 candidates), 4
    filtered as magnitude-implied, 10 sent to real verification. This
    test locks in the generation-time half of that prediction; the
    real-verification half (all 10 predicted killed) is locked in by
    tests/test_mutation_report.py against the committed real capture."""
    source = _dosage_source()
    mutants = generate_lvr_mutants(source, "CalculateHourlyDose", function_name="ExpectedDose")
    assert len(mutants) == 14
    filtered = [m for m in mutants if m.filtered_reason]
    assert len(filtered) == 4
    for m in filtered:
        assert m.keyword in ("requires", "ensures")
        assert "magnitude-implied" in m.filtered_reason


def test_int_literal_lvr_mutant_stays_int_typed():
    """Real bug found applying this module to renal_adjustment.dfy
    (2026-07-09): formatting an int-typed literal's LVR mutant as a
    decimal (`90.01`) produces a genuine Dafny static type error
    ('arguments to >= must have a common supertype (got int and real)'),
    not a semantic verification result - dosage.dfy's own literals were
    all already real-typed (`0.0`), so this never surfaced before an
    int-typed spec was ever pointed at this module. An int literal's
    mutant must stay an int literal (no decimal point), perturbed by
    +/-1, not +/-0.01."""
    assert _is_int_literal("90") is True
    assert _is_int_literal("0.0") is False
    assert _is_int_literal("18.0") is False
    assert _format_literal_mutant("90", 1) == "91"
    assert _format_literal_mutant("90", -1) == "89"
    assert _format_literal_mutant("0.0", 1) == "0.01"
    assert _format_literal_mutant("0.0", -1) == "-0.01"

    source = """
    function IntBoundary(roundedEgfr: int): bool
      requires roundedEgfr >= 0
      ensures roundedEgfr >= 90 ==> IntBoundary(roundedEgfr) == true
    {
      true
    }
    """
    mutants = generate_lvr_mutants(source, "IntBoundary")
    for m in mutants:
        assert "." not in m.mutated_clause, m.mutated_clause


def test_lvr_mutated_source_changes_exactly_the_targeted_literal():
    source = _dosage_source()
    mutants = generate_lvr_mutants(source, "CalculateHourlyDose")
    m = next(
        mm
        for mm in mutants
        if mm.keyword == "requires"
        and mm.original_clause == "concentrationMgPerMl > 0.0"
        and mm.description.endswith("-> -0.01")
    )
    assert m.mutated_source != source
    assert "-0.01" in m.mutated_source
    # exactly one occurrence changed: splicing "0.0" -> "-0.01" adds 2
    # characters at exactly one place, nowhere else in the file.
    assert len(m.mutated_source) == len(source) + 2
