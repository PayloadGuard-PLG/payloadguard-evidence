import pathlib
import subprocess
import sys

# Make the example kernel and its fixtures importable by the test suite.
sys.path.insert(
    0,
    str(pathlib.Path(__file__).resolve().parent.parent / "examples" / "dosage_calculator"),
)


def make_git_repo(tmp_path: pathlib.Path, files: dict, *, stage: tuple = None) -> pathlib.Path:
    """Shared test helper: write `files` (relative path -> content)
    under tmp_path, git-init it, and stage either `stage` (a tuple of
    relative paths) or, if not given, every file just written. Used by
    tests/test_hazard_id_lint.py and tests/test_citation_registry.py,
    both of which scan only git-tracked files via
    evidence/tracked_files.py (added 2026-07-15 after an external
    review found the original implementation scanned the filesystem
    regardless of git status) - a bare tmp_path with no `.git` no
    longer works as a fixture for either lint's unit tests."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    for relative_path, content in files.items():
        full_path = tmp_path / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
    to_stage = stage if stage is not None else tuple(files.keys())
    if to_stage:
        subprocess.run(["git", "add", "--", *to_stage], cwd=tmp_path, check=True)
    return tmp_path
