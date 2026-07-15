"""Regression coverage for evidence/test_catalog.py, and - the whole
point of the module - a check that the committed TEST_CATALOG.md is
exactly what the generator produces against the real, current test
suite right now. If this fails, someone added/renamed/removed a test
without regenerating the catalog - the same "generated artifact must
match its generator" discipline evidence/cli.py's own tests already
apply to the traceability matrices.
"""

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.test_catalog import (  # noqa: E402
    build_catalog,
    category_heading,
    render_markdown,
)
from tests.conftest import make_git_repo  # noqa: E402


def test_committed_catalog_matches_the_generator():
    categories = build_catalog(REPO_ROOT)
    expected = render_markdown(categories)
    actual = (REPO_ROOT / "TEST_CATALOG.md").read_text(encoding="utf-8")
    assert actual == expected, (
        "TEST_CATALOG.md is out of date. Regenerate with:\n"
        "  python -m evidence.test_catalog --out TEST_CATALOG.md"
    )


def test_every_real_test_file_produces_a_nonempty_category():
    """Sanity check that the parser actually finds tests, not an
    accidentally-empty result that would make the regression test above
    vacuously pass."""
    categories = build_catalog(REPO_ROOT)
    assert len(categories) >= 20
    assert sum(len(c.entries) for c in categories) >= 200


def test_category_heading_title_cases_and_expands_acronyms():
    assert category_heading("test_hazard_id_lint.py") == "Hazard ID Lint"
    assert category_heading("test_dafny_nl_summary.py") == "Dafny NL Summary"
    assert category_heading("test_dafny_stp_suite.py") == "Dafny STP Suite"
    assert category_heading("test_cli.py") == "CLI"
    assert category_heading("test_conflict_check.py") == "Conflict Check"


def test_parses_a_docstring_first_sentence_as_the_description(tmp_path):
    make_git_repo(
        tmp_path,
        {
            "tests/test_example.py": (
                "def test_something():\n"
                '    """Confirms the thing works. Extra detail that should\n'
                '    be dropped from the one-line description."""\n'
                "    assert True\n"
            )
        },
    )

    categories = build_catalog(tmp_path)

    assert len(categories) == 1
    entry = categories[0].entries[0]
    assert entry.name == "test_something"
    assert entry.description == "Confirms the thing works."
    assert entry.file == "tests/test_example.py"
    assert entry.line == 1


def test_derives_a_description_from_the_name_when_no_docstring(tmp_path):
    make_git_repo(
        tmp_path,
        {"tests/test_example.py": "def test_returns_zero_on_empty_input():\n    assert True\n"},
    )

    categories = build_catalog(tmp_path)

    entry = categories[0].entries[0]
    assert entry.description == "Returns zero on empty input."


def test_non_test_functions_are_excluded(tmp_path):
    make_git_repo(
        tmp_path,
        {
            "tests/test_example.py": (
                "def _helper():\n"
                "    pass\n"
                "\n"
                "def test_real_one():\n"
                "    assert True\n"
            )
        },
    )

    categories = build_catalog(tmp_path)

    names = [e.name for e in categories[0].entries]
    assert names == ["test_real_one"]


def test_a_file_with_no_test_functions_produces_no_category(tmp_path):
    make_git_repo(tmp_path, {"tests/test_empty.py": "x = 1\n"})

    assert build_catalog(tmp_path) == []


def test_rendered_markdown_escapes_pipe_characters_in_descriptions():
    from evidence.test_catalog import TestCategory, TestEntry

    category = TestCategory(
        heading="Example",
        file="tests/test_example.py",
        entries=(TestEntry(name="test_x", description="A | B", file="tests/test_example.py", line=1),),
    )

    markdown = render_markdown([category])

    assert "A \\| B" in markdown
