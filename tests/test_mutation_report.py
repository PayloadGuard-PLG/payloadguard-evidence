"""Phase C, Gate C5: validates the COMMITTED mutation report - the real,
captured outcome of every mutant against the real installed Dafny binary
(run_mutation_suite.py). Does not re-invoke Dafny (that capture is real
and already made; re-running 39 verifications on every test pass would
be slow and would let a regenerated report silently drift without a
human noticing) - reads mutation_report.json exactly the way
tests/test_dafny_stp_suite.py and friends read other committed captures.
"""

import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ART_DIR = REPO_ROOT / "examples" / "dosage_calculator"


def _report():
    return json.loads((ART_DIR / "mutation_report.json").read_text())


def test_report_total_and_outcome_counts():
    records = _report()
    assert len(records) == 39
    counts = {}
    for r in records:
        counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1
    assert counts == {
        "killed": 29,
        "filtered_static": 4,
        "survived": 2,
        "unclassifiable": 4,
    }


def test_the_two_real_survivors_are_named_not_silently_lost():
    """A real, understood finding (2026-07-07): at infusionRateMlPerHr ==
    0.0 exactly, real multiplication by zero makes rawDose == 0.0 exactly,
    so dose == 0.0 already holds independent of the `>=` boundary's exact
    operator - `>=`, `!=`, and `>` are all satisfied by this
    implementation at that single point. This is a genuine looseness in
    REQ-GIP-1-8-1's postcondition (the >=0.0 disjunct's own strictness
    isn't independently load-bearing), reported to Steven rather than
    silently 'fixed' in a spec he already signed off on in Gate C6 - see
    KNOWN_LIMITATIONS.md's Gate C5 section for the decision record. This
    test exists so a future regeneration can't make this survivor quietly
    disappear (or newly appear) without a human noticing."""
    records = _report()
    survivors = {r["description"] for r in records if r["outcome"] == "survived"}
    assert survivors == {
        "ROR on ensures clause 'infusionRateMlPerHr >= 0.0 || dose == 0.0': "
        ">= -> !=",
        "ROR on ensures clause 'infusionRateMlPerHr >= 0.0 || dose == 0.0': "
        ">= -> >",
    }


def test_unclassifiable_mutants_are_all_chain_direction_parse_errors():
    """A real, understood mutation-engine gap, not a spec finding: mutating
    only one side of the chained `0.0 <= dose <= maxSafeDoseMgPerHr` to a
    descending operator produces a Dafny PARSE error (chained comparisons
    must stay direction-consistent), not a semantic test. Named and
    refused (Tier 1) rather than misclassified as killed or survived."""
    records = _report()
    unclassifiable = [r for r in records if r["outcome"] == "unclassifiable"]
    assert len(unclassifiable) == 4
    for r in unclassifiable:
        assert "operator chain" in r["detail"]
        assert "0.0 <= dose <= maxSafeDoseMgPerHr" in r["original_clause"]


def test_no_mutant_touches_the_method_implementation_body():
    """Mutation testing perturbs the SPEC, never the trusted
    implementation - every mutated_clause recorded must come from a
    requires/ensures clause or an explicit COI negation of one, never
    from CalculateHourlyDose's own `{ ... }` body."""
    records = _report()
    for r in records:
        assert r["keyword"] in ("requires", "ensures")


def test_run_manifest_records_real_dafny_version_and_matching_counts():
    manifest = json.loads((ART_DIR / "run_manifest_mutation.json").read_text())
    assert "4.11.0" in manifest["tool_version"]
    assert manifest["total_mutants"] == 39
    assert manifest["counts"] == {
        "killed": 29,
        "filtered_static": 4,
        "survived": 2,
        "unclassifiable": 4,
    }
