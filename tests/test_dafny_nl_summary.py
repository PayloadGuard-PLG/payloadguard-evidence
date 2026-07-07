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

    reverse_flow_line = next(l for l in lines if "infusionRateMlPerHr >= 0.0" in l)
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


def test_refuses_a_multiline_clause_rather_than_dropping_its_continuation():
    """The regression this module's own design guards against: a
    multi-line clause must never silently lose its continuation line -
    caught by comparing against dafny_spec_lint's canonical (multi-line-
    capable) extraction, not just counting clauses."""
    source = """
    method Multi(x: int) returns (r: int)
      requires x > 0
        && x < 100
      ensures r == x
    {
      r := x;
    }
    """
    with pytest.raises(SystemExit, match="single-line"):
        summarize_method(source, "Multi")


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
