"""Gate: SYSTEM_REFERENCE.md must stay pure current-state prose.

Every other nominally-"current-state" document in this repository
(HANDOFF.md, SYSTEM_BLUEPRINT.md) has drifted into carrying build
narrative over time, despite that not being their stated purpose —
confirmed by direct inspection of SYSTEM_BLUEPRINT.md, which contains
"turned out", "mistake", and dated build entries throughout. This test
exists so SYSTEM_REFERENCE.md does not follow the same path silently;
a future edit that reintroduces narrative language fails CI here
rather than being caught only by manual re-review.
"""

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.polish_lint import scan_for_narrative_language


def test_system_reference_has_no_narrative_language():
    text = (REPO_ROOT / "SYSTEM_REFERENCE.md").read_text()
    findings = scan_for_narrative_language(text)
    assert not findings, (
        "SYSTEM_REFERENCE.md contains decision-journal narrative language, "
        "which does not belong in a pure current-state reference document "
        "(that content belongs in DEVLOG.md or KNOWN_LIMITATIONS.md "
        "instead). Findings:\n" + "\n".join(findings)
    )


def test_scanner_actually_detects_narrative_language():
    """Positive-control test: prove the scanner isn't vacuously passing
    by feeding it text it must flag."""
    dirty_text = (
        "Last updated: 2026-07-18\n\n"
        "We found a real bug 2026-07-10 and it turned out to be a mistake "
        "in this session's own probing.\n"
    )
    findings = scan_for_narrative_language(dirty_text)
    assert findings, "scanner failed to flag known-bad narrative text"
    # Confirm it's not just flagging the exempted header line alone.
    assert any("line 3" in f for f in findings)


def test_last_updated_header_line_is_exempt_from_the_date_check():
    """The one legitimate date in the document -- its own header --
    must not itself trip the dated-reference check."""
    clean_text = "Last updated: 2026-07-18\n\nThis document has no other dates in it.\n"
    findings = scan_for_narrative_language(clean_text)
    assert not findings, f"header line incorrectly flagged: {findings}"
