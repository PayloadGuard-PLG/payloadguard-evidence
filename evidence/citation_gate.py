"""Citation gate: mechanical, deterministic verification that a claimed
quote actually appears in a source document's text.

Scoped out 2026-07-09 as the buildable-now piece of a larger idea
(automating contract drafting from natural-language specs via
"vericoding") — this session caught two real, independently fabricated
citations by hand, both from documents that presented themselves as
verified research: NICE NG203's real Recommendation 1.1.2 doesn't
specify an eGFR equation version at all (the claim said it mandated the
2009 equation), and its real 1.1.4 is about not eating meat before a
blood test (the claim said it barred ethnicity-based eGFR adjustment).
A second document repeated the SAME NICE fabrication verbatim and added
a new one: KDIGO's real recommendation is numbered 1.1.2.1, not 1.1.2,
and its content is about the eGFRcr-vs-eGFRcr-cys choice, not "the
explicit shift to the 2021 race-free equation" as claimed. Both were
caught only by fetching the actual primary source and reading it
directly — this module is the mechanical version of that same check,
so it doesn't have to be redone by hand every time.

Deliberately NOT an LLM judgment call. This module only does normalized
substring matching against source text the caller already has (fetched
via WebFetch, extracted from a PDF, or otherwise obtained) - it does not
fetch, summarize, or interpret anything itself. Keeping the check
mechanical is the entire point: an automated citation drafter and an
automated citation checker must not be the same kind of system, or the
checker inherits the drafter's failure mode (this mirrors why Gate C6's
human sign-off can't be performed by the system that drafted the spec
it's confirming).

Verdict vocabulary is deliberately asymmetric, mirroring this repo's own
Strength vocabulary (evidence/model.py) rather than a plain pass/fail:

    CONFIRMED  - the claimed quote (or a close, normalized match) was
                 found in the source text. Strong evidence the citation
                 is real.
    NOT_FOUND  - no match found in the source text as given. This is
                 NOT proof of fabrication - source-text extraction
                 (particularly from PDFs) can be lossy, and this
                 repo's own PDF extractor has already been observed to
                 drop characters at some kerning-adjustment boundaries.
                 A NOT_FOUND verdict means "could not confirm
                 automatically" and should prompt a direct, manual
                 check of the raw source before concluding a citation
                 is fabricated - never presented as certain proof
                 either way, in either direction.

Both of the real fabrication cases above are used as regression fixtures
in tests/test_citation_gate.py - not synthetic examples, the actual
claims and the actual source text this session verified them against.
"""

import re
import unicodedata
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CitationClaim:
    """One claim to check: a quote, attributed to a label (e.g. a
    document name or a recommendation number), to be checked against a
    specific source text."""

    label: str
    claimed_quote: str
    source_text: str


@dataclass(frozen=True)
class CitationVerdict:
    """The result of checking one CitationClaim. `context` is populated
    only on CONFIRMED (a snippet of the source surrounding the match,
    for human spot-checking) - always None on NOT_FOUND, since there is
    nothing to show."""

    label: str
    verdict: str  # "CONFIRMED" or "NOT_FOUND"
    context: Optional[str]
    caveat: str


_NOT_FOUND_CAVEAT = (
    "Not found in the source text as given. This does NOT confirm the "
    "citation is fabricated - extraction can be lossy. Check the raw "
    "source directly before concluding anything."
)
_CONFIRMED_CAVEAT = (
    "Found as a normalized substring of the source text. Strong "
    "evidence the citation is real, not a guarantee against a "
    "coincidental match on a short or generic phrase."
)

_WHITESPACE_RE = re.compile(r"\s+")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")

_CONTEXT_RADIUS = 80


def _normalize(text: str) -> str:
    """Lowercase, Unicode-normalize (so e.g. curly vs straight quotes
    and precomposed vs decomposed accents don't cause a spurious
    mismatch), then strip everything except letters and digits.

    Stripping whitespace entirely (not just collapsing it) is
    deliberate, not an oversight: source text extracted from a PDF via
    this repo's own extractor (sources/kdigo-2024-gfr-staging.md's
    extraction method) is frequently unspaced or inconsistently spaced
    across word boundaries. Matching on letters/digits only sidesteps
    that at the cost of being unable to distinguish "red flag" from
    "redflag" - an accepted tradeoff given the alternative is silently
    missing real matches due to extraction artifacts, which is the
    worse failure mode for a check whose whole purpose is not missing
    real citations.
    """
    text = unicodedata.normalize("NFKD", text)
    text = text.lower()
    text = _NON_ALNUM_RE.sub("", text)
    return text


def verify_citation(claim: CitationClaim) -> CitationVerdict:
    """Check whether claim.claimed_quote appears (as a normalized
    substring) in claim.source_text. Pure function - no I/O, no
    fetching. See module docstring for the verdict vocabulary and why
    NOT_FOUND is not treated as proof of anything."""
    normalized_quote = _normalize(claim.claimed_quote)
    normalized_source = _normalize(claim.source_text)

    if not normalized_quote:
        raise ValueError("claimed_quote is empty after normalization; refusing to check a vacuous claim")

    idx = normalized_source.find(normalized_quote)
    if idx == -1:
        return CitationVerdict(
            label=claim.label,
            verdict="NOT_FOUND",
            context=None,
            caveat=_NOT_FOUND_CAVEAT,
        )

    context = _extract_context(claim.source_text, claim.claimed_quote)
    return CitationVerdict(
        label=claim.label,
        verdict="CONFIRMED",
        context=context,
        caveat=_CONFIRMED_CAVEAT,
    )


def _extract_context(source_text: str, claimed_quote: str) -> str:
    """Best-effort human-readable context snippet for a CONFIRMED
    match, found by re-searching the ORIGINAL (non-normalized) source
    text for the first word of the claim - a readability aid for spot-
    checking, not part of the pass/fail logic itself, which runs
    entirely on normalized text. If even the first word can't be found
    verbatim (can happen if normalization changed it, e.g. it contained
    only punctuation), returns a fixed placeholder rather than guessing."""
    words = claimed_quote.strip().split()
    if not words:
        return "(no context available)"
    first_word = words[0]
    idx = source_text.find(first_word)
    if idx == -1:
        # Case-insensitive fallback before giving up.
        idx = source_text.lower().find(first_word.lower())
    if idx == -1:
        return "(match confirmed on normalized text; no verbatim context located)"
    start = max(0, idx - _CONTEXT_RADIUS)
    end = min(len(source_text), idx + len(claimed_quote) + _CONTEXT_RADIUS)
    return source_text[start:end]


def verify_citations(claims: list) -> list:
    """Batch form of verify_citation - checks each claim independently
    (a claim's source_text is per-claim, not shared, since different
    claims typically cite different documents). Returns verdicts in the
    same order as the input claims."""
    return [verify_citation(c) for c in claims]
