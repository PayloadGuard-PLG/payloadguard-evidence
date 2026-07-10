"""Mechanical version of a check performed by hand repeatedly this
session (Steven, more than once: "devlog in main is still 2 hours
old") -- HANDOFF.md, KNOWN_LIMITATIONS.md, and SYSTEM_BLUEPRINT.md each
carry their own "Last updated" claim, and nothing enforced that it
isn't older than DEVLOG.md's actual newest entry. As of 2026-07-10 this
is not hypothetical: KNOWN_LIMITATIONS.md's and SYSTEM_BLUEPRINT.md's
headers both still said "2026-07-09" while DEVLOG.md's newest entry
(line 9) was already "2026-07-10" -- a real, live instance of the exact
drift this test exists to catch, found while writing this test, not
constructed as a synthetic example.

DEVLOG.md is strictly newest-first (its own header says so) and every
entry heading begins "## YYYY-MM-DD" even though what follows the date
varies across older entries ("## 2026-07-05 09:46 UTC -- ...",
"## 2026-07-05 (Turn B4) -- ..."), so the FIRST "## YYYY-MM-DD" match in
the file is always the newest date -- no need to parse or sort every
heading.
"""

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

DEVLOG_DATE_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})", re.MULTILINE)

LAST_UPDATED_RE = re.compile(r"Last updated:\*{0,2}\s+(\d{4}-\d{2}-\d{2})")

DOCS_WITH_LAST_UPDATED = ["HANDOFF.md", "KNOWN_LIMITATIONS.md", "SYSTEM_BLUEPRINT.md"]


def _first_match_date(text: str, pattern: re.Pattern, source: str) -> str:
    match = pattern.search(text)
    assert match is not None, f"no date found in {source} matching {pattern.pattern!r}"
    return match.group(1)


def test_current_state_docs_are_not_older_than_devlogs_newest_entry():
    devlog_text = (REPO_ROOT / "DEVLOG.md").read_text()
    devlog_date = _first_match_date(devlog_text, DEVLOG_DATE_RE, "DEVLOG.md")

    stale = []
    for relative_path in DOCS_WITH_LAST_UPDATED:
        doc_text = (REPO_ROOT / relative_path).read_text()
        doc_date = _first_match_date(doc_text, LAST_UPDATED_RE, relative_path)
        if doc_date < devlog_date:
            stale.append(f"{relative_path} (says {doc_date})")

    assert not stale, (
        f"DEVLOG.md's newest entry is dated {devlog_date}, but these docs' "
        f"own 'Last updated' date is older than that: {', '.join(stale)}. "
        "Bring each one's content current with DEVLOG.md's latest entry "
        "(or confirm nothing in it is actually stale) before bumping its "
        "date -- don't just bump the date to silence this check."
    )
