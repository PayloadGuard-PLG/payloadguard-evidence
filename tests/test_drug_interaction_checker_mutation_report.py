"""Phase E, Gate C5: validates the COMMITTED drug_interaction_checker.dfy
mutation report - the real, captured outcome of every mutant against the
real installed Dafny binary (run_mutation_suite_ddi.py). Does not
re-invoke Dafny, mirroring tests/test_mutation_report.py's/
test_renal_mutation_report.py's exact discipline.

Re-run for real 2026-07-12 after REQ-DDI-6 (DoseReductionTargetMg) was
built on top of REQ-DDI-5, then twice more 2026-07-13 (a Qodo review
fix, then a Gate C6 review's Fix 2A) - see the three-part history below.
Every survivor and unclassifiable result is explained and categorized
here, not silently accepted as "some mutants survived" - a future
change that introduces a genuinely different, unexplained result should
fail this test, not slip through.

**Run 1 (2026-07-12):** 1178 mutants - 634 killed, 472 filtered_static,
68 survived, 4 unclassifiable. CheckInteraction's 31 survivors (28
REQ-DDI-5 indication-disjunction + 3 pre-existing SSRIOrSNRI) established
here for the first time; DoseReductionTargetMg contributed 37 (7
requires-clause + 30 ensures-clause) plus all 4 unclassifiable (the
datatype-ordering type-error category REQ-DDI-5 had made disappear,
reappearing via DoseReductionTargetMg's own new requires clause).

**Run 2 (2026-07-13, Qodo review on PR #39):** DoseReductionTargetMg's
wildcard match arm's bare `0` fallback was replaced with `case _ =>
(assert false; 0)`, making Dafny prove that branch unreachable rather
than risk a silently wrong value on an out-of-domain call. Real, positive
side effect: the 7 requires-clause ROR survivors were now ALL KILLED (a
mutated requires clause can admit a pair that falls into the wildcard
arm, defeating the assertion) - 1178 mutants, 641 killed, 472
filtered_static, 61 survived, 4 unclassifiable.

**Run 3 (2026-07-13, Gate C6 review Fix 2A - see
nl_confirmation_drug_interaction_checker_dfy.md's "Addendum 3"):**
`TreatmentIndication` gained a third constructor
(`OrthopaedicVTEProphylaxis`, a real, source-confirmed licensed
indication DoseReductionTargetMg's Dabigatran+Verapamil cell needed to
exclude), and `DoseReductionTargetMg` gained a `treatmentIndication`
parameter with an indication guard on that one cell. Building this
surfaced a real, independent tooling gap, caught before trusting the
first re-run of this fix: writing the new requires/ensures clauses
across multiple physical lines (a natural way to keep line length sane)
made `evidence/dafny_mutate.py`'s clause-site locator silently TRUNCATE
both clauses at the first physical line - `run_mutation_suite_ddi.py`'s
own real run reported only 1171 mutants with the Edoxaban disjuncts and
ensures clauses entirely missing from requires-clause coverage, a
regression in test coverage, not caught by Dafny (all still verified
clean) or by pytest (no assertion pinned the exact mutant *set*, only
counts, and the counts alone didn't obviously signal truncation).
Diagnosed directly: every truncated `original_clause` read exactly
`'(doac == Dabigatran && agent == Verapamil'`, cut off before the
indication guard and the `==> ... == 110` consequent. Fixed by
reformatting both clauses to single lines, matching this repo's own
established precedent (`renal_adjustment.dfy`'s equivalent Gate C6 gap,
fixed the same way rather than extending the tool, since no committed
capture yet depended on the multi-line formatting). Re-ran clean:
**1250 mutants - 668 killed, 482 filtered_static, 74 survived, 26
unclassifiable.** The jump in every count reflects real, previously-
missing coverage of the full 5-disjunct requires clause and the full
indication-guarded ensures clause, not a new class of finding -
confirmed below, category by category.
"""

import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ART_DIR = REPO_ROOT / "examples" / "drug_interaction_checker"


def _report():
    return json.loads((ART_DIR / "mutation_report_ddi.json").read_text())


def test_report_total_and_outcome_counts():
    records = _report()
    assert len(records) == 1250
    counts = {}
    for r in records:
        counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1
    assert counts == {
        "killed": 668,
        "filtered_static": 482,
        "survived": 74,
        "unclassifiable": 26,
    }


