"""Polish lint: flags decision-journal narrative language in a
current-state reference document.

This repository keeps two deliberately different kinds of document:
DEVLOG.md and KNOWN_LIMITATIONS.md are append-only decision journals —
narrative, dated, describing how a conclusion was reached. SYSTEM_
REFERENCE.md is the opposite: pure current-state description, no
history, no discussion of alternatives, no dated build narrative.

The two are easy to conflate over time, since every other current-
state document in this repository (HANDOFF.md, SYSTEM_BLUEPRINT.md)
has already drifted into carrying narrative language despite nominally
being "current state" docs — confirmed by direct inspection, not
assumed. This module exists to keep SYSTEM_REFERENCE.md from following
the same path: it scans for a fixed set of phrases that are reliable
markers of decision-journal prose (a verb tense implying a past
conclusion was reached, a dated session reference, a reference to
whose decision something was) and reports every match with enough
context to fix it.

This is deliberately a narrow, high-precision phrase list, not a
general "sounds like narrative" classifier — false positives on
legitimate technical language (e.g. "Z3 found a counterexample" is
fine; "we found a bug" is not) would make the lint unusable. The list
is expected to grow if a real instance of narrative drift is caught
that isn't already covered.
"""

import re

# Each pattern is matched case-insensitively. Keep this list precise:
# every entry should be a phrase that essentially only appears in
# narrative/decision-journal prose, not in accurate current-state
# technical description.
_BANNED_PATTERNS = [
    r"\bturned out\b",
    r"\bit turned out\b",
    r"\ba mistake\b",
    r"\bwas a mistake\b",
    r"\boriginally\b",
    r"\bused to be\b",
    r"\bused to say\b",
    r"\bat first\b",
    r"\bwe decided\b",
    r"\bwe found\b",
    r"\bwe considered\b",
    r"\bself-caught\b",
    r"\bcaught a real\b",
    r"\brequested directly\b",
    r"\bSteven decided\b",
    r"\bon Steven's decision\b",
    r"\bin this session\b",
    r"\bthis session\b",
    r"\bpreviously (said|claimed|stated|described)\b",
]

# A dated entry (YYYY-MM-DD) is a strong marker of decision-journal
# writing, since a pure current-state fact doesn't need a date to be
# true. The single legitimate use in this document is its own
# "Last updated:" header line, which is exempted explicitly rather
# than by excluding dates from the pattern entirely.
_DATE_RE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
_LAST_UPDATED_LINE_RE = re.compile(r"^Last updated:", re.IGNORECASE)

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _BANNED_PATTERNS]


def scan_for_narrative_language(text: str) -> list[str]:
    """Return a list of human-readable findings, empty if the text is
    clean. Each finding names the matched phrase and quotes the line
    it appears on, so a caller can locate and fix it without having
    to re-run the scan themselves."""
    findings = []
    lines = text.splitlines()

    for lineno, line in enumerate(lines, start=1):
        for pattern in _COMPILED:
            if pattern.search(line):
                findings.append(
                    f"line {lineno}: matched {pattern.pattern!r} in: {line.strip()!r}"
                )

        if _DATE_RE.search(line) and not _LAST_UPDATED_LINE_RE.match(line.strip()):
            findings.append(
                f"line {lineno}: dated reference outside the 'Last updated:' "
                f"header: {line.strip()!r}"
            )

    return findings
