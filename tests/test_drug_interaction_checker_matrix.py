"""Phase 3 (evidence packaging) for drug_interaction_checker: proves the
real, committed metadata.a.yaml -> evidence.cli -> traceability_matrix.a
pipeline works end to end for this example's genuinely new shape - one
Dafny function (CheckInteraction) backing four requirement rows
(REQ-DDI-1/2/3/4), plus two deliberately-unbuilt requirements
(REQ-DDI-5/6) rendered as honest GAP rows, not hidden or faked.

This example is also the first real exercise of evidence/cli.py's
--manifest/--concrete becoming optional (2026-07): no crosshair or
concrete_test evidence exists anywhere in this metadata, so both flags
are omitted entirely, not pointed at stub files - see cli.py's own
module docstring and evidence/render/matrix_variants.py::derive_bounds_block
for why that's the honest choice over fabricating empty bounds data.
"""

import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from evidence.render.matrix_variants import assert_no_realized_proven  # noqa: E402

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ART_DIR = REPO_ROOT / "examples" / "drug_interaction_checker"


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


def _build_now(tmp_path):
    out_json = tmp_path / "out.json"
    result = _run_cli(
        "build",
        "--variant", "a",
        "--metadata", str(ART_DIR / "metadata.a.yaml"),
        "--dafny-captures", str(ART_DIR / "dafny_captures_index.json"),
        "--out-json", str(out_json),
    )
    assert result.returncode == 0, result.stderr
    return json.loads(out_json.read_text())


def test_cli_omitting_manifest_and_concrete_entirely_still_works(tmp_path):
    """The real point of this test file's existence: --manifest and
    --concrete are genuinely optional now, not just defaulted to an
    empty stub file - this example passes neither flag at all."""
    produced = _build_now(tmp_path)
    committed = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    assert _strip_ts(produced) == _strip_ts(committed)


def test_cli_writes_markdown_matching_committed(tmp_path):
    out_json = tmp_path / "out.json"
    out_md = tmp_path / "out.md"
    result = _run_cli(
        "build",
        "--variant", "a",
        "--metadata", str(ART_DIR / "metadata.a.yaml"),
        "--dafny-captures", str(ART_DIR / "dafny_captures_index.json"),
        "--out-json", str(out_json),
        "--out-md", str(out_md),
    )
    assert result.returncode == 0, result.stderr
    committed_md = (ART_DIR / "traceability_matrix.a.md").read_text()
    produced_md = out_md.read_text()
    strip = lambda s: "\n".join(  # noqa: E731
        "Generated (UTC): TIMESTAMP" if line.startswith("Generated (UTC):") else line
        for line in s.splitlines()
    )
    assert strip(produced_md) == strip(committed_md)


def test_four_requirements_share_the_one_real_proof():
    """REQ-DDI-1/2/3/4 all bind to the SAME CheckInteraction capture - the
    first time this repo's matrix binder has been exercised with a
    many-requirements-to-one-proof shape (every dosage_calculator/
    renal_adjustment requirement is 1:1 with its own function)."""
    matrix = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    by_id = {row["requirement_id"]: row for row in matrix["rows"]}
    for req_id in ("REQ-DDI-1", "REQ-DDI-2", "REQ-DDI-3", "REQ-DDI-4"):
        row = by_id[req_id]
        assert row["intent_ok"] is True
        assert len(row["evidence"]) == 1
        rec = row["evidence"][0]
        assert rec["method"] == "dafny"
        assert rec["strength"] == "PROVEN"
        assert rec["verifier_completion_status"] == "completed"
        assert rec["code_location"] == "drug_interaction_checker.dfy::CheckInteraction"


def test_deferred_requirements_render_as_honest_gaps_not_hidden():
    """REQ-DDI-5/6 (indication axis, numeric dose targets) are genuinely
    unbuilt in v1 - the matrix must say so explicitly, not omit the rows
    or silently mark them satisfied."""
    matrix = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    by_id = {row["requirement_id"]: row for row in matrix["rows"]}
    for req_id in ("REQ-DDI-5", "REQ-DDI-6"):
        row = by_id[req_id]
        assert row["intent_ok"] is False
        assert row["evidence"] == []
        assert "no evidence bound for this requirement" in row["notes"]
        assert "intended PROVEN, realized GAP" in row["notes"]


def test_no_crosshair_evidence_renders_bounds_as_explicitly_not_applicable():
    """Real, notable fact about this artifact: the header's bounds block
    reads a clear N/A, not a bare 'None' that could be misread as a data
    gap rather than the honest 'no crosshair pipeline exists for this
    example' it actually is."""
    md = (ART_DIR / "traceability_matrix.a.md").read_text()
    assert "N/A (no crosshair evidence in this metadata)" in md
    matrix = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    assert matrix["crosshair_bounds"] is None
    assert matrix["bounds"]["declared"] is None
    assert matrix["bounds"]["effective"] is None


def test_committed_matrix_passes_the_structural_proven_check():
    """R3 (assert_no_realized_proven) re-checked directly against the
    real committed artifact, not just trusted because build_matrix()
    itself calls it internally at generation time."""
    matrix = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    assert_no_realized_proven(matrix)  # raises on violation
