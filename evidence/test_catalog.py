"""Generates TEST_CATALOG.md — a categorized index of every test in
this repo's suite, with a brief description and a file:line pointer to
the real test.

Built 2026-07-15, direct instruction: "I need a document that outlines
each test completed and updated as more are added... categorized
correctly and a brief description and code." Deliberately generated,
not hand-authored: this repo's own standing discipline this session
(evidence/hazard_id_lint.py, evidence/citation_registry.py) is that a
fact restated by hand in more than one place drifts. A large, by-hand
test catalog is exactly that fact, restated - deliberately not naming
a specific row count here, since it would need updating every time a
test is added and this docstring is not what's actually enforced (see
tests/test_test_catalog.py; TEST_CATALOG.md's own generated header is
the real count) - this module
reads the real test suite via Python's own `ast` module and renders
the catalog from it, so "updated as more are added" means re-running
this script, not manually transcribing a new row. `code` means a
file:line pointer to the real test, not a copy of its source - a copy
would itself drift the next time someone edits the test without
remembering to update the catalog too.

Categorization is by source file (tests/test_<name>.py -> one category),
matching how this repo already organizes its suite - no new taxonomy
invented or kept in sync separately.

Usage:
    python -m evidence.test_catalog --out TEST_CATALOG.md

tests/test_test_catalog.py regenerates the catalog in memory and diffs
it against the committed TEST_CATALOG.md - the same "generated artifact
must match what the generator produces" discipline evidence/cli.py's
own test (tests/test_cli.py) already uses for the traceability matrices.
"""

import argparse
import ast
import pathlib
import re
from dataclasses import dataclass

from evidence.tracked_files import tracked_files

_MAX_DESCRIPTION_LEN = 220

# Tokens that should render as acronyms, not title-cased words, when
# turning a test filename into a category heading.
_ACRONYMS = {"cli": "CLI", "nl": "NL", "stp": "STP", "id": "ID"}

_SENTENCE_RE = re.compile(r"^(.*?[.!?])(\s|$)")


@dataclass(frozen=True)
class TestEntry:
    """One test function: enough to render one catalog row."""

    name: str
    description: str
    file: str
    line: int


@dataclass(frozen=True)
class TestCategory:
    """All tests from one tests/test_<name>.py file."""

    heading: str
    file: str
    entries: tuple


def category_heading(filename: str) -> str:
    """tests/test_hazard_id_lint.py -> "Hazard ID Lint"."""
    stem = filename[:-3] if filename.endswith(".py") else filename
    if stem.startswith("test_"):
        stem = stem[len("test_") :]
    words = stem.split("_")
    return " ".join(_ACRONYMS.get(w, w.capitalize()) for w in words)


def _first_sentence(docstring: str) -> str:
    text = " ".join(docstring.split())
    match = _SENTENCE_RE.match(text)
    sentence = match.group(1) if match else text
    if len(sentence) > _MAX_DESCRIPTION_LEN:
        sentence = sentence[: _MAX_DESCRIPTION_LEN - 1].rstrip() + "…"
    return sentence


def _description_from_name(test_name: str) -> str:
    words = test_name[len("test_") :].replace("_", " ")
    return words[:1].upper() + words[1:] + "."


def _describe(node: ast.FunctionDef) -> str:
    docstring = ast.get_docstring(node)
    if docstring:
        return _first_sentence(docstring)
    return _description_from_name(node.name)


def parse_test_file(path: pathlib.Path, repo_root: pathlib.Path) -> TestCategory:
    """Parse one tests/test_*.py file via `ast` (not import - this must
    work without the test's own dependencies installed/importable, and
    must not execute any test code) and return its TestCategory."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    rel_path = str(path.relative_to(repo_root))
    entries = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            entries.append(
                TestEntry(
                    name=node.name,
                    description=_describe(node),
                    file=rel_path,
                    line=node.lineno,
                )
            )
    entries.sort(key=lambda e: e.line)
    return TestCategory(heading=category_heading(path.name), file=rel_path, entries=tuple(entries))


def build_catalog(repo_root: pathlib.Path) -> list:
    """One TestCategory per git-tracked test_*.py file under tests/,
    sorted by filename for stable, diffable output.

    Uses the pattern "*test_*.py" (not "tests/test_*.py") and filters
    to paths under tests/ afterward - confirmed empirically that a
    literal directory prefix in a git pathspec ("tests/test_*.py")
    matches only tests/'s direct children, not a nested layout like
    tests/unit/test_nested.py, unlike a bare leading wildcard
    ("*test_*.py" or hazard_id_lint.py's "*.md"), which matches at any
    depth. This repo has no nested test files today, so the bug found
    no real damage, but it was a silent incompleteness hazard - a
    future nested test file would have been omitted with no error.
    Found by an external review (Qodo) on PR #54, not self-caught."""
    categories = []
    for path in tracked_files(repo_root, "*test_*.py"):
        rel_path = path.relative_to(repo_root)
        if rel_path.parts[0] != "tests" or not path.name.startswith("test_"):
            continue
        category = parse_test_file(path, repo_root)
        if category.entries:
            categories.append(category)
    categories.sort(key=lambda c: c.file)
    return categories


def render_markdown(categories: list) -> str:
    total_tests = sum(len(c.entries) for c in categories)
    lines = [
        "# Test Catalog — payloadguard-evidence",
        "",
        "**Generated — do not hand-edit.** Every row is read directly from",
        "the real test suite via `evidence/test_catalog.py`'s AST parser, not",
        "transcribed by hand. Regenerate after adding, renaming, or removing",
        "any test:",
        "",
        "```",
        "python -m evidence.test_catalog --out TEST_CATALOG.md",
        "```",
        "",
        "`tests/test_test_catalog.py` fails CI if this file drifts from what",
        "the generator actually produces against the committed test suite —",
        "the same discipline `evidence/cli.py`'s own tests already apply to",
        "the traceability matrices.",
        "",
        f"**Total: {total_tests} test functions across {len(categories)} categories.**",
        "Counts test *functions*, not pytest's collected test-case count -",
        "a `@pytest.mark.parametrize`-decorated function is one row here",
        "(one description, one code location) even though pytest runs it as",
        "several cases with different data. Run `python -m pytest tests/ -q`",
        "for the actual collected-case count.",
        "",
        "---",
        "",
    ]
    for category in categories:
        lines.append(f"## {category.heading} (`{category.file}`)")
        lines.append("")
        lines.append("| Test | Description | Code |")
        lines.append("|---|---|---|")
        for entry in category.entries:
            escaped_description = entry.description.replace("|", "\\|")
            lines.append(f"| `{entry.name}` | {escaped_description} | `{entry.file}:{entry.line}` |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="Output path for the generated markdown file")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root to scan (default: current directory)",
    )
    args = parser.parse_args()

    repo_root = pathlib.Path(args.repo_root).resolve()
    categories = build_catalog(repo_root)
    markdown = render_markdown(categories)
    pathlib.Path(args.out).write_text(markdown, encoding="utf-8")


if __name__ == "__main__":
    main()