def test_dose_reduction_target_mg_unclassifiable_results_are_the_same_named_type_error_case_at_full_scale():
    """The datatype-ordering type-error category (ROR mutating <=/>= onto
    a datatype-vs-datatype equality, refused by evidence/dafny_spec_lint.py's
    Z3 translator rather than crashing or guessing) now appears at its
    real, full scale now that the requires clause's truncation bug is
    fixed: 12 datatype comparisons in the fully-scanned requires clause
    (doac==Dabigatran, agent==Verapamil, treatmentIndication==
    AFStrokePrevention, treatmentIndication==RecurrentVTEPrevention,
    doac==Edoxaban x4 - once per disjunct) x 2 ROR variants each (<=, >=)
    = 24, plus 2 new LOR "Ambiguous use of && and ||" parser refusals
    (the mixed &&/|| structure inside the indication-guarded disjunct,
    genuinely ambiguous to Dafny's own parser without explicit
    parentheses, refused rather than guessed - the same discipline this
    tool's own ROR/LOR generators already apply elsewhere) = 26 total,
    all on DoseReductionTargetMg's requires clause, none on
    CheckInteraction."""
    records = _report()
    unclassifiable = [r for r in records if r["outcome"] == "unclassifiable"]
    assert len(unclassifiable) == 26
    for r in unclassifiable:
        assert r["function"] == "DoseReductionTargetMg"
        assert r["keyword"] == "requires"
        assert r["operator"] in ("ROR", "LOR")

    ror = [r for r in unclassifiable if r["operator"] == "ROR"]
    assert len(ror) == 24
    for r in ror:
        assert "must be of a numeric type" in r["detail"]

    lor = [r for r in unclassifiable if r["operator"] == "LOR"]
    assert len(lor) == 2
    for r in lor:
        assert "Ambiguous use of && and ||" in r["detail"]

    check_interaction_unclassifiable = [
        r for r in records if r["function"] == "CheckInteraction" and r["outcome"] == "unclassifiable"
    ]
    assert check_interaction_unclassifiable == []


def test_ddi5_indication_disjunction_survivors_are_a_redundant_guard_not_a_gap():
    """Unchanged by this session's DoseReductionTargetMg extension (28 of
    CheckInteraction's 31 survivors), one set of 7 per REQ-DDI-5 clause
    (Rifampicin/Carbamazepine/Phenytoin/Phenobarbital + Apixaban): ROR (6
    per clause: 2 equality operands x 3 variants) and LOR (1 per clause:
    || -> &&) on `(treatmentIndication == AFStrokePrevention ||
    treatmentIndication == RecurrentVTEPrevention)`. Both named
    indications give the IDENTICAL outcome per the source, and the match
    arm doesn't inspect treatmentIndication's value at all for these four
    cells - so any mutation to this disjunction either narrows which
    inputs the postcondition still claims something about (ROR) or makes
    the antecedent unsatisfiable, hence vacuously true (LOR) - never
    wrong. A structural blind spot against guard-style ==> clauses whose
    consequent happens to be identical across every value the guard
    could distinguish - the same shape as the pre-existing SSRIOrSNRI
    category below, and now also DoseReductionTargetMg's own indication
    guard (tested separately below)."""
    records = _report()
    survivors = [r for r in records if r["outcome"] == "survived" and r["function"] == "CheckInteraction"]

    ddi5_survivors = [
        r for r in survivors
        if "treatmentIndication == AFStrokePrevention" in r["original_clause"]
    ]
    assert len(ddi5_survivors) == 28

    by_agent = {}
    for r in ddi5_survivors:
        for agent in ("Rifampicin", "Carbamazepine", "Phenytoin", "Phenobarbital"):
            if f"agent == {agent}" in r["original_clause"]:
                by_agent.setdefault(agent, []).append(r)
    assert {agent: len(rs) for agent, rs in by_agent.items()} == {
        "Rifampicin": 7,
        "Carbamazepine": 7,
        "Phenytoin": 7,
        "Phenobarbital": 7,
    }
    for r in ddi5_survivors:
        assert "doac == Apixaban" in r["original_clause"]
        assert "InteractionResult(Caution, ThrombosisRisk)" in r["original_clause"]


