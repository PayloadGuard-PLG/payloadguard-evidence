"""Phase C, Gate C6: NL-dialogue confirmation - the plain-English summary
generator that feeds the human sign-off step.
"""

import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.dafny_nl_summary import summarize_method  # noqa: E402

ART_DIR = REPO_ROOT / "examples" / "dosage_calculator"


def test_real_dosage_spec_summary_lists_parameters():
    source = (ART_DIR / "dosage.dfy").read_text()
    summary = summarize_method(source, "CalculateHourlyDose")
    assert "`concentrationMgPerMl`: real" in summary
    assert "`infusionRateMlPerHr`: real" in summary
    assert "`maxSafeDoseMgPerHr`: real" in summary


def test_real_dosage_spec_summary_lists_preconditions_verbatim():
    source = (ART_DIR / "dosage.dfy").read_text()
    summary = summarize_method(source, "CalculateHourlyDose")
    assert "`concentrationMgPerMl > 0.0`" in summary
    assert "`maxSafeDoseMgPerHr > 0.0`" in summary


def test_real_dosage_spec_summary_cites_the_right_requirement_per_postcondition():
    """The load-bearing property: each postcondition's citation must
    match what the source itself declares, not be inferred or guessed."""
    source = (ART_DIR / "dosage.dfy").read_text()
    summary = summarize_method(source, "CalculateHourlyDose")
    lines = summary.splitlines()

    bounds_line = next(l for l in lines if "0.0 <= dose <= maxSafeDoseMgPerHr" in l)
    assert "REQ-GIP-1-4-12" in bounds_line

    reverse_flow_line = next(l for l in lines if "infusionRateMlPerHr > 0.0" in l)
    assert "REQ-GIP-1-8-1" in reverse_flow_line

    pinning_line = next(l for l in lines if "dose == ExpectedDose" in l)
    assert "no requirement cited" in pinning_line
    assert "REQ-GIP" not in pinning_line


def test_gloss_renders_common_operators_as_words():
    source = """
    method Simple(x: int, y: int) returns (r: bool)
      requires x > 0 && y > 0
      ensures r == (x <= y)
    {
      r := x <= y;
    }
    """
    summary = summarize_method(source, "Simple")
    assert "x is greater than 0 and y is greater than 0" in summary


def test_multiline_clause_is_summarized_correctly_not_refused():
    """Real gap found 2026-07-10 building Gate C6 for
    drug_interaction_checker.dfy: its one requires clause is the first
    genuinely multi-line clause this repo has built against (every clause
    in dosage.dfy/renal_adjustment.dfy happened to be one line). Before
    this fix, summarize_method refused outright on any multi-line clause
    rather than risk dropping its continuation - now it assembles the
    full clause correctly, still verified byte-for-byte against
    dafny_spec_lint's canonical multi-line-capable extractor (the
    original regression-protection intent, preserved: a dropped or
    truncated continuation still fails this test, it just no longer does
    so via a blanket refusal)."""
    source = """
    method Multi(x: int) returns (r: int)
      requires x > 0
        && x < 100
      ensures r == x
    {
      r := x;
    }
    """
    summary = summarize_method(source, "Multi")
    assert "`x > 0 && x < 100`" in summary


def test_standalone_comment_inside_a_multiline_clause_still_refuses():
    """A multi-line clause's continuation lines are only ever joined up to
    the first blank line, standalone `//`-comment line, or next clause
    keyword - deliberately, so a free-floating block comment BETWEEN two
    clauses is never misattributed as either one's citation (the common
    shape in this repo's own specs). The cost of that choice: a comment
    sitting on its own line INSIDE a multi-line boolean expression
    (rather than between two clauses) genuinely orphans the continuation
    lines after it, producing a truncated clause that no longer matches
    dafny_spec_lint's canonical extraction - correctly caught by the
    existing cross-check and refused, not silently misparsed."""
    source = """
    method Split(x: int) returns (r: int)
      requires x > 0
        // an explanatory comment stuck mid-expression, not at the end
        && x < 100
      ensures r == x
    {
      r := x;
    }
    """
    with pytest.raises(SystemExit, match="could not exactly reconstruct"):
        summarize_method(source, "Split")


