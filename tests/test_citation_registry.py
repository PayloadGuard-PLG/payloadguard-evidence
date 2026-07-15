"""Regression coverage for evidence/citation_registry.py, and - the
whole point of the module - a live check that this repo's real,
committed markdown currently asserts the ISO 14971 Annex D claim
nowhere except as a marked quotation or correction.

Unit tests build a real (if minimal) git repo under tmp_path and stage
the files under test - find_unmarked_banned_citations() now scans only
git-tracked files (see evidence/tracked_files.py, added after a
separate review finding on PR #51 that the original implementation
scanned the filesystem regardless of git status), so a bare directory
with no `.git` no longer works as a test fixture.
"""

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.citation_registry import find_unmarked_banned_citations  # noqa: E402
from tests.conftest import make_git_repo  # noqa: E402


def test_real_repo_has_no_unmarked_annex_d_claims():
    """The regression test. If this fails, some document asserts "ISO
    14971['s own] Annex D" as if it were fact, with no quotation and no
    correction marker nearby - the exact claim this repo spent an audit
    finding, fixing across six files, and then re-fixing after a
    restructuring pass re-typed it. See RISK_MANAGEMENT_FINDINGS.md
    Finding 2."""
    findings = find_unmarked_banned_citations(REPO_ROOT)
    assert findings == [], (
        "Unmarked banned citation(s) found:\n"
        + "\n".join(f"  {f.file}:{f.line} [{f.key}] ...{f.snippet}..." for f in findings)
    )


def test_detects_a_fresh_unmarked_claim(tmp_path):
    make_git_repo(
        tmp_path,
        {"SOME_DOC.md": "Per ISO 14971's own Annex D, risk should be reduced as far as possible.\n"},
    )

    findings = find_unmarked_banned_citations(tmp_path)

    assert len(findings) == 1
    assert findings[0].key == "iso-14971-annex-d"
    assert findings[0].file == "SOME_DOC.md"


def test_allows_a_directly_quoted_occurrence(tmp_path):
    make_git_repo(
        tmp_path,
        {
            "SOME_DOC.md": (
                'This was previously attributed to "ISO 14971\'s own Annex D," '
                "an error discovered during review with no correction language "
                "nearby in this particular sentence on purpose.\n"
            )
        },
    )

    assert find_unmarked_banned_citations(tmp_path) == []


def test_allows_an_occurrence_with_a_nearby_correction_marker(tmp_path):
    """Mirrors DEVLOG.md's actual pattern: the original, unquoted wrong
    text preserved verbatim (append-only discipline), immediately
    followed by a bracketed correction - never quoted, but clearly
    marked."""
    make_git_repo(
        tmp_path,
        {
            "DEVLOG.md": (
                "a genuine ALARP determination from Steven — an ISO 14971 Annex D "
                "move [correction, 2026-07-15: the 2019 edition has no Annex D; "
                "see the findings ledger].\n"
            )
        },
    )

    assert find_unmarked_banned_citations(tmp_path) == []


def test_does_not_match_the_correct_true_statement(tmp_path):
    """"ISO 14971:2019 has no Annex D" is a TRUE statement (it's the
    finding itself), not a re-assertion of the wrong claim - the
    pattern requires "ISO 14971" immediately followed by "Annex D"
    (mod an optional possessive), which this sentence's intervening
    ":2019 has no" breaks, so it should never even match, regardless of
    quoting or markers."""
    make_git_repo(
        tmp_path,
        {"SOME_DOC.md": "ISO 14971:2019 has no Annex D, confirmed against Table B.1.\n"},
    )

    assert find_unmarked_banned_citations(tmp_path) == []


def test_matches_survive_a_markdown_line_wrap(tmp_path):
    make_git_repo(
        tmp_path,
        {
            "SOME_DOC.md": 'previously attributed to "ISO 14971\'s own Annex\nD," which is wrong.\n',
            # Quoted, so still allowed - but this confirms the pattern
            # itself tolerates the wrap (would raise no findings either
            # way here, so assert via a non-quoted variant below instead).
            "OTHER_DOC.md": "attributed to ISO 14971's own Annex\nD with no marker at all nearby whatsoever.\n",
        },
    )

    findings = find_unmarked_banned_citations(tmp_path)

    assert any(f.file == "OTHER_DOC.md" for f in findings)


def test_untracked_markdown_is_not_scanned(tmp_path):
    """The exact case an external review (Qodo, PR #51) flagged: a
    workspace file that was never `git add`-ed must not affect the
    result, even though it asserts the banned claim unmarked."""
    make_git_repo(tmp_path, {"README.md": "Nothing relevant here.\n"})
    # Written to disk but deliberately never staged.
    (tmp_path / "UNTRACKED_SCRATCH.md").write_text(
        "Per ISO 14971's own Annex D, unmarked and untracked.\n"
    )

    assert find_unmarked_banned_citations(tmp_path) == []
