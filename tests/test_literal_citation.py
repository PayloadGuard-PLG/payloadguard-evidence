"""Component C: tests for evidence/literal_citation.py - the mechanical
literal-to-source citation gate.

Synthetic cases exercise the harness (literal extraction, both-way
completeness, source verification via the citation gate, malformed-entry
detection); the real assertion runs the committed renal_adjustment manifest
against the actual KDIGO/MHRA/Cockcroft-Gault source texts, so every numeric
constant in that spec is either a verified source quote or an honestly
declared structural/design-decision value - and a future edit that mistypes a
constant, or drops a citation, breaks the build."""

import pathlib

import pytest
import yaml

from evidence.literal_citation import (
    check_example,
    spec_literals,
    verify_literal_citations,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
RENAL_DIR = REPO_ROOT / "examples" / "renal_adjustment"
SOURCES = REPO_ROOT / "sources"


# --------------------------------------------------------------- synthetic

SYNTH = """
// A comment mentioning 2019 and PMID 1244564 - must NOT be treated as constants.
datatype Stage = G1 | G3a  // G1/G3a: the digits here are part of an identifier
function Threshold(x: real): bool
  requires x >= 0.0
  ensures Threshold(x) <==> x >= 145.0  // 145.0 is the real constant
{ x >= 145.0 }
"""


def test_spec_literals_extracts_code_constants_only():
    lits = spec_literals(SYNTH)
    assert "145.0" in lits
    assert "0.0" in lits
    # numbers living only in comments (a year, a PMID) never appear
    assert "2019" not in lits
    assert "1244564" not in lits
    # a digit glued to an identifier (G1, G3a) is not a literal
    assert "1" not in lits
    assert "3" not in lits


def test_unary_signed_literals_keep_their_sign_binary_subtraction_does_not():
    """A unary +/- adjacent to the digits is part of the literal (a sign
    transcription error must be catchable), but binary subtraction is not a
    sign - `>= -0.5` is the negative literal, `x - 0.5` and `x-0.5` are not."""
    assert spec_literals("ensures f(x) >= -0.5") == ["-0.5"]
    assert spec_literals("ensures f(x) == y - 0.5") == ["0.5"]
    assert spec_literals("ensures f(x) == y-0.5") == ["0.5"]
    # a negative literal opening a group, and after a comparison
    assert set(spec_literals("requires -1 <= x < +2")) == {"-1", "+2"}


def test_block_comment_containing_a_line_comment_is_fully_stripped():
    """A `//` inside a `/* */` block must not truncate the block's `*/`,
    leaving comment digits behind as false code literals."""
    src = "function f(x: int): int /* note: threshold 145 // not code */ { 0 }"
    lits = spec_literals(src)
    assert "145" not in lits
    assert lits == ["0"]


def test_source_quote_confirmed_and_not_found():
    manifest = {
        "145.0": {"kind": "source", "source": "s.md", "quote": "less than 145 km/h"},
        "0.0": {"kind": "structural", "note": "non-negativity boundary"},
    }
    # source text that CONTAINS the quote
    ok = verify_literal_citations(SYNTH, manifest, {"s.md": "greater than 10 and less than 145 km/h."})
    assert ok["ok"] is True
    assert ok["not_found"] == []
    # source text that does NOT contain the quote
    bad = verify_literal_citations(SYNTH, manifest, {"s.md": "an unrelated document."})
    assert bad["ok"] is False
    assert "145.0" in bad["not_found"]


def test_uncited_literal_breaks_completeness():
    """A spec constant with no manifest entry is the exact hole this closes."""
    manifest = {"0.0": {"kind": "structural", "note": "boundary"}}
    report = verify_literal_citations(SYNTH, manifest, {})
    assert report["ok"] is False
    assert "145.0" in report["uncited"]


def test_stale_manifest_entry_is_flagged():
    manifest = {
        "145.0": {"kind": "source", "source": "s.md", "quote": "less than 145 km/h"},
        "0.0": {"kind": "structural", "note": "boundary"},
        "999": {"kind": "structural", "note": "not in the spec at all"},
    }
    report = verify_literal_citations(SYNTH, manifest, {"s.md": "less than 145 km/h"})
    assert report["ok"] is False
    assert report["stale"] == ["999"]


def test_malformed_entries_are_flagged():
    manifest = {
        "145.0": {"kind": "source", "source": "s.md"},  # missing quote
        "0.0": {"kind": "structural"},  # missing note
    }
    report = verify_literal_citations(SYNTH, manifest, {"s.md": "less than 145 km/h"})
    assert report["ok"] is False
    assert len(report["malformed"]) == 2


def test_structural_and_design_decision_need_no_source():
    manifest = {
        "145.0": {"kind": "source", "source": "s.md", "quote": "less than 145 km/h"},
        "0.0": {"kind": "design_decision", "note": "an author-chosen tie-break"},
    }
    report = verify_literal_citations(SYNTH, manifest, {"s.md": "less than 145 km/h"})
    assert report["ok"] is True
    dd = next(r for r in report["results"] if r["literal"] == "0.0")
    assert dd["kind"] == "design_decision" and dd["verdict"] == "declared"


# ----------------------------------------------------------- real examples

EXAMPLES_DIR = REPO_ROOT / "examples"

# Every worked example whose numeric constants are now literal-cited. Each
# entry: (spec .dfy, manifest .yaml). All four examples are covered:
# aeb_kernel's constants trace to 49 CFR 571.127 (the FMVSS-127 source text);
# dosage.dfy is fully parameterized, so its only literal is the structural zero.
COMMITTED = {
    "renal_adjustment": ("renal_adjustment.dfy", "literal_citations.yaml"),
    "drug_interaction_checker": ("drug_interaction_checker.dfy", "literal_citations.yaml"),
    "aeb_kernel": ("aeb_kernel.dfy", "literal_citations.yaml"),
    "dosage_calculator": ("dosage.dfy", "literal_citations.yaml"),
}


def _manifest(example, manifest_name):
    return yaml.safe_load((EXAMPLES_DIR / example / manifest_name).read_text())["literals"]


@pytest.mark.parametrize("example", sorted(COMMITTED))
def test_committed_example_every_constant_is_cited_or_declared(example):
    """The real gate: every numeric literal in the spec is accounted for, and
    every source-cited constant's quote is CONFIRMED present in its actual
    source document."""
    dfy, manifest_name = COMMITTED[example]
    report = check_example(
        EXAMPLES_DIR / example / dfy, _manifest(example, manifest_name), SOURCES
    )
    assert report["uncited"] == [], (example, report["uncited"])
    assert report["not_found"] == [], (example, report["not_found"])
    assert report["stale"] == [], (example, report["stale"])
    assert report["malformed"] == [], (example, report["malformed"])
    assert report["ok"] is True


@pytest.mark.parametrize("example", sorted(COMMITTED))
def test_committed_source_quotes_are_contiguous_verbatim_substrings(example):
    """The citation gate normalizes whitespace (deliberately, to survive PDF
    line-wraps - see citation_gate._normalize), so it CONFIRMS a quote even
    when the source wraps it across a newline. But every quote is shown to a
    human as "Source says (verbatim)" in the Component D template, and that
    promise only holds if the displayed string is literally findable in the
    source - a reviewer Ctrl-F-ing a quote that spans a line break would fail.
    This gate enforces the stronger, human-facing property the normalized
    check can't: each source quote is an exact, contiguous substring of its
    source text, not merely a normalized match."""
    _dfy, manifest_name = COMMITTED[example]
    manifest = _manifest(example, manifest_name)
    non_contiguous = []
    for lit, entry in manifest.items():
        if entry.get("kind") != "source":
            continue
        source_text = (SOURCES / entry["source"]).read_text(encoding="utf-8")
        if entry["quote"] not in source_text:
            non_contiguous.append((lit, entry["source"], entry["quote"]))
    assert non_contiguous == [], (
        f"{example}: these source quotes are not contiguous substrings of "
        f"their source (they match only after whitespace normalization, so "
        f"the 'verbatim' promise is broken for a human searching the source): "
        f"{non_contiguous}"
    )


def _renal_manifest():
    return _manifest("renal_adjustment", "literal_citations.yaml")


def test_ddi_dose_targets_are_source_cited_against_the_sps_document():
    """drug_interaction_checker's only numeric constants are REQ-DDI-6's dose
    figures (dabigatran 110 mg, edoxaban 30 mg), both CONFIRMED against the SPS
    interactions source; the unreachable-arm zero is structural."""
    report = check_example(
        EXAMPLES_DIR / "drug_interaction_checker" / "drug_interaction_checker.dfy",
        _manifest("drug_interaction_checker", "literal_citations.yaml"),
        SOURCES,
    )
    by_lit = {r["literal"]: r for r in report["results"]}
    assert by_lit["110"]["kind"] == "source" and by_lit["110"]["verdict"] == "confirmed"
    assert by_lit["30"]["kind"] == "source" and by_lit["30"]["verdict"] == "confirmed"
    assert by_lit["0"]["kind"] == "structural"


def test_renal_source_cited_constants_are_the_kdigo_mhra_cg_numbers():
    """Pin the classification: the safety-critical numbers trace to a source,
    the round-half-up tie-break is a declared design decision (not KDIGO), and
    the domain boundaries are structural."""
    report = check_example(RENAL_DIR / "renal_adjustment.dfy", _renal_manifest(), SOURCES)
    by_lit = {r["literal"]: r for r in report["results"]}
    for gfr in ("90", "89", "60", "59", "45", "44", "30", "29", "15"):
        assert by_lit[gfr]["kind"] == "source" and by_lit[gfr]["verdict"] == "confirmed"
    for cg in ("140", "72.0", "88.4", "0.85"):
        assert by_lit[cg]["kind"] == "source" and by_lit[cg]["verdict"] == "confirmed"
    assert by_lit["0.5"]["kind"] == "design_decision"
    assert by_lit["0.0"]["kind"] == "structural"


def test_aeb_source_constants_trace_to_fmvss_127():
    """aeb_kernel's speed-envelope, onset, and false-activation numbers all
    trace to the codified 49 CFR 571.127 text; the non-negativity boundary is
    structural. This is the first non-medical example to be literal-cited."""
    report = check_example(
        EXAMPLES_DIR / "aeb_kernel" / "aeb_kernel.dfy",
        _manifest("aeb_kernel", "literal_citations.yaml"),
        SOURCES,
    )
    by_lit = {r["literal"]: r for r in report["results"]}
    for lit in ("10.0", "145.0", "73.0", "0.15", "0.05", "11.0", "0.25"):
        assert by_lit[lit]["kind"] == "source" and by_lit[lit]["verdict"] == "confirmed"
    assert by_lit["0.0"]["kind"] == "structural"


def test_dosage_only_literal_is_the_structural_zero():
    """dosage.dfy is fully parameterized - concentration, rate and the safe
    ceiling are all inputs - so it transcribes no source threshold at all; its
    single code literal is the reverse-flow/non-negativity zero."""
    manifest = _manifest("dosage_calculator", "literal_citations.yaml")
    report = check_example(
        EXAMPLES_DIR / "dosage_calculator" / "dosage.dfy", manifest, SOURCES
    )
    assert [r["literal"] for r in report["results"]] == ["0.0"]
    assert report["results"][0]["kind"] == "structural"
    assert report["ok"] is True


def test_renal_gate_catches_a_mistyped_constant():
    """Demonstrates the point: mutate a spec constant (90 -> 91) and the gate
    flags 91 as uncited - the transcription error Dafny itself can't catch."""
    tampered = (RENAL_DIR / "renal_adjustment.dfy").read_text().replace(
        "roundedEgfr >= 90", "roundedEgfr >= 91"
    )
    manifest = _renal_manifest()
    source_texts = {
        e["source"]: (SOURCES / e["source"]).read_text()
        for e in manifest.values()
        if e.get("kind") == "source"
    }
    report = verify_literal_citations(tampered, manifest, source_texts)
    assert "91" in report["uncited"]
    assert report["ok"] is False
