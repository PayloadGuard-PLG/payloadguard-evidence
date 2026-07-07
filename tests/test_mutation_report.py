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
        "filtered_static": 6,
        "unclassifiable": 4,
    }


def test_no_survivors_remain_after_the_req_gip_1_8_1_tightening():
    """2026-07-07: mutation testing originally found 2 real survivors -
    REQ-GIP-1-8-1's `>=` weakened to `!=` or `>` both still verified,
    because real multiplication by exactly 0.0 makes `dose == 0.0` hold
    at that boundary independent of the first disjunct's operator. Steven
    decided to tighten the clause to `>` rather than accept the
    looseness. Confirmed here: after the fix, the same two mutation
    targets are no longer even sent to Dafny - the pass-1 static filter
    now correctly recognizes them as trivial (a proof of `x > 0`
    universally implies both `x >= 0` and `x != 0`), which is itself
    evidence the boundary is now tight. See KNOWN_LIMITATIONS.md's Gate
    C5 section and nl_confirmation_dosage_dfy.md's amendment for the full
    decision record. This test exists so a future regeneration can't let
    a survivor quietly reappear without a human noticing."""
    records = _report()
    assert not [r for r in records if r["outcome"] == "survived"]
    reverse_flow_filtered = {
        r["description"]
        for r in records
        if r["outcome"] == "filtered_static" and "': > ->" in r["description"]
    }
    assert reverse_flow_filtered == {
        "ROR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': "
        "> -> >=",
        "ROR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': "
        "> -> !=",
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
        "filtered_static": 6,
        "unclassifiable": 4,
    }
