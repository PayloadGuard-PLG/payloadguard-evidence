"""Phase C, Gate C5: validates the COMMITTED mutation report - the real,
captured outcome of every mutant against the real installed Dafny binary
(run_mutation_suite.py). Does not re-invoke Dafny (that capture is real
and already made; re-running 42 verifications on every test pass would
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
    assert len(records) == 42
    counts = {}
    for r in records:
        counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1
    assert counts == {
        "killed": 31,
        "filtered_static": 6,
        "filtered_chain_incompatible": 4,
        "filtered_ar_group_incompatible": 1,
    }


def test_no_survivors_and_no_unclassifiable_results_remain():
    """2026-07-07: mutation testing originally found 2 real survivors
    (REQ-GIP-1-8-1's `>=` boundary, fixed by tightening to `>`) and 4
    unclassifiable results (chain-direction parse errors, fixed by
    teaching the generator Dafny's chain-direction rule so it never
    generates those candidates in the first place). Both classes are
    gone now, not just reduced - the former "unclassifiable" bucket no
    longer exists at all; the same 4 mutants are now filtered before
    ever reaching Dafny (filtered_chain_incompatible). See
    KNOWN_LIMITATIONS.md's Gate C5 section for the full history."""
    records = _report()
    outcomes = {r["outcome"] for r in records}
    assert "survived" not in outcomes
    assert "unclassifiable" not in outcomes


def test_reverse_flow_clause_weakenings_are_filtered_not_survivors():
    """The two mutations that used to be real survivors before the
    REQ-GIP-1-8-1 tightening are now correctly recognized as statically
    trivial (a proof of `x > 0` universally implies both `x >= 0` and
    `x != 0`) before Dafny is even invoked - itself a mechanical
    confirmation the boundary is tight. This test exists so a future
    regeneration can't let a survivor quietly reappear."""
    records = _report()
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


def test_chained_clause_direction_incompatible_mutants_are_filtered_pre_verification():
    """Built 2026-07-07 from external research: mutating one side of the
    chained `0.0 <= dose <= maxSafeDoseMgPerHr` to a descending operator
    (>=, >) is a genuine Dafny PARSE error (chained comparisons must stay
    direction-consistent, Dafny Reference Manual Sec 5.2.1-5.2.2). These
    4 mutants (2 links x 2 incompatible operators) are now filtered by
    the generator itself, before any Dafny invocation - not sent to
    Dafny and refused post-hoc as "unclassifiable" the way they were
    before this fix."""
    records = _report()
    chain_filtered = [r for r in records if r["outcome"] == "filtered_chain_incompatible"]
    assert len(chain_filtered) == 4
    for r in chain_filtered:
        assert "chain-direction incompatible" in r["detail"]
        assert "0.0 <= dose <= maxSafeDoseMgPerHr" in r["original_clause"]


def test_function_body_aor_mutants_present_and_division_free_candidate_filtered():
    """Built 2026-07-07 from external research: ExpectedDose's function
    body (part of the formal spec, referenced by the pinning ensures
    clause) now gets AOR mutation on its one `*` operator, restricted
    per MutDafny's own group rule - `+`/`-` are real, sent to Dafny (both
    genuinely killed, confirming `*` is load-bearing); `/` is filtered
    before verification, never risking Dafny's division-by-zero check
    producing a false "kill" for the wrong reason."""
    records = _report()
    body_mutants = [r for r in records if r["keyword"] == "function_body"]
    assert len(body_mutants) == 3
    by_op = {r["description"].rsplit(" ", 1)[-1]: r for r in body_mutants}
    assert by_op["+"]["outcome"] == "killed"
    assert by_op["-"]["outcome"] == "killed"
    assert by_op["/"]["outcome"] == "filtered_ar_group_incompatible"
    assert "group incompatible" in by_op["/"]["detail"]


def test_no_mutant_touches_the_calculatehourlydose_method_implementation_body():
    """Mutation testing perturbs the SPEC, never
    CalculateHourlyDose's trusted implementation - every recorded mutant
    comes from a requires/ensures clause, an explicit COI negation of
    one, or ExpectedDose's function body (also spec, not implementation)
    - never CalculateHourlyDose's own `{ ... }` body."""
    records = _report()
    for r in records:
        assert r["keyword"] in ("requires", "ensures", "function_body")


def test_run_manifest_records_real_dafny_version_and_matching_counts():
    manifest = json.loads((ART_DIR / "run_manifest_mutation.json").read_text())
    assert "4.11.0" in manifest["tool_version"]
    assert manifest["total_mutants"] == 42
    assert manifest["counts"] == {
        "killed": 31,
        "filtered_static": 6,
        "filtered_chain_incompatible": 4,
        "filtered_ar_group_incompatible": 1,
    }
