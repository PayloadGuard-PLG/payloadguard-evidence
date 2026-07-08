"""Phase C, Gate C6: NL-dialogue confirmation (process control).

Before a proof is trusted: generate a plain-English summary of what a
Dafny method's contract actually asserts, and get explicit human sign-off
that the summary matches intent. This is the process fix aimed directly
at recurrence of Gate 1's original finding (a spec/requirement-text
mismatch caught only at review, not at authoring time) - catching it at
authoring time instead.

This module is deliberately NOT a natural-language generator. It does
two honest, mechanical things and nothing more:

  1. Extracts each requires/ensures clause verbatim (ground truth,
     unambiguous) alongside any REQ-ID it cites in a trailing comment,
     exactly as authored in the source - never inferred, never guessed
     from the method name or surrounding prose.
  2. Produces a best-effort English GLOSS of each clause via a small,
     fixed operator-substitution table (&&/||/==>/<=>/comparisons ->
     words). This is explicitly a template, not comprehension - it does
     not understand the clause's meaning, only its surface grammar. The
     raw clause is always shown first and is the authoritative artifact;
     the gloss is a reading aid.

The actual correctness check is the human sign-off this feeds, not this
function - a generated summary is not itself evidence of anything. See
examples/dosage_calculator/nl_confirmation_dosage_dfy.md for the recorded
decision this produced for the one real spec in this repository.

Scope, checked not assumed: only single-line requires/ensures clauses are
supported (every real clause in this repo's specs is one line). A
multi-line clause would break the citation-association logic below
silently if not caught - so summarize_method() cross-checks its own
line-based extraction against evidence.dafny_spec_lint's more general,
already-tested clause extractor and refuses (SystemExit, Tier 1) on any
mismatch, rather than risk a dropped or misattributed citation.
"""

import re

from evidence.dafny_spec_lint import (
    _find_method_header,
    _parse_params,
    extract_ensures_clauses,
    extract_requires_clauses,
)

_CLAUSE_LINE_RE = re.compile(r"^\s*(requires|ensures)\s+(.*?)\s*(?://\s*(.*))?$")
# [A-Za-z0-9-]: a real bug, not a hypothetical, surfaced by
# renal_adjustment.dfy's REQ-RENAL-1a (2026-07-08) - the original
# [A-Z0-9-] (no lowercase) silently truncated "REQ-RENAL-1a" to
# "REQ-RENAL-1", misattributing the citation to a real but wrong
# requirement ID rather than dropping it visibly. dosage.dfy's REQ-IDs
# (REQ-GIP-1-4-12, REQ-GIP-1-8-1) never had a lowercase suffix, so this
# never fired until a second spec actually exercised it.
_REQ_ID_RE = re.compile(r"REQ-[A-Za-z0-9-]+")

# Longest/most-specific operators first, so e.g. "<==>" is consumed
# whole before "==>" or "<=" ever get a chance to match part of it.
_GLOSS_SUBSTITUTIONS = (
    (re.compile(r"<==>"), " if and only if "),
    (re.compile(r"==>"), " implies "),
    (re.compile(r"&&"), " and "),
    (re.compile(r"\|\|"), " or "),
    (re.compile(r"!="), " does not equal "),
    (re.compile(r"=="), " equals "),
    (re.compile(r"<="), " is at most "),
    (re.compile(r">="), " is at least "),
    (re.compile(r"<"), " is less than "),
    (re.compile(r">"), " is greater than "),
)


def _gloss(clause_code):
    """Best-effort mechanical English rendering - a template, not
    comprehension. See module docstring."""
    text = clause_code
    for pattern, replacement in _GLOSS_SUBSTITUTIONS:
        text = pattern.sub(replacement, text)
    return re.sub(r"\s+", " ", text).strip()


def _extract_annotated_clauses(source, method_name, keyword):
    """Line-based extraction that preserves trailing `// ...` comments as
    citations - evidence.dafny_spec_lint's extractors strip comments
    before this module ever sees the text, so citations have to be
    pulled separately, here, from the original source. Only matches
    clauses that are exactly one line; summarize_method() is responsible
    for detecting when that assumption doesn't hold."""
    header = _find_method_header(source, method_name)
    clauses = []
    for line in header.splitlines():
        m = _CLAUSE_LINE_RE.match(line)
        if m and m.group(1) == keyword:
            code = m.group(2).strip()
            comment = (m.group(3) or "").strip()
            if code:
                clauses.append((code, comment))
    return clauses


def _normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def summarize_method(source, method_name):
    """Gate C6: the plain-English summary a human signs off on. Returns
    a markdown string. Raises SystemExit if any requires/ensures clause
    for method_name isn't a single line - refusing to guess a citation
    association rather than silently dropping or misattributing one."""
    header = _find_method_header(source, method_name)
    params = _parse_params(header)

    requires = _extract_annotated_clauses(source, method_name, "requires")
    ensures = _extract_annotated_clauses(source, method_name, "ensures")
    canonical_requires = extract_requires_clauses(source, method_name)
    canonical_ensures = extract_ensures_clauses(source, method_name)
    # Content comparison, not just a count - a multi-line clause can
    # silently produce the SAME count as its canonical (correct) parse
    # while the line-based scan above only captured its first line,
    # dropping the continuation. Comparing normalized text catches that;
    # comparing len() alone would not.
    requires_norm = [_normalize(code) for code, _ in requires]
    ensures_norm = [_normalize(code) for code, _ in ensures]
    canonical_requires_norm = [_normalize(c) for c in canonical_requires]
    canonical_ensures_norm = [_normalize(c) for c in canonical_ensures]
    if requires_norm != canonical_requires_norm or ensures_norm != canonical_ensures_norm:
        raise SystemExit(
            f"Gate C6 summary generator only supports single-line "
            f"requires/ensures clauses; {method_name!r} appears to have "
            "one that isn't - refusing to guess a citation association "
            "rather than risk a dropped or misattributed one"
        )

    lines = [f"# Plain-English summary: `{method_name}`", ""]

    lines.append("## Parameters")
    if params:
        for name, ty in params.items():
            lines.append(f"- `{name}`: {ty}")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Preconditions (must hold before the method runs)")
    if requires:
        for i, (code, _comment) in enumerate(requires, 1):
            lines.append(f"{i}. `{code}` — {_gloss(code)}")
    else:
        lines.append("- (none declared)")
    lines.append("")

    lines.append("## Postconditions (guaranteed to hold on return)")
    if ensures:
        for i, (code, comment) in enumerate(ensures, 1):
            req_ids = _REQ_ID_RE.findall(comment)
            cite = f" **[{', '.join(req_ids)}]**" if req_ids else " *(no requirement cited)*"
            lines.append(f"{i}. `{code}` — {_gloss(code)}{cite}")
    else:
        lines.append("- (none declared)")
    lines.append("")

    return "\n".join(lines)
