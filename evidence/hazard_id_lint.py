"""Repo self-consistency lint: every hazard ID referenced anywhere in
this repo's markdown must resolve to a real `### HAZ-...` heading in
some HAZARD_REGISTER.md.

Built 2026-07-15, directly in response to a real bug caught by an
external reviewer (Qodo) on PR #50: a hand-edit meant to narrow
HAZ-GIP-1.2/HAZ-GIP-1.3 into two separate, narrowed rows instead
collapsed them into a single row, silently dropping HAZ-GIP-1.3 while
five other documents (including the very row it split from,
HAZ-GIP-1.2b) kept referencing it. The error was purely mechanical -
no clinical judgment involved anywhere in it - and exactly the kind of
thing a script should catch same-day rather than a human reviewer
catching it after the fact. This module is that script.

Deliberately NOT a citation-content checker (see citation_registry.py
for that) - this only asks "does this ID resolve to a real row," never
whether the row's content is correct or whether a severity/probability
value is defensible. Those remain human, clinical-judgment questions
this repo has never let a script answer.
"""

import pathlib
import re
from dataclasses import dataclass

HAZARD_ID_RE = re.compile(r"\bHAZ-[A-Z]+-[0-9]+(?:\.[0-9]+)?[a-z]?\b")
DEFINED_HEADING_RE = re.compile(r"^###\s+(HAZ-[A-Z]+-[0-9]+(?:\.[0-9]+)?[a-z]?)\b", re.MULTILINE)

# Hazard IDs intentionally retired/merged with no register row of their
# own, but still legitimately mentioned in historical prose (change
# logs, DEVLOG entries). Empty today - every split this repo has done
# so far (see HAZ-GIP-1.2b) kept every original ID as a real row rather
# than retiring one. Add an entry here, with a reason, only if a hazard
# is ever deliberately retired outright.
INTENTIONALLY_RETIRED_IDS: frozenset = frozenset()


@dataclass(frozen=True)
class UndefinedReference:
    """One hazard-ID-shaped token, found somewhere in this repo's
    markdown, that does not resolve to a real `### HAZ-...` heading in
    any HAZARD_REGISTER.md (and is not in INTENTIONALLY_RETIRED_IDS)."""

    file: str
    line: int
    hazard_id: str


def find_defined_hazard_ids(repo_root: pathlib.Path) -> set:
    """The set of every hazard ID that has a real `### HAZ-...` heading
    in any HAZARD_REGISTER.md under repo_root. Repo-wide, not scoped
    per-example - a cross-reference to a different example's hazard
    would legitimately resolve too, though none exist as of this
    writing (every example's hazards are self-contained)."""
    defined = set()
    for register_path in sorted(repo_root.rglob("HAZARD_REGISTER.md")):
        text = register_path.read_text(encoding="utf-8")
        defined.update(DEFINED_HEADING_RE.findall(text))
    return defined


def find_undefined_references(
    repo_root: pathlib.Path,
    intentionally_retired: frozenset = INTENTIONALLY_RETIRED_IDS,
) -> list:
    """Scan every tracked markdown file for hazard-ID-shaped tokens and
    flag any that don't resolve to a real heading and aren't
    intentionally retired. Returns findings sorted by (file, line,
    hazard_id) for stable, diffable output - `rglob` + a sort on the
    returned list already gives deterministic ordering, made explicit
    here rather than relied on implicitly."""
    defined = find_defined_hazard_ids(repo_root)
    findings = []
    for md_path in sorted(repo_root.rglob("*.md")):
        if _is_ignored(md_path):
            continue
        text = md_path.read_text(encoding="utf-8")
        rel_path = str(md_path.relative_to(repo_root))
        for match in HAZARD_ID_RE.finditer(text):
            hazard_id = match.group(0)
            if hazard_id in defined or hazard_id in intentionally_retired:
                continue
            line = text.count("\n", 0, match.start()) + 1
            findings.append(UndefinedReference(file=rel_path, line=line, hazard_id=hazard_id))
    return sorted(findings, key=lambda f: (f.file, f.line, f.hazard_id))


def _is_ignored(path: pathlib.Path) -> bool:
    parts = path.parts
    return "node_modules" in parts or ".git" in parts
