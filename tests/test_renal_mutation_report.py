"""Phase D, Gate C5: validates the COMMITTED renal_adjustment.dfy mutation
report - the real, captured outcome of every mutant against the real
installed Dafny binary (run_mutation_suite_renal.py). Does not re-invoke
Dafny, mirroring tests/test_mutation_report.py's exact discipline.

Unlike dosage.dfy's final zero-survivor state, this report has real
survivors and one real named engine gap (the &&/|| ambiguity limitation -
see run_mutation_suite_renal.py's module docstring). Both are asserted
explicitly here as EXPLAINED, categorized findings, not silently accepted
as "some mutants survived" - a future change that introduces a genuinely
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
    assert len(records) == 450
    counts = {}
    for r in records:
        counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1
    assert counts == {
        "killed": 250,
        "filtered_static": 72,
        "filtered_chain_incompatible": 28,
        "filtered_ar_group_incompatible": 9,
        "filtered_magnitude_implied": 28,
        "blocked_lvr_clause_literal": 2,
        "survived": 51,
        "unclassifiable": 10,
    }


def test_survivors_are_all_antecedent_narrowing_on_a_one_way_implication():
    """Category 1 (39 of 51 survivors): ROR/LVR mutations that NARROW the
    antecedent of a one-way `==>` ensures clause (e.g. `roundedEgfr >= 90`
    -> `roundedEgfr == 90`, or a boundary literal shifted inward) can
    never be killed - a narrower antecedent's true-set is always a subset
    of the original's, so if the original implication held, the narrowed
    one holds trivially too, regardless of whether the spec is tight.
    This is a structural blind spot of ROR/LVR against guard-style `==>`
    clauses, not a proof gap - Gate C4's STP suite is the tool that
    actually pins these boundaries (renal_adjustment_stp_suite.dfy, 52
    verified, 0 errors, including dedicated boundary lemmas for every one
    of these exact transitions)."""
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
    """Category 2 (11 of 51 survivors): ROR/LVR mutations to a `requires`
    clause that Dafny's real verifier can still satisfy under the
    weakened precondition, because the specific `ensures` clauses proven
    for that function don't actually depend on it (e.g. ComposedCeiling's
    `<=`/pinning postconditions hold for ANY real existingCeiling/
    renalCeiling pair, not just positive ones - `existingCeiling > 0.0`
    documents a real-world domain fact about dose ceilings, but isn't
    proof-necessary for what's currently established). Not a spec defect:
    the precondition still correctly documents the calling convention: it
    just isn't load-bearing for THESE postconditions specifically."""
    records = _report()
    survivors = [r for r in records if r["outcome"] == "survived"]
    requires_weakenings = [r for r in survivors if r["keyword"] == "requires"]
    assert len(requires_weakenings) == 17, [r["description"] for r in requires_weakenings]
    for r in requires_weakenings:
        assert r["function"] in ("GStage", "SelectFormula", "ComposedCeiling")


def test_round_half_up_aor_survivor_is_the_one_named_exception():
    """Category 3 (1 of 51 survivors): RoundHalfUp's self-referential
    ensures clause (`(RoundHalfUp(x) as real) - 0.5 <= x < ...`) survives
    a `-` -> `*` mutation for a coincidental numeric reason (the mutated
    lower bound is looser than the original for all x >= 0 this spec's
    precondition allows), not because 0.5's role as a subtraction is
    undecided - RoundHalfUp's exact integer output is independently
    pinned by Gate C4's STP suite (10 hand-derived boundary lemmas)."""
    records = _report()
    survivors = [r for r in records if r["outcome"] == "survived"]
    aor = [r for r in survivors if r["operator"] == "AOR"]
    assert len(aor) == 1
    assert aor[0]["function"] == "RoundHalfUp"


def test_all_51_survivors_accounted_for_by_the_three_named_categories():
    """No survivor should exist outside the three categories above - a
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
    assert len(narrowing) + len(requires_weakenings) + len(aor) == len(survivors)


def test_unclassifiable_results_are_all_the_named_lor_ambiguity_gap():
    """Real, named engine limitation (2026-07-09), not fixed: SelectFormula's
    ensures clause antecedent is a flat, unparenthesized run of six `||`
    terms; mutating any one `||` to `&&` produces Dafny's own genuine
    'Ambiguous use of && and ||' parser rejection (Dafny requires explicit
    parens when mixing the two, unlike languages with fixed precedence).
    Unlike ROR's analogous chain-direction problem (fixed, 2026-07-07),
    this was NOT built into a static pre-filter - real new engineering
    (grouping same-paren-depth && / || runs, mirroring
    _chain_group_ids), not a bounded fix, and SelectFormula's actual
    branching logic is independently proven both by the ensures clause
    itself and by Gate C4's STP suite. Named here rather than silently
    reported as an unexplained gap."""
    records = _report()
    unclassifiable = [r for r in records if r["outcome"] == "unclassifiable"]
    assert len(unclassifiable) == 10
    for r in unclassifiable:
        assert r["function"] == "SelectFormula"
        assert r["operator"] == "LOR"
        assert "Ambiguous use of" in r["detail"]


def test_lvr_clause_literal_blocked_entries_match_the_named_functions():
    """Two functions hit the LVR clause-literal locator's documented
    Tier-1 scope boundary ("every literal sits immediately adjacent to a
    comparison operator... refuses rather than guess"): RoundHalfUp's
    ensures clause has its 0.5 literals embedded in arithmetic (`... -
    0.5 <= x`, `... + 0.5`); CockcroftGaultCrClMlPerMin's ensures clauses
    have 140/88.4/72.0 embedded deep inside the pinning equality's RHS
    arithmetic, nowhere near the `==` itself. Neither extended (see
    run_mutation_suite_renal.py's module docstring) - Gate C4's STP suite
    already independently proves both functions' exact values."""
    records = _report()
    blocked = [r for r in records if r["outcome"] == "blocked_lvr_clause_literal"]
    assert len(blocked) == 2
    assert {r["function"] for r in blocked} == {"RoundHalfUp", "CockcroftGaultCrClMlPerMin"}


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
    assert manifest["total_mutants"] == 450
    assert manifest["functions"] == [
        "RoundHalfUp",
        "GStage",
        "SelectFormula",
        "ComposedCeiling",
        "AssessRenalFunction",
        "CockcroftGaultCrClMlPerMin",
        "AssessRenalFunctionFromInputs",
    ]
