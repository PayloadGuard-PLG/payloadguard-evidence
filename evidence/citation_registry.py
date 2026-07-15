"""Repo self-consistency lint, citation half: guards against the exact
regression this repo's own history demonstrates is real - a specific,
already-disproven citation ("ISO 14971['s own] Annex D" - the 2019
edition has no Annex D, confirmed directly against the standard's own
Table B.1; see RISK_MANAGEMENT_FINDINGS.md Finding 2 for the full
record) being asserted again as fact anywhere in this repo, rather than
only ever appearing as a clearly marked quotation or correction.

Built 2026-07-15, alongside evidence/hazard_id_lint.py, as the other
half of the same root-cause fix: both this citation error and the
HAZ-GIP-1.3 hazard-splitting bug hazard_id_lint.py guards against
happened for the same underlying reason - a fact was restated
independently across many files with no single source of truth and no
mechanical cross-check, so one wrong instance (or one dropped ID)
spreads silently instead of being caught at the point it's introduced.

Deliberately narrow, not a general "citation checker": this module
knows about exactly one disproven claim today. Extending
BANNED_CITATIONS with a new entry is the intended way to add
protection against a newly-discovered wrong citation once it has been
fixed everywhere it currently appears - the pattern generalizes, the
list itself doesn't need to be exhaustive on day one.

Not the same tool as citation_gate.py, despite the similar name: that
module checks whether a NEW claim's quoted text appears in a source
document - used when verifying an externally-supplied claim against a
primary source before trusting it. This module checks whether an
ALREADY-KNOWN-WRONG phrase has crept back into this repo's OWN
committed prose without being clearly marked as a corrected historical
reference. Different question, opposite direction of check.
"""

import pathlib
import re
from dataclasses import dataclass

from evidence.tracked_files import tracked_files

_QUOTE_LOOKBEHIND_CHARS = 3
_CONTEXT_BEFORE_CHARS = 60
_CONTEXT_AFTER_CHARS = 250


@dataclass(frozen=True)
class BannedCitation:
    """One known-wrong claim this repo has already disproven and fixed
    everywhere it was asserted as fact. `pattern` matches the wrong
    claim itself (whitespace-tolerant, so it still matches across a
    markdown line wrap). `allow_markers` are substrings (matched
    case-insensitively on whitespace-collapsed text) whose presence
    near a match means the occurrence is a marked correction, not a
    fresh, unqualified re-assertion of the wrong claim."""

    key: str
    pattern: re.Pattern
    reason: str
    allow_markers: tuple


BANNED_CITATIONS = (
    BannedCitation(
        key="iso-14971-annex-d",
        pattern=re.compile(r"ISO\s+14971(?:['’]s(?:\s+own)?)?\s+Annex\s+D", re.IGNORECASE),
        reason=(
            "ISO 14971:2019 has no Annex D (third edition: Annexes A, B, "
            "and C only). The 2007 edition's Annex D was moved to ISO/TR "
            "24971 in the 2019 revision, not retained as an annex - "
            "confirmed directly against the 2019 standard's own Table "
            "B.1. See RISK_MANAGEMENT_FINDINGS.md Finding 2 for the full "
            "record of where this was wrong and how it was fixed."
        ),
        allow_markers=(
            "table b.1",
            "no annex d",
            "doesn't exist",
            "does not exist",
            "correction",
            "corrects",
        ),
    ),
)


@dataclass(frozen=True)
class UnmarkedBannedCitation:
    """One occurrence of a BANNED_CITATIONS pattern that is neither
    quoted nor accompanied by one of its allow_markers nearby - i.e. it
    reads as a fresh, unqualified assertion of a claim this repo has
    already disproven."""

    file: str
    line: int
    key: str
    snippet: str
    reason: str


def find_unmarked_banned_citations(repo_root: pathlib.Path) -> list:
    """Scan every git-tracked markdown file (via tracked_files(), not a
    plain filesystem walk - see that module's docstring for why: an
    untracked/generated .md file shouldn't affect this scan's result)
    for each BANNED_CITATIONS pattern. A match is allowed - not flagged
    - if either:

    1. It is directly quoted (a quotation mark appears immediately
       before the match), i.e. the text is discussing the phrase as a
       claim under review, not asserting it; or
    2. One of the citation's allow_markers appears nearby (same
       sentence/paragraph), i.e. the text is actively correcting the
       claim right where it appears.

    Both are the two real patterns every existing, legitimate
    occurrence in this repo's own history already follows - see
    DEVLOG.md's bracketed corrections (pattern 2, unquoted original
    text immediately followed by a correction bracket) and
    RISK_MANAGEMENT_PLAN.md's citation-correction paragraphs (pattern
    1, the wrong claim quoted before being corrected). Anything that
    matches neither pattern is new, or was fixed without leaving either
    marker, and gets flagged either way - fail closed, not silently
    permissive, matching this repo's own citation_gate.py precedent of
    treating an unconfirmed case as needing human attention rather than
    resolving it either direction automatically."""
    findings = []
    for md_path in tracked_files(repo_root, "*.md"):
        if _is_ignored(md_path):
            continue
        text = md_path.read_text(encoding="utf-8")
        rel_path = str(md_path.relative_to(repo_root))
        for banned in BANNED_CITATIONS:
            for match in banned.pattern.finditer(text):
                if _is_quoted(text, match.start()):
                    continue
                if _has_allow_marker(text, match.start(), match.end(), banned.allow_markers):
                    continue
                line = text.count("\n", 0, match.start()) + 1
                snippet = _snippet(text, match.start(), match.end())
                findings.append(
                    UnmarkedBannedCitation(
                        file=rel_path,
                        line=line,
                        key=banned.key,
                        snippet=snippet,
                        reason=banned.reason,
                    )
                )
    return sorted(findings, key=lambda f: (f.file, f.line, f.key))


def _is_quoted(text: str, match_start: int) -> bool:
    lookbehind = text[max(0, match_start - _QUOTE_LOOKBEHIND_CHARS) : match_start]
    return '"' in lookbehind or "“" in lookbehind


def _has_allow_marker(text: str, match_start: int, match_end: int, markers: tuple) -> bool:
    window = text[max(0, match_start - _CONTEXT_BEFORE_CHARS) : match_end + _CONTEXT_AFTER_CHARS]
    window_normalized = re.sub(r"\s+", " ", window).lower()
    return any(marker in window_normalized for marker in markers)


def _snippet(text: str, match_start: int, match_end: int) -> str:
    raw = text[max(0, match_start - 40) : match_end + 40]
    return re.sub(r"\s+", " ", raw).strip()


def _is_ignored(path: pathlib.Path) -> bool:
    parts = path.parts
    return "node_modules" in parts or ".git" in parts
