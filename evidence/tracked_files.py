"""Shared helper: enumerate git-tracked files matching a pattern, so
repo self-consistency lints (hazard_id_lint.py, citation_registry.py)
scan the committed tree rather than whatever untracked or generated
files happen to sit in the working directory.

Built 2026-07-15, fixing a real gap found by an external reviewer
(Qodo) on PR #51: both lints' docstrings claimed to scan "tracked"
markdown, but the original implementation used `Path.rglob("*.md")`,
which walks the actual filesystem regardless of git status. Confirmed
concretely, not hypothetically - this repo's own working tree already
had two untracked, pytest-generated files at the time
(`.pytest_cache/README.md`, `examples/dosage_calculator/.pytest_cache/README.md`)
that `rglob` would have picked up on the next scan. Neither happened to
trip either lint's pattern, but the regression tests' pass/fail was
already resting on workspace contents rather than the committed tree -
exactly the kind of quiet, environment-dependent fragility this repo's
own CI-reproducibility discipline (see .github/workflows/tests.yml's
comment on why it avoids live subprocess calls to external tools)
argues against.
"""

import pathlib
import subprocess


def tracked_files(repo_root: pathlib.Path, pattern: str) -> list:
    """Git-tracked files under repo_root matching `pattern` (a git
    pathspec glob, e.g. "*.md" or "*HAZARD_REGISTER.md" - note a bare
    literal filename with no wildcard does NOT match nested paths in
    `git ls-files`, confirmed empirically; a leading `*` does), as
    absolute Path objects, sorted for deterministic output.

    Raises RuntimeError if `git` itself fails (not a git repository,
    git not installed, etc.) - deliberately NOT falling back to a
    filesystem walk on failure, which would silently reintroduce the
    exact untracked-file problem this helper exists to avoid. A lint
    that can't confirm it's looking at the committed tree should refuse
    outright, not guess."""
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", pattern],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git ls-files failed (exit {result.returncode}) in {repo_root}: "
            f"{result.stderr.strip()}. Refusing to fall back to a filesystem "
            "walk, which would scan untracked/generated files instead of the "
            "committed tree this lint is supposed to check."
        )
    relative_paths = [p for p in result.stdout.split("\0") if p]
    return sorted(repo_root / p for p in relative_paths)