def test_ensures_survivors_are_a_broadly_true_consequent_not_load_bearing_antecedent():
    """Pre-existing category (3 of CheckInteraction's 31 survivors,
    unchanged this session): ROR on the SSRIOrSNRI/Dabigatran/no-risk-
    factor clause's `doac == Dabigatran` antecedent (mutated to !=, <,
    >). Caution/BleedingRisk is ALREADY separately guaranteed for
    Apixaban/Edoxaban/Rivaroxaban+SSRIOrSNRI by three other ensures
    clauses (unconditional on the flag) -- so whatever set of doac
    values this specific antecedent's mutation ends up matching, the
    consequent holds regardless, confirmed directly against the real
    spec's other ensures clauses, not just argued."""
    records = _report()
    survivors = [r for r in records if r["outcome"] == "survived" and r["function"] == "CheckInteraction"]
    ensures_survivors = [
        r for r in survivors
        if "doac == Dabigatran" in r["original_clause"] and "SSRIOrSNRI" in r["original_clause"]
    ]
    assert len(ensures_survivors) == 3
    for r in ensures_survivors:
        assert "InteractionResult(Caution, BleedingRisk)" in r["original_clause"]

    spec = (ART_DIR / "drug_interaction_checker.dfy").read_text()
    for doac in ("Apixaban", "Edoxaban", "Rivaroxaban"):
        assert (
            f"(doac == {doac} && agent == SSRIOrSNRI) ==> "
            "CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) "
            "== InteractionResult(Caution, BleedingRisk)"
        ) in spec


def test_check_interaction_survivors_unchanged_by_dose_reduction_target_mg_extension():
    """CheckInteraction wasn't touched while extending DoseReductionTargetMg
    with a treatmentIndication parameter (Fix 2A) - its 31 survivors (28
    REQ-DDI-5 + 3 pre-existing SSRIOrSNRI, both tested above) are the
    exact same count as every prior run this session established, not a
    coincidentally-equal but different set."""
    records = _report()
    ci_survivors = [r for r in records if r["outcome"] == "survived" and r["function"] == "CheckInteraction"]
    assert len(ci_survivors) == 31


def test_dose_reduction_target_mg_survivors_are_guard_antecedent_pattern_at_full_scale():
    """43 survivors, all on DoseReductionTargetMg, now that the
    truncation bug (module docstring) no longer hides most of the
    requires clause from mutation testing. Two categories, both the same
    established "guard antecedent, never load-bearing" shape - none on
    the consequent (the pinned mg value's own == comparison), confirmed
    directly below for every survivor, not assumed:

    1. **6 requires-clause ROR survivors**, all on the indication guard's
       own comparisons (`treatmentIndication == AFStrokePrevention`,
       `treatmentIndication == RecurrentVTEPrevention`, 3 ROR variants
       each: !=, <, >). Mutating only the indication sub-condition never
       changes which (doac, agent) pairs the requires clause admits (the
       outer `doac == Dabigatran && agent == Verapamil` conjunct is
       untouched), so the wildcard match arm's `assert false` proof -
       which depends only on (doac, agent) admission, not on
       treatmentIndication's exact bound - remains valid regardless. The
       doac==Dabigatran/agent==Verapamil comparisons THEMSELVES are never
       survivors here (tested in the next function) - only the
       indication sub-condition is redundant in this specific sense.
    2. **37 ensures-clause survivors** (13 on the Dabigatran+Verapamil
       clause - 6 doac/agent antecedent comparisons + 6 indication-guard
       comparisons + 1 LOR; 24 on the four Edoxaban clauses, 6 doac/agent
       antecedent comparisons each): every one leaves the consequent
       (`== 110` or `== 30`) byte-identical, confirmed directly below.

    LVR (the literal itself, 109/111, 29/31) has zero survivors - all 10
    killed, confirmed in test_dose_reduction_target_mg_lvr_mutants_all_killed
    below - proving the five pinned figures are exact, not just roughly
    right."""
    records = _report()
    ddi6_survivors = [r for r in records if r["outcome"] == "survived" and r["function"] == "DoseReductionTargetMg"]
    assert len(ddi6_survivors) == 43

    requires_survivors = [r for r in ddi6_survivors if r["keyword"] == "requires"]
    assert len(requires_survivors) == 6
    for r in requires_survivors:
        assert r["operator"] == "ROR"
        # The mutation touched one of the two indication comparisons
        # specifically (not a doac/agent comparison elsewhere in the same
        # multi-disjunct clause) - detected by the "treatmentIndication =="
        # occurrence count dropping from 2 to 1, not substring presence
        # alone (every mutant's full clause text still contains both
        # indication names regardless of which token was actually mutated).
        assert r["original_clause"].count("treatmentIndication ==") == 2
        assert r["mutated_clause"].count("treatmentIndication ==") == 1

    ensures_survivors = [r for r in ddi6_survivors if r["keyword"] == "ensures"]
    assert len(ensures_survivors) == 37
    for r in ensures_survivors:
        # Every survivor mutates the antecedent (before ==>); the
        # consequent (the pinned mg value's own == comparison) is always
        # untouched - confirmed directly, not assumed, by checking the
        # part after ==> is byte-identical to the original.
        orig_consequent = r["original_clause"].split("==>", 1)[1]
        mut_consequent = r["mutated_clause"].split("==>", 1)[1]
        assert orig_consequent == mut_consequent, r

    dabigatran_ensures = [r for r in ensures_survivors if "Dabigatran" in r["original_clause"]]
    assert len(dabigatran_ensures) == 13
    edoxaban_ensures = [r for r in ensures_survivors if "Edoxaban" in r["original_clause"]]
    assert len(edoxaban_ensures) == 24


