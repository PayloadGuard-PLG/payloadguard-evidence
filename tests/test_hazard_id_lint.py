"""Regression coverage for evidence/hazard_id_lint.py, and - the whole
point of the module - a live check that this repo's real, committed
markdown is currently clean. That second test is the one that would
have caught the actual HAZ-GIP-1.3 bug (PR #50) the day it was
introduced instead of a day later, via an external reviewer.

Unit tests build a real (if minimal) git repo under tmp_path and stage
the files under test - find_undefined_references() now scans only
git-tracked files (see evidence/tracked_files.py, added after a
separate review finding on PR #51 that the original implementation
scanned the filesystem regardless of git status), so a bare directory
with no `.git` no longer works as a test fixture.
"""

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.hazard_id_lint import (  # noqa: E402
    find_defined_hazard_ids,
    find_undefined_references,
)
from tests.conftest import make_git_repo  # noqa: E402


def test_real_repo_has_no_undefined_hazard_references():
    """The regression test. If this fails, some document references a
    hazard ID that doesn't resolve to a real `### HAZ-...` heading in
    any HAZARD_REGISTER.md - exactly the shape of the HAZ-GIP-1.3 bug
    this module was built to catch."""
    findings = find_undefined_references(REPO_ROOT)
    assert findings == [], (
        "Undefined hazard ID reference(s) found:\n"
        + "\n".join(f"  {f.file}:{f.line} references {f.hazard_id!r}" for f in findings)
    )


def test_real_repo_defines_the_expected_hazard_ids_per_example():
    """Sanity check that the scanner actually finds real headings, not
    an accidentally-empty set that would make the regression test above
    vacuously pass."""
    defined = find_defined_hazard_ids(REPO_ROOT)
    # A representative id from each of the three examples' registers.
    assert "HAZ-GIP-1.2" in defined
    assert "HAZ-GIP-1.3" in defined
    assert "HAZ-GIP-1.2b" in defined
    assert "HAZ-DOSE-003" in defined
    assert "HAZ-RENAL-1" in defined
    assert "HAZ-DDI-1" in defined


def test_detects_an_undefined_reference(tmp_path):
    make_git_repo(
        tmp_path,
        {
            "HAZARD_REGISTER.md": "### HAZ-X-1 — a real hazard\n\nsome content\n",
            "PLAN.md": "See HAZ-X-1 for the closed pathway and HAZ-X-2 for the residual.\n",
        },
    )

    findings = find_undefined_references(tmp_path)

    assert len(findings) == 1
    assert findings[0].hazard_id == "HAZ-X-2"
    assert findings[0].file == "PLAN.md"


def test_does_not_flag_a_defined_id_referenced_elsewhere(tmp_path):
    make_git_repo(
        tmp_path,
        {
            "HAZARD_REGISTER.md": "### HAZ-X-1 — a real hazard\n",
            "PLAN.md": "Cross-reference: HAZ-X-1.\n",
        },
    )

    assert find_undefined_references(tmp_path) == []


def test_split_hazard_style_ids_are_parsed_correctly(tmp_path):
    """The exact shape of the bug this module exists to catch: a base
    ID (HAZ-X-2) and a lettered split-row ID (HAZ-X-2b) must be treated
    as distinct IDs, not merged or confused."""
    make_git_repo(
        tmp_path,
        {
            "HAZARD_REGISTER.md": "### HAZ-X-2 — narrowed row\n\n### HAZ-X-2b — split residual\n",
            "PLAN.md": "See HAZ-X-2 and HAZ-X-2b, but not HAZ-X-3.\n",
        },
    )

    findings = find_undefined_references(tmp_path)

    assert len(findings) == 1
    assert findings[0].hazard_id == "HAZ-X-3"


def test_intentionally_retired_ids_are_not_flagged(tmp_path):
    make_git_repo(
        tmp_path,
        {
            "DEVLOG.md": "HAZ-X-9 was retired and folded into HAZ-X-1.\n",
            "HAZARD_REGISTER.md": "### HAZ-X-1 — the survivor\n",
        },
    )

    findings = find_undefined_references(tmp_path, intentionally_retired=frozenset({"HAZ-X-9"}))

    assert findings == []


def test_dotted_and_undotted_ids_both_parse(tmp_path):
    make_git_repo(
        tmp_path,
        {"HAZARD_REGISTER.md": "### HAZ-GIP-1.14 — dotted\n\n### HAZ-RENAL-8 — undotted\n"},
    )

    defined = find_defined_hazard_ids(tmp_path)

    assert defined == {"HAZ-GIP-1.14", "HAZ-RENAL-8"}


def test_untracked_markdown_is_not_scanned(tmp_path):
    """The exact case an external review (Qodo, PR #51) flagged: a
    workspace file that was never `git add`-ed - a local scratch note,
    or something a tool generated (this repo's own working tree already
    had pytest's cache README as a real, non-hypothetical example) -
    must not affect the result, even though it references an undefined
    hazard ID."""
    make_git_repo(
        tmp_path,
        {"HAZARD_REGISTER.md": "### HAZ-X-1 — the only real hazard\n"},
    )
    # Written to disk but deliberately never staged.
    (tmp_path / "UNTRACKED_SCRATCH.md").write_text("References HAZ-X-999, which is fake.\n")

    assert find_undefined_references(tmp_path) == []


def test_test_catalog_md_is_excluded_even_when_tracked(tmp_path):
    """Real false positive, found 2026-07-15 the first time
    TEST_CATALOG.md was generated: it quotes test docstrings verbatim,
    including tests/test_hazard_id_lint.py's own fixture examples
    ("HAZ-X-2", etc.) - fictional IDs used to test this exact module,
    not claims about a real hazard. TEST_CATALOG.md must be excluded
    even though it's git-tracked (unlike the untracked-scratch case
    above, which is excluded because tracked_files() never returns it
    at all)."""
    make_git_repo(
        tmp_path,
        {
            "HAZARD_REGISTER.md": "### HAZ-X-1 — the only real hazard\n",
            "TEST_CATALOG.md": "| `test_x` | Mentions HAZ-X-999 as fixture data. | `t.py:1` |\n",
        },
    )

    assert find_undefined_references(tmp_path) == []
