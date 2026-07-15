"""Regression coverage for evidence/tracked_files.py - the fix for a
real gap an external reviewer (Qodo) found on PR #51: the two lint
modules' docstrings claimed to scan "tracked" markdown but actually
walked the filesystem, so untracked/generated .md files (this repo's
own working tree already had two, from pytest's own cache directory)
could affect results.
"""

import pathlib
import subprocess
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.tracked_files import tracked_files  # noqa: E402


def _git_init(repo_dir: pathlib.Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=repo_dir, check=True)


def _git_add(repo_dir: pathlib.Path, *relative_paths: str) -> None:
    subprocess.run(["git", "add", "--", *relative_paths], cwd=repo_dir, check=True)


def test_returns_only_staged_files_matching_pattern(tmp_path):
    _git_init(tmp_path)
    (tmp_path / "a.md").write_text("tracked")
    (tmp_path / "b.txt").write_text("wrong extension")
    _git_add(tmp_path, "a.md", "b.txt")

    result = tracked_files(tmp_path, "*.md")

    assert result == [tmp_path / "a.md"]


def test_untracked_file_is_not_returned(tmp_path):
    """The exact case Qodo's review asked for: an untracked .md file
    present on disk (e.g. a local scratch note, or something a tool
    generated - this repo's real pytest cache README is the concrete
    precedent) must not affect the result."""
    _git_init(tmp_path)
    (tmp_path / "tracked.md") .write_text("staged")
    _git_add(tmp_path, "tracked.md")
    (tmp_path / "untracked.md").write_text("never staged")

    result = tracked_files(tmp_path, "*.md")

    assert result == [tmp_path / "tracked.md"]


def test_matches_nested_paths(tmp_path):
    nested_dir = tmp_path / "examples" / "thing"
    nested_dir.mkdir(parents=True)
    (nested_dir / "HAZARD_REGISTER.md").write_text("nested")
    _git_init(tmp_path)
    _git_add(tmp_path, "examples/thing/HAZARD_REGISTER.md")

    result = tracked_files(tmp_path, "*HAZARD_REGISTER.md")

    assert result == [nested_dir / "HAZARD_REGISTER.md"]


def test_no_matches_returns_empty_list(tmp_path):
    _git_init(tmp_path)
    (tmp_path / "a.txt").write_text("not markdown")
    _git_add(tmp_path, "a.txt")

    assert tracked_files(tmp_path, "*.md") == []


def test_raises_clear_error_when_not_a_git_repository(tmp_path):
    """Deliberately refuses to fall back to a filesystem walk on git
    failure - that fallback would silently reintroduce the exact
    untracked-file problem this module exists to avoid."""
    with pytest.raises(RuntimeError, match="git ls-files failed"):
        tracked_files(tmp_path, "*.md")
