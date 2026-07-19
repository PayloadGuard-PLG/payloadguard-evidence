"""Phase D, Gate C5: validates the COMMITTED renal_adjustment.dfy mutation
report - the real, captured outcome of every mutant against the real
installed Dafny binary (run_mutation_suite_renal.py). Does not re-invoke
Dafny, mirroring tests/test_mutation_report.py's exact discipline.

This report is produced with two accuracy mechanisms in place (both
2026-07-19): every mutant is verified against the mutated function in
ISOLATION (its own callees + datatypes, never its callers - see
evidence/dafny_isolate.py) so a kill is attributable to the function's
own contract rather than a downstream caller failing to discharge the
mutated precondition; and the LVR generator now covers arithmetic-
embedded clause literals (evidence/dafny_mutate.py fixes 4a/4b) that it
formerly refused. Combined with two spec tightenings (RoundHalfUp gains
`ensures ... >= 0`, ComposedCeiling gains `ensures ... > 0.0`), the
previously-surviving precondition mutants of those two functions are now
killed for the right reason - at the function's own contract, in
isolation.

Real survivors and one real named engine gap (the &&/|| ambiguity
limitation) remain, both asserted explicitly here as EXPLAINED,
categorized findings - a future change that introduces a genuinely
different, unexplained survivor should fail this test, not slip through.
"""

import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ART_DIR = REPO_ROOT / "examples" / "renal_adjustment"


def _report():
    return json.loads((ART_DIR / "mutation_report_renal.json").read_text())


def test_report_total_and_outcome_counts():
    records = _report()
    assert len(records) == 504
    counts = {}
    for r in records:
        counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1
    assert counts == {
        "killed": 294,
        "filtered_static": 74,
        "filtered_chain_incompatible": 28,
        "filtered_ar_group_incompatible": 9,
        "filtered_magnitude_implied": 36,
        "survived": 53,
        "unclassifiable": 10,
    }
    # The LVR generator no longer refuses arithmetic-embedded clause
    # literals (fixes 4a/4b), so the former placeholder outcome is gone.
    assert "blocked_lvr_clause_literal" not in counts


def test_verified_mutants_are_recorded_as_isolated():
    """Every mutant that reached real Dafny verification (i.e. was not
    statically filtered or pre-empted by the vacuous-precondition check)
    carries isolation_status == 'isolated' - the caller-confound fix is
    applied uniformly, not selectively."""
    records = _report()
    verified = [r for r in records if r["outcome"] in ("killed", "survived", "unclassifiable")]
    assert verified
    for r in verified:
        assert r.get("isolation_status") == "isolated", r["description"]


def test_survivors_are_all_antecedent_narrowing_on_a_one_way_implication():
    """Category 1 (33 of 53 survivors): ROR/LVR mutations that NARROW the
    antecedent of a one-way `==>` ensures clause (e.g. `roundedEgfr >= 90`
    -> `roundedEgfr == 90`, or a boundary literal shifted inward) can
    never be killed - a narrower antecedent's true-set is always a subset
    of the original's, so if the original implication held, the narrowed
    one holds trivially too, regardless of whether the spec is tight.
    This is a structural blind spot of ROR/LVR against guard-style `==>`
    clauses, not a proof gap - Gate C4's STP suite is the tool that
    actually pins these boundaries."""
    records = _report()
    survivors = [r for r in records if r["outcome"] == "survived"]
    narrowing = [
        r for r in survivors
        if r["operator"] in ("ROR", "LVR")
        and "==>" in (r["original_clause"] or "")
    ]
    assert len(narrowing) == 33, [r["description"] for r in narrowing]
    for r in narrowing:
        assert r["function"] in ("GStage", "SelectFormula")


def test_survivors_are_all_requires_clause_weakenings_not_load_bearing():
    """Category 2 (17 of 53 survivors): ROR/LVR mutations to a `requires`
    clause that Dafny's real verifier can still satisfy under the weakened
    precondition, because the specific `ensures` clauses proven for that
    function don't depend on it. Note which functions are and are NOT
    here: ComposedCeiling's precondition weakenings used to be in this
    category and are now KILLED (the added `ensures ... > 0.0` made
    `requires ... > 0.0` load-bearing); RoundHalfUp's three qualitative
    precondition weakenings are likewise now killed (the added `ensures
    RoundHalfUp(x) >= 0`). What remains here is genuinely not load-bearing
    for the current postconditions: RoundHalfUp's LVR-scale weakening
    (`x >= -0.01`, since RoundHalfUp(x)=0 for x in [-0.01,0) still
    satisfies `>= 0`) and CockcroftGaultCrClMlPerMin's lower-bound-on-
    ageYears weakenings (its equality-pinning ensures work for any int;
    only the UPPER bound `< 140` is proof-necessary)."""
    records = _report()
    survivors = [r for r in records if r["outcome"] == "survived"]
    requires_weakenings = [r for r in survivors if r["keyword"] == "requires"]
    assert len(requires_weakenings) == 17, [r["description"] for r in requires_weakenings]
    for r in requires_weakenings:
        assert r["function"] in (
            "GStage", "SelectFormula", "RoundHalfUp", "CockcroftGaultCrClMlPerMin",
        )
    # The tightening's whole point: neither ComposedCeiling nor a
    # confounded RoundHalfUp qualitative weakening survives here anymore.
    assert not any(r["function"] == "ComposedCeiling" for r in requires_weakenings)


