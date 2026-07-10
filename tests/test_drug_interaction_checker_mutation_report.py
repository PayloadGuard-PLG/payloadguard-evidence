"""Phase E, Gate C5: validates the COMMITTED drug_interaction_checker.dfy
mutation report - the real, captured outcome of every mutant against the
real installed Dafny binary (run_mutation_suite_ddi.py). Does not
re-invoke Dafny, mirroring tests/test_mutation_report.py's/
test_renal_mutation_report.py's exact discipline.

7 real survivors and 2 real unclassifiable results, both explained and
categorized here, not silently accepted as "some mutants survived" - a
future change that introduces a genuinely different, unexplained
survivor should fail this test, not slip through.
"""

import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ART_DIR = REPO_ROOT / "examples" / "drug_interaction_checker"


def _report():
    return json.loads((ART_DIR / "mutation_report_ddi.json").read_text())


def test_report_total_and_outcome_counts():
    records = _report()
    assert len(records) == 962
    counts = {}
    for r in records:
        counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1
    assert counts == {
        "killed": 564,
        "filtered_static": 389,
        "survived": 7,
        "unclassifiable": 2,
    }


def test_unclassifiable_results_are_the_named_type_error_case():
    """Dafny genuinely refuses <= and >= between two datatype (DOAC)
    values with a real type error ("arguments to <= must be of a
    numeric type... instead got DOAC and DOAC") - a real, different
    failure mode from renal_adjustment's own unclassifiable case (a
    parser ambiguity, not a type error). Both are on the one requires
    clause's `doac == Apixaban` comparison."""
    records = _report()
    unclassifiable = [r for r in records if r["outcome"] == "unclassifiable"]
    assert len(unclassifiable) == 2
    for r in unclassifiable:
        assert r["operator"] == "ROR"
        assert r["keyword"] == "requires"
        assert "Apixaban" in r["original_clause"]
        assert "must be of a numeric type" in r["detail"]


def test_survivors_are_all_explained_not_load_bearing_narrowing_or_widening():
    """Category A (4 of 7 survivors): mutations to the ONE requires
    clause (!(doac == Apixaban && agent in {Rifampicin, Carbamazepine,
    Phenytoin, Phenobarbital})) that widen or narrow which inputs are
    excluded. None of the 60 ensures clauses makes any claim about the
    (Apixaban, {those four agents}) region specifically -- the six
    recovered cells' clauses only reference Dabigatran/Edoxaban/
    Rivaroxaban -- so no ensures clause's provability depends on the
    exact shape of this exclusion. Same structural category
    renal_adjustment's own requires-clause survivors fell into
    ("weakenings not load-bearing for the specific ensures clauses
    currently proven")."""
    records = _report()
    survivors = [r for r in records if r["outcome"] == "survived"]
    assert len(survivors) == 7

    requires_survivors = [r for r in survivors if r["keyword"] == "requires"]
    assert len(requires_survivors) == 4
    for r in requires_survivors:
        assert "Apixaban" in r["original_clause"]


def test_ensures_survivors_are_a_broadly_true_consequent_not_load_bearing_antecedent():
    """Category B (3 of 7 survivors): ROR on the SSRIOrSNRI/Dabigatran/
    no-risk-factor clause's `doac == Dabigatran` antecedent (mutated to
    !=, <, >). Caution/BleedingRisk is ALREADY separately guaranteed for
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
    ensures_survivors = [r for r in survivors if r["keyword"] == "ensures"]
    assert len(ensures_survivors) == 3
    for r in ensures_survivors:
        assert "doac == Dabigatran" in r["original_clause"]
        assert "SSRIOrSNRI" in r["original_clause"]
        assert "InteractionResult(Caution, BleedingRisk)" in r["original_clause"]

    spec = (ART_DIR / "drug_interaction_checker.dfy").read_text()
    for doac in ("Apixaban", "Edoxaban", "Rivaroxaban"):
        assert (
            f"(doac == {doac} && agent == SSRIOrSNRI) ==> "
            "CheckInteraction(doac, agent, hasOtherBleedingRiskFactors) "
            "== InteractionResult(Caution, BleedingRisk)"
        ) in spec