def test_real_ddi_spec_multiline_requires_clause_summarizes_correctly():
    """End-to-end confirmation against the real, committed spec that
    motivated this extension: CheckInteraction's one requires clause
    spans three physical lines and carries no inline REQ-ID citation (a
    real, notable fact about this function worth surfacing at sign-off -
    unlike dosage.dfy/renal_adjustment.dfy, none of this spec's clauses
    cite a per-clause REQ-ID; the source is validated as a whole table
    instead)."""
    source = (DDI_ART_DIR / "drug_interaction_checker.dfy").read_text()
    summary = summarize_method(source, "CheckInteraction")
    assert (
        "`!(doac == Apixaban && (agent == Rifampicin || agent == Carbamazepine "
        "|| agent == Phenytoin || agent == Phenobarbital))`" in summary
    )


def test_method_with_no_requires_or_ensures_still_summarizes():
    source = """
    method Bare(x: int) returns (r: int)
    {
      r := x;
    }
    """
    summary = summarize_method(source, "Bare")
    assert "(none declared)" in summary


def test_summary_is_deterministic():
    """No timestamps, no randomness - the same source always produces
    byte-identical output, since this feeds a committed, reviewable
    artifact."""
    source = (ART_DIR / "dosage.dfy").read_text()
    assert summarize_method(source, "CalculateHourlyDose") == summarize_method(
        source, "CalculateHourlyDose"
    )


# --------------------------------------- function support (2026-07-08)
# renal_adjustment.dfy's Gate C6 pass surfaced two real gaps in this
# module that dosage.dfy's single method never exercised: it only
# matched `method`, not `function` declarations, and its REQ-ID regex
# silently truncated a lowercase-suffixed ID (REQ-RENAL-1a -> REQ-RENAL-1)
# instead of citing it correctly. Both are fixed; these are the
# regression tests for each.

RENAL_ART_DIR = REPO_ROOT / "examples" / "renal_adjustment"
DDI_ART_DIR = REPO_ROOT / "examples" / "drug_interaction_checker"


def test_summarizes_a_function_not_just_a_method():
    """The real gap: _find_method_header only matched `method` until
    this fix - every real Dafny function in this repo before
    renal_adjustment.dfy was a companion to a method (ExpectedDose next
    to CalculateHourlyDose), so summarize_method was never actually
    asked to summarize a function directly until now."""
    source = (RENAL_ART_DIR / "renal_adjustment.dfy").read_text()
    summary = summarize_method(source, "RoundHalfUp")
    assert "`x`: real" in summary
    assert "`x >= 0.0`" in summary


def test_lowercase_suffixed_req_id_is_cited_in_full_not_truncated():
    """The real bug: REQ-RENAL-1a was silently cited as REQ-RENAL-1
    (the trailing lowercase 'a' dropped by the old [A-Z0-9-] character
    class) before this fix - a genuine citation-accuracy defect, not a
    hypothetical, caught by Gate C6 actually running against a second
    real spec."""
    source = (RENAL_ART_DIR / "renal_adjustment.dfy").read_text()
    summary = summarize_method(source, "RoundHalfUp")
    assert "REQ-RENAL-1a" in summary
    assert "REQ-RENAL-1]" not in summary.replace("REQ-RENAL-1a]", "")


def test_all_five_renal_functions_summarize_without_error():
    """Every function in the real, committed renal_adjustment.dfy
    summarizes cleanly - the concrete end-to-end confirmation for Gate
    C6's own sign-off document, not just a synthetic fixture."""
    source = (RENAL_ART_DIR / "renal_adjustment.dfy").read_text()
    for name in ("RoundHalfUp", "GStage", "SelectFormula", "ComposedCeiling", "AssessRenalFunction"):
        summary = summarize_method(source, name)
        assert f"`{name}`" in summary