def test_dose_reduction_target_mg_doac_agent_requires_comparisons_are_all_killed():
    """Unlike the indication sub-condition (redundant, tested above), the
    requires clause's own doac==Dabigatran/agent==Verapamil and
    doac==Edoxaban comparisons ARE load-bearing: mutating any of them
    genuinely changes which (doac, agent) pairs are admitted, which can
    make the wildcard match arm's `assert false` unprovable (a mutated
    requires clause can admit a pair outside the 5 explicit match cases)
    - so every one of these is killed or unclassifiable (the datatype-
    comparison type-error class, tested separately above), never a
    survivor. This is the real, measured effect of the Qodo-driven
    assert-false fix, confirmed here at the requires clause's full
    scale, not just the single-line-truncated slice the first two runs
    saw."""
    records = _report()
    requires_ror = [
        r for r in records
        if r["function"] == "DoseReductionTargetMg" and r["keyword"] == "requires" and r["operator"] == "ROR"
    ]
    assert len(requires_ror) == 60  # 12 datatype comparisons x 5 ROR variants each
    # doac/agent comparisons: mutation drops a "doac ==" or "agent =="
    # occurrence count, not a "treatmentIndication ==" one.
    doac_agent_mutants = [
        r for r in requires_ror
        if r["original_clause"].count("treatmentIndication ==") == r["mutated_clause"].count("treatmentIndication ==")
    ]
    assert len(doac_agent_mutants) == 50  # 10 doac/agent comparisons x 5 ROR variants
    for r in doac_agent_mutants:
        assert r["outcome"] in ("killed", "unclassifiable"), r


def test_dose_reduction_target_mg_lvr_mutants_all_killed():
    """The 10 clause-level LVR mutants (110->109/111, 30->29/31 x4) are
    ALL killed, none survived - confirmed directly, not assumed from the
    absence of "LVR" in the survivor list above. This is the real proof
    that each pinned figure is exact: a wrong-by-one value is genuinely
    excluded by Dafny, not just consistent with an under-constrained
    spec. Unaffected by the treatmentIndication extension - LVR only
    scans literals adjacent to `==` in ensures clauses, and none of the
    five pinned mg figures moved."""
    records = _report()
    lvr_mutants = [r for r in records if r["function"] == "DoseReductionTargetMg" and r["operator"] == "LVR"]
    assert len(lvr_mutants) == 10
    assert all(r["outcome"] == "killed" for r in lvr_mutants)


def test_all_survivors_are_accounted_for_by_the_three_named_categories():
    """No fourth, unexplained survivor category exists - the 28 REQ-DDI-5
    disjunction survivors, the 3 pre-existing SSRIOrSNRI survivors, and
    the 43 DoseReductionTargetMg guard-antecedent survivors (6 requires +
    37 ensures) add up to the full 74, not just a subset each test
    happens to find."""
    records = _report()
    survivors = [r for r in records if r["outcome"] == "survived"]
    assert len(survivors) == 74

    ddi5 = [r for r in survivors if "treatmentIndication == AFStrokePrevention" in r["original_clause"] and r["function"] == "CheckInteraction"]
    ssri = [r for r in survivors if "doac == Dabigatran" in r["original_clause"] and "SSRIOrSNRI" in r["original_clause"]]
    ddi6 = [r for r in survivors if r["function"] == "DoseReductionTargetMg"]
    assert len(ddi5) + len(ssri) + len(ddi6) == len(survivors)
