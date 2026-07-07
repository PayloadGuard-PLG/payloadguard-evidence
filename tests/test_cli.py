"""Gate 2 CLI: proves it produces the same evidence as the existing
per-variant generator scripts, driven end to end via subprocess (the way
a real user would invoke it), plus its Tier-1 error handling.
"""

import json
import pathlib
import subprocess
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ART_DIR = REPO_ROOT / "examples" / "dosage_calculator"


def _run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "evidence.cli", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def _strip_ts(matrix):
    m = dict(matrix)
    m["generated_utc"] = "TIMESTAMP"
    return m


DAFNY_CAPTURES = str(ART_DIR / "dafny_captures_index.json")


@pytest.mark.parametrize(
    "variant,metadata_name,committed_name",
    [
        ("a", "metadata.a.yaml", "traceability_matrix.a.json"),
        ("b", "metadata.b.yaml", "traceability_matrix.b.json"),
        ("c-symbolic", "metadata.c.yaml", "traceability_matrix.symbolic.json"),
        ("c-concrete", "metadata.c.yaml", "traceability_matrix.concrete.json"),
        ("c-formal", "metadata.c.yaml", "traceability_matrix.formal.json"),
    ],
)
def test_cli_build_matches_committed_artifact(tmp_path, variant, metadata_name, committed_name):
    # --dafny-captures is required for every variant here (2026-07-07,
    # Gate 2/C2-C4 wiring extended to A/B): metadata.a.yaml/b.yaml/c.yaml
    # all declare dafny evidence now, and even c-symbolic/c-concrete need
    # dafny_store passed for their own intent_ok computation to match the
    # committed artifacts (their RENDERED rows are unaffected either way -
    # see _bind_self_describing's docstring).
    out_json = tmp_path / "out.json"
    result = _run_cli(
        "build",
        "--variant", variant,
        "--metadata", str(ART_DIR / metadata_name),
        "--manifest", str(ART_DIR / "run_manifest.json"),
        "--concrete", str(ART_DIR / "concrete_results.json"),
        "--dafny-captures", DAFNY_CAPTURES,
        "--out-json", str(out_json),
    )
    assert result.returncode == 0, result.stderr
    produced = json.loads(out_json.read_text())
    committed = json.loads((ART_DIR / committed_name).read_text())
    assert _strip_ts(produced) == _strip_ts(committed)


def test_cli_writes_markdown_too(tmp_path):
    out_json = tmp_path / "out.json"
    out_md = tmp_path / "out.md"
    result = _run_cli(
        "build",
        "--variant", "a",
        "--metadata", str(ART_DIR / "metadata.a.yaml"),
        "--manifest", str(ART_DIR / "run_manifest.json"),
        "--concrete", str(ART_DIR / "concrete_results.json"),
        "--dafny-captures", DAFNY_CAPTURES,
        "--out-json", str(out_json),
        "--out-md", str(out_md),
    )
    assert result.returncode == 0, result.stderr
    assert out_md.exists()
    committed_md = (ART_DIR / "traceability_matrix.a.md").read_text()
    produced_md = out_md.read_text()
    # Only the timestamp line should differ.
    strip = lambda s: "\n".join(  # noqa: E731
        "Generated (UTC): TIMESTAMP" if line.startswith("Generated (UTC):") else line
        for line in s.splitlines()
    )
    assert strip(produced_md) == strip(committed_md)


def test_cli_prints_to_stdout_when_no_output_path_given():
    result = _run_cli(
        "build",
        "--variant", "a",
        "--metadata", str(ART_DIR / "metadata.a.yaml"),
        "--manifest", str(ART_DIR / "run_manifest.json"),
        "--concrete", str(ART_DIR / "concrete_results.json"),
        "--dafny-captures", DAFNY_CAPTURES,
    )
    assert result.returncode == 0, result.stderr
    produced = json.loads(result.stdout)
    committed = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    assert _strip_ts(produced) == _strip_ts(committed)


def test_cli_schema_validation_failure_is_a_clean_exit(tmp_path):
    bad_metadata = tmp_path / "bad.yaml"
    bad_metadata.write_text("{}\n")
    result = _run_cli(
        "build",
        "--variant", "a",
        "--metadata", str(bad_metadata),
        "--manifest", str(ART_DIR / "run_manifest.json"),
        "--concrete", str(ART_DIR / "concrete_results.json"),
    )
    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert "schema validation failed" in result.stderr
    assert "'device' is a required property" in result.stderr


def test_cli_conflict_failure_is_a_clean_exit(tmp_path):
    """Drives the CLI end to end (subprocess, real files) with a
    corrupted concrete store, proving Type 1 fires through the CLI path
    too, not just when build_matrix() is called from Python directly."""
    concrete = json.loads((ART_DIR / "concrete_results.json").read_text())
    for case in concrete["cases"]:
        if case["test_id"] == "kernel_detects_bolus_limit_exceeded":
            case["requirement_id"] = "REQ-DOSE-003"  # was REQ-GIP-1-4-12
    concrete_path = tmp_path / "concrete_results.json"
    concrete_path.write_text(json.dumps(concrete))

    result = _run_cli(
        "build",
        "--variant", "a",
        "--metadata", str(ART_DIR / "metadata.a.yaml"),
        "--manifest", str(ART_DIR / "run_manifest.json"),
        "--concrete", str(concrete_path),
    )
    assert result.returncode != 0
    assert "Traceback" not in result.stderr
    assert "Type 1, identity mismatch" in result.stderr


def test_cli_missing_required_arg_exits_nonzero():
    result = _run_cli("build", "--variant", "a")
    assert result.returncode != 0


def test_cli_tool_name_derived_from_manifest_not_hardcoded(tmp_path):
    """tool_versions is keyed by the manifest's own 'tool' field, not a
    hardcoded 'crosshair' string - a small genuine vocabulary-agnostic
    improvement over the existing generator scripts. Uses c-symbolic
    without --dafny-captures: unlike variants A/B/c-formal, that view
    doesn't require dafny_store at all (declared dafny evidence is
    silently unbound there, not refused - see
    _bind_self_describing's docstring), so it's the cleanest way to
    isolate this assertion to the manifest-derived tool name alone."""
    out_json = tmp_path / "out.json"
    _run_cli(
        "build",
        "--variant", "c-symbolic",
        "--metadata", str(ART_DIR / "metadata.c.yaml"),
        "--manifest", str(ART_DIR / "run_manifest.json"),
        "--concrete", str(ART_DIR / "concrete_results.json"),
        "--out-json", str(out_json),
    )
    produced = json.loads(out_json.read_text())
    manifest = json.loads((ART_DIR / "run_manifest.json").read_text())
    assert produced["tool_versions"] == {manifest["tool"]: manifest["tool_version"]}
