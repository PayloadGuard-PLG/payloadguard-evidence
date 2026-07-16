"""Phase D, Gate C5: validates the COMMITTED aeb_kernel.dfy mutation
report - the real, captured outcome of every mutant against the real
installed Dafny binary (run_mutation_suite_aeb.py). Does not re-invoke
Dafny, mirroring tests/test_renal_mutation_report.py's exact discipline.

Two real, explained findings from this run, asserted here so a future
change that introduces a genuinely different, unexplained survivor or
unclassifiable mutant fails this test rather than slipping through:

  1. Four survivors, all on IsFalseActivationCompliant's
     `requires peakAdditionalDecelG >= 0.0` precondition (ROR to <=/!=/<,
     LVR to -0.01). This precondition documents a real physical fact
     (deceleration magnitude is non-negative) that the function's single
     ensures clause (`... <==> peakAdditionalDecelG < 0.25`) does not
     actually depend on - the biconditional holds regardless of sign.
     Same category renal_adjustment.dfy's report calls "requires-clause
     weakenings not load-bearing for the specific ensures clause
     currently proven" - real, but not a defect.
  2. Four unclassifiable mutants, all COI (negate ensures clause) on
     FCWRequiredActive/AEBRequiredActive's `target == X ==>` guard
     clauses - Dafny rejects the mutated form with "invalid
     UnaryExpression" (negating a one-way implication whose antecedent is
     itself an equality comparison). A real, named shared-engine gap in
     evidence/dafny_mutate.py's COI generator, same class as
     run_mutation_suite_renal.py's documented &&/|| ambiguity limitation
     - not silently worked around.
"""

import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ART_DIR = REPO_ROOT / "examples" / "aeb_kernel"


def _report():
    return json.loads((ART_DIR / "mutation_report_aeb.json").read_text())


def test_report_total_and_outcome_counts():
    records = _report()
    assert len(records) == 63
    counts = {}
    for r in records:
        counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1
    assert counts == {
        "killed": 38,
        "filtered_static": 12,
        "filtered_magnitude_implied": 5,
        "survived": 4,
        "unclassifiable": 4,
    }


def test_survivors_are_all_false_activation_non_negativity_precondition_weakenings():
    records = _report()
    survivors = [r for r in records if r["outcome"] == "survived"]
    assert len(survivors) == 4
    for r in survivors:
        assert r["function"] == "IsFalseActivationCompliant"
        assert r["keyword"] == "requires"
        assert r["original_clause"] == "peakAdditionalDecelG >= 0.0"
        assert r["operator"] in ("ROR", "LVR")


def test_unclassifiable_are_all_coi_on_target_equality_guard_clauses():
    records = _report()
    unclassifiable = [r for r in records if r["outcome"] == "unclassifiable"]
    assert len(unclassifiable) == 4
    for r in unclassifiable:
        assert r["function"] in ("FCWRequiredActive", "AEBRequiredActive")
        assert r["operator"] == "COI"
        assert r["keyword"] == "ensures"
        assert "==>" in (r["original_clause"] or "")
        assert "invalid UnaryExpression" in r["detail"]