def test_round_half_up_aor_survivor_is_the_one_named_exception():
    """Category 3 (1 of 53 survivors): RoundHalfUp's self-referential
    ensures clause (`(RoundHalfUp(x) as real) - 0.5 <= x < ...`) survives
    a `-` -> `*` mutation for a coincidental numeric reason (the mutated
    lower bound is looser than the original for all x >= 0 this spec's
    precondition allows), not because 0.5's role as a subtraction is
    undecided - RoundHalfUp's exact integer output is independently pinned
    by Gate C4's STP suite."""
    records = _report()
    survivors = [r for r in records if r["outcome"] == "survived"]
    aor = [r for r in survivors if r["operator"] == "AOR"]
    assert len(aor) == 1
    assert aor[0]["function"] == "RoundHalfUp"


def test_round_half_up_ensures_lvr_widening_survivors_are_the_named_pair():
    """Category 4 (2 of 53 survivors): now that the LVR generator covers
    RoundHalfUp's arithmetic-embedded ensures literal (fix 4a), widening
    the rounding tolerance `0.5 -> 0.51` in `(RoundHalfUp(x) as real) -
    0.5 <= x < (RoundHalfUp(x) as real) + 0.5` survives - a looser
    tolerance is still satisfied by the exact round-half-up body. A sound
    consequence, not a spec gap; the exact value is pinned by Gate C4.
    These are the two literal occurrences (lower and upper bound)."""
    records = _report()
    survivors = [r for r in records if r["outcome"] == "survived"]
    rhu_ensures_lvr = [
        r for r in survivors
        if r["function"] == "RoundHalfUp"
        and r["operator"] == "LVR"
        and r["keyword"] == "ensures"
    ]
    assert len(rhu_ensures_lvr) == 2, [r["description"] for r in rhu_ensures_lvr]


def test_all_53_survivors_accounted_for_by_the_four_named_categories():
    """No survivor should exist outside the four categories above - a
    future spec change producing a genuinely new, unexplained survivor
    must fail this test, not blend into an unexamined total."""
    records = _report()
    survivors = [r for r in records if r["outcome"] == "survived"]
    narrowing = [
        r for r in survivors
        if r["operator"] in ("ROR", "LVR") and "==>" in (r["original_clause"] or "")
    ]
    requires_weakenings = [r for r in survivors if r["keyword"] == "requires"]
    aor = [r for r in survivors if r["operator"] == "AOR"]
    rhu_ensures_lvr = [
        r for r in survivors
        if r["function"] == "RoundHalfUp" and r["operator"] == "LVR" and r["keyword"] == "ensures"
    ]
    assert len(narrowing) + len(requires_weakenings) + len(aor) + len(rhu_ensures_lvr) == len(survivors)


def test_unclassifiable_results_are_all_the_named_lor_ambiguity_gap():
    """Real, named engine limitation (2026-07-09), not fixed: SelectFormula's
    ensures clause antecedent is a flat, unparenthesized run of six `||`
    terms; mutating any one `||` to `&&` produces Dafny's own genuine
    'Ambiguous use of && and ||' parser rejection. Named here rather than
    silently reported as an unexplained gap."""
    records = _report()
    unclassifiable = [r for r in records if r["outcome"] == "unclassifiable"]
    assert len(unclassifiable) == 10
    for r in unclassifiable:
        assert r["function"] == "SelectFormula"
        assert r["operator"] == "LOR"
        assert "Ambiguous use of" in r["detail"]


def test_no_mutant_touches_a_function_body_other_than_the_two_named():
    """AOR/LVR body mutation is scoped to exactly RoundHalfUp and
    CockcroftGaultCrClMlPerMin - the only two functions with arithmetic
    operators or numeric literals in their own bodies (see
    run_mutation_suite_renal.py's module docstring)."""
    records = _report()
    body_mutants = [r for r in records if r["keyword"] == "function_body"]
    assert body_mutants
    for r in body_mutants:
        assert r["function"] in ("RoundHalfUp", "CockcroftGaultCrClMlPerMin")


def test_run_manifest_records_real_dafny_version_and_matching_counts():
    manifest = json.loads((ART_DIR / "run_manifest_mutation_renal.json").read_text())
    assert "4.11.0" in manifest["tool_version"]
    assert manifest["total_mutants"] == 504
    assert manifest["functions"] == [
        "RoundHalfUp",
        "GStage",
        "SelectFormula",
        "ComposedCeiling",
        "AssessRenalFunction",
        "CockcroftGaultCrClMlPerMin",
        "AssessRenalFunctionFromInputs",
    ]
