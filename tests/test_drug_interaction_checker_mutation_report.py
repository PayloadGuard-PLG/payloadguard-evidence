"""Phase E, Gate C5: validates the COMMITTED drug_interaction_checker.dfy
mutation report - the real, captured outcome of every mutant against the
real installed Dafny binary (run_mutation_suite_ddi.py). Does not
re-invoke Dafny, mirroring tests/test_mutation_report.py's/
test_renal_mutation_report.py's exact discipline.

Re-run for real 2026-07-12 after REQ-DDI-5 (the TreatmentIndication
axis) was built: 31 real survivors, all explained and categorized here,
not silently accepted as "some mutants survived" - a future change that
introduces a genuinely different, unexplained survivor should fail this
test, not slip through. The two unclassifiable results from the
pre-REQ-DDI-5 run are gone entirely, not just reduced - see
test_no_unclassifiable_results_since_the_precondition_was_removed below
for why that's a real structural consequence, not a coincidence.
"""

import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ART_DIR = REPO_ROOT / "examples" / "drug_interaction_checker"


def _report():
    return json.loads((ART_DIR / "mutation_report_ddi.json").read_text())


def test_report_total_and_outcome_counts():
    records = _report()
    assert len(records) == 1072
    counts = {}
    for r in records:
        counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1
    assert counts == {
        "killed": 604,
        "filtered_static": 437,
        "survived": 31,
    }


def test_no_unclassifiable_results_since_the_precondition_was_removed():
    """Pre-REQ-DDI-5, this spec had exactly 2 unclassifiable mutants: a
    real Dafny type error from ROR mutating <= / >= onto the ONE requires
    clause's `doac == Apixaban` comparison (datatype values aren't
    numerically ordered). REQ-DDI-5 (built 2026-07-12) removed that
    requires clause entirely - CheckInteraction is now total, no
    precondition at all - so there is no longer anything for that
    mutation to land on. Confirmed here directly (not assumed from the
    requires clause's absence in the source) so a future requires clause
    reintroducing a datatype comparison would be expected to bring this
    category back, not silently pass a stale "0 unclassifiable" belief."""
    records = _report()
    unclassifiable = [r for r in records if r["outcome"] == "unclassifiable"]
    assert unclassifiable == []
    requires_mutants = [r for r in records if r["keyword"] == "requires"]
    assert requires_mutants == []


def test_ddi5_indication_disjunction_survivors_are_a_redundant_guard_not_a_gap():
    """New category (28 of 31 survivors), one set of 7 per newly-built
    REQ-DDI-5 clause (Rifampicin/Carbamazepine/Phenytoin/Phenobarbital +
    Apixaban): ROR (6 per clause: 2 equality operands x 3 variants) and
    LOR (1 per clause: || -> &&) on
    `(treatmentIndication == AFStrokePrevention || treatmentIndication ==
    RecurrentVTEPrevention)`. Both named indications give the IDENTICAL
    outcome per the source, and the match arm doesn't inspect
    treatmentIndication's value at all for these four cells - so any
    mutation to this disjunction either narrows which inputs the
    postcondition still claims something about (ROR) or makes the
    antecedent unsatisfiable, hence vacuously true (LOR) - never wrong,
    since the implementation's actual return value satisfies whatever
    weaker or narrower claim survives. A structural blind spot against
    guard-style ==> clauses whose consequent happens to be identical
    across every value the guard could distinguish - the same shape as
    the pre-existing SSRIOrSNRI category below, newly instantiated for a
    2-constructor enum disjunction instead of a boolean flag."""
    records = _report()
    survivors = [r for r in records if r["outcome"] == "survived"]

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
    """Pre-existing category (3 of 31 survivors, unchanged by REQ-DDI-5):
    ROR on the SSRIOrSNRI/Dabigatran/no-risk-factor clause's
    `doac == Dabigatran` antecedent (mutated to !=, <, >).
    Caution/BleedingRisk is ALREADY separately guaranteed for
    Apixaban/Edoxaban/Rivaroxaban+SSRIOrSNRI by three other ensures
    clauses (unconditional on the flag) -- so whatever set of doac
    values this specific antecedent's mutation ends up matching, the
    consequent holds regardless, confirmed directly against the real
    spec's other ensures clauses, not just argued. A structural blind
    spot against guard-style ==> clauses whose consequent happens to be
    broadly true across cases -- the same category renal_adjustment's
    largest survivor group (39 of 51) fell into."""
    records = _report()
    survivors = [r for r in records if r["outcome"] == "survived"]
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


def test_all_survivors_are_accounted_for_by_the_two_named_categories():
    """No third, unexplained survivor category exists - the 28 REQ-DDI-5
    disjunction survivors plus the 3 pre-existing SSRIOrSNRI survivors
    add up to the full 31, not just a subset each test happens to find."""
    records = _report()
    survivors = [r for r in records if r["outcome"] == "survived"]
    assert len(survivors) == 31

    ddi5 = [r for r in survivors if "treatmentIndication == AFStrokePrevention" in r["original_clause"]]
    ssri = [r for r in survivors if "doac == Dabigatran" in r["original_clause"] and "SSRIOrSNRI" in r["original_clause"]]
    assert len(ddi5) + len(ssri) == len(survivors)
