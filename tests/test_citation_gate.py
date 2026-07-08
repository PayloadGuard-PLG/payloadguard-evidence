"""Citation gate: regression fixtures are the actual claims and actual
source text this session verified by hand, not synthetic examples - see
evidence/citation_gate.py's module docstring for the two real
fabrication events these encode.
"""

import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.citation_gate import (  # noqa: E402
    CitationClaim,
    verify_citation,
    verify_citations,
)

# Real source text, as actually fetched/extracted this session - see
# sources/mhra-renal-formula-selection-2019.md (NICE fetch) and
# sources/kdigo-2024-gfr-staging.md (KDIGO PDF extraction) for the
# original citations these strings are drawn from.

NICE_NG203_1_1_2_REAL = (
    "1.1.2 use the Chronic Kidney Disease Epidemiology Collaboration "
    "(CKD-EPI) creatinine equation to estimate GFRcreatinine for adults, "
    "using creatinine assays with calibration traceable to standardised "
    "reference material"
)

NICE_NG203_1_1_4_REAL = (
    "1.1.4 Advise adults not to eat any meat in the 12 hours before "
    "having a blood test for eGFRcreatinine"
)

KDIGO_RECOMMENDATION_1_1_2_1_REAL = (
    "Recommendation 1.1.2.1: In adults at risk for CKD, we recommend "
    "using creatinine-based estimated glomerular filtration rate "
    "(eGFRcr). If cystatin C is available, the GFR category should be "
    "estimated from the combination of creatinine and cystatin C "
    "(creatinine and cystatin C-based estimated glomerular filtration "
    "rate [eGFRcr-cys]) (1B)."
)


def test_confirms_a_real_nice_citation():
    claim = CitationClaim(
        label="NICE NG203 1.1.2",
        claimed_quote="use the Chronic Kidney Disease Epidemiology Collaboration (CKD-EPI) creatinine equation to estimate GFRcreatinine",
        source_text=NICE_NG203_1_1_2_REAL,
    )
    verdict = verify_citation(claim)
    assert verdict.verdict == "CONFIRMED"
    assert verdict.context is not None
    assert "strong evidence" in verdict.caveat.lower()


def test_rejects_the_actual_fabricated_nice_1_1_2_claim():
    """The real event: a supplied document claimed NICE's Recommendation
    1.1.2 "mandates the 2009 equation" - the real 1.1.2 says nothing of
    the sort (see NICE_NG203_1_1_2_REAL above, fetched directly)."""
    claim = CitationClaim(
        label="fabricated: NICE NG203 1.1.2 'mandates the 2009 equation'",
        claimed_quote="mandates the 2009 CKD-EPI equation without ethnicity adjustments",
        source_text=NICE_NG203_1_1_2_REAL,
    )
    verdict = verify_citation(claim)
    assert verdict.verdict == "NOT_FOUND"
    assert verdict.context is None


def test_rejects_the_actual_fabricated_nice_1_1_4_claim():
    """The real event: a supplied document claimed NICE's 1.1.4 says
    "Do not use a person's ethnicity to adjust their eGFR." The real
    1.1.4 is about not eating meat before a blood test."""
    claim = CitationClaim(
        label="fabricated: NICE NG203 1.1.4 ethnicity claim",
        claimed_quote="Do not use a person's ethnicity to adjust their eGFR",
        source_text=NICE_NG203_1_1_4_REAL,
    )
    verdict = verify_citation(claim)
    assert verdict.verdict == "NOT_FOUND"


def test_confirms_the_real_kdigo_recommendation():
    claim = CitationClaim(
        label="KDIGO Recommendation 1.1.2.1",
        claimed_quote="we recommend using creatinine-based estimated glomerular filtration rate (eGFRcr)",
        source_text=KDIGO_RECOMMENDATION_1_1_2_1_REAL,
    )
    verdict = verify_citation(claim)
    assert verdict.verdict == "CONFIRMED"


def test_rejects_the_actual_fabricated_kdigo_claim():
    """The real event: a supplied document claimed KDIGO's "Recommendation
    1.1.2" (wrong number - the real one is 1.1.2.1) states "the explicit
    shift to the 2021 race-free equation." The real recommendation is
    about the eGFRcr-vs-eGFRcr-cys choice, not equation version at all."""
    claim = CitationClaim(
        label="fabricated: KDIGO 'explicit shift to 2021 race-free equation'",
        claimed_quote="explicit shift to the 2021 race-free equation",
        source_text=KDIGO_RECOMMENDATION_1_1_2_1_REAL,
    )
    verdict = verify_citation(claim)
    assert verdict.verdict == "NOT_FOUND"


def test_normalization_survives_whitespace_and_case_differences():
    """The claim need not match the source's exact spacing/casing - PDF
    extraction in this repo has already been observed to produce
    unspaced text (sources/kdigo-2024-gfr-staging.md's extraction
    method note)."""
    claim = CitationClaim(
        label="whitespace/case robustness",
        claimed_quote="ESTIMATED GLOMERULAR FILTRATION RATE (eGFRcr)",
        source_text="...estimatedglomerularfiltrationrate(eGFRcr)...",
    )
    verdict = verify_citation(claim)
    assert verdict.verdict == "CONFIRMED"


def test_does_not_false_positive_on_an_unrelated_short_phrase():
    """Sanity check against the opposite failure mode - the gate
    shouldn't report CONFIRMED just because a short substring happens
    to appear somewhere unrelated."""
    claim = CitationClaim(
        label="unrelated phrase",
        claimed_quote="the sky is blue and the grass is green",
        source_text=NICE_NG203_1_1_2_REAL,
    )
    verdict = verify_citation(claim)
    assert verdict.verdict == "NOT_FOUND"


def test_refuses_a_vacuous_empty_claim():
    claim = CitationClaim(label="empty", claimed_quote="   ", source_text="anything")
    with pytest.raises(ValueError, match="vacuous"):
        verify_citation(claim)


def test_not_found_verdict_never_claims_fabrication_is_certain():
    """Load-bearing wording check: a NOT_FOUND caveat must not overclaim
    - this is the exact honesty discipline this repo already applies to
    BOUNDED_CHECKED (evidence/model.py's CAVEAT map), extended here to
    citation checking."""
    claim = CitationClaim(
        label="not found",
        claimed_quote="something not present anywhere in the source",
        source_text="a completely unrelated sentence",
    )
    verdict = verify_citation(claim)
    assert verdict.verdict == "NOT_FOUND"
    caveat_lower = verdict.caveat.lower()
    assert "does not confirm" in caveat_lower
    assert "fabricated" in caveat_lower  # names the risk explicitly...
    assert "check the raw source" in caveat_lower  # ...but demands a
                                                    # human check rather
                                                    # than asserting it


def test_verify_citations_batch_preserves_order():
    claims = [
        CitationClaim("first", "estimate GFRcreatinine for adults", NICE_NG203_1_1_2_REAL),
        CitationClaim("second", "mandates the 2009 equation", NICE_NG203_1_1_2_REAL),
        CitationClaim("third", "not to eat any meat", NICE_NG203_1_1_4_REAL),
    ]
    verdicts = verify_citations(claims)
    assert [v.label for v in verdicts] == ["first", "second", "third"]
    assert [v.verdict for v in verdicts] == ["CONFIRMED", "NOT_FOUND", "CONFIRMED"]
