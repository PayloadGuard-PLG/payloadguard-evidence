"""Phase 3 (evidence packaging) for renal_adjustment: proves the real,
committed metadata.a.yaml -> evidence.cli -> traceability_matrix.a
pipeline works end to end for this example's one-row-per-function shape
(REQ-RENAL-1/1a/2/5), the dual-cited AssessRenalFunction row
(REQ-RENAL-1 and REQ-RENAL-2 both bind it, mirroring the .dfy file's own
REQ-RENAL-1, REQ-RENAL-2 inline citation), and two distinct kinds of
deliberately-unbuilt requirement: REQ-RENAL-3/4/6/7 (prose only, a real
future Dafny-formalization candidate - intended_method PROVEN) and
REQ-RENAL-8 (a permanent trust boundary that will never be
Dafny-checkable, whose provenance answer is parked pending real-world
process data - intended_method DECLARED). Both render as honest GAP rows
either way, but with different note text.

Like drug_interaction_checker's own matrix test, this example omits
--manifest/--concrete entirely (no crosshair/concrete_test evidence
exists anywhere in this metadata) - see evidence/cli.py's module
docstring for why that's the honest choice.
"""

import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from evidence.render.matrix_variants import assert_no_realized_proven  # noqa: E402

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ART_DIR = REPO_ROOT / "examples" / "renal_adjustment"


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


def test_cli_omitting_manifest_and_concrete_entirely_still_works(tmp_path):
    out_json = tmp_path / "out.json"
    result = _run_cli(
        "build",
        "--variant", "a",
        "--metadata", str(ART_DIR / "metadata.a.yaml"),
        "--dafny-captures", str(ART_DIR / "dafny_captures_index.json"),
        "--out-json", str(out_json),
    )
    assert result.returncode == 0, result.stderr
    produced = json.loads(out_json.read_text())
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


def _row(matrix, req_id):
    return next(r for r in matrix["rows"] if r["requirement_id"] == req_id)


def test_single_function_requirements_bind_correctly():
    matrix = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    for req_id, dafny_method in (
        ("REQ-RENAL-1a", "RoundHalfUp"),
        ("REQ-RENAL-5", "ComposedCeiling"),
    ):
        row = _row(matrix, req_id)
        assert row["intent_ok"] is True
        assert len(row["evidence"]) == 1
        rec = row["evidence"][0]
        assert rec["method"] == "dafny"
        assert rec["strength"] == "PROVEN"
        assert rec["verifier_completion_status"] == "completed"
        assert rec["code_location"] == f"renal_adjustment.dfy::{dafny_method}"


def test_dual_cited_assess_renal_function_backs_both_req_1_and_req_2():
    """AssessRenalFunction is tagged REQ-RENAL-1, REQ-RENAL-2 inline in
    the real .dfy file - its evidence must appear in BOTH rows, not just
    one, mirroring that dual citation exactly."""
    matrix = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    for req_id in ("REQ-RENAL-1", "REQ-RENAL-2"):
        row = _row(matrix, req_id)
        assert row["intent_ok"] is True
        methods = [e["code_location"] for e in row["evidence"]]
        assert "renal_adjustment.dfy::AssessRenalFunction" in methods
        for rec in row["evidence"]:
            assert rec["strength"] == "PROVEN"
            assert rec["verifier_completion_status"] == "completed"


def test_req_renal_1_covers_gstage_and_assess_renal_function():
    matrix = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    row = _row(matrix, "REQ-RENAL-1")
    methods = {e["code_location"] for e in row["evidence"]}
    assert methods == {
        "renal_adjustment.dfy::GStage",
        "renal_adjustment.dfy::AssessRenalFunction",
    }


def test_req_renal_2_covers_formula_selection_and_crcl_computation():
    """The unnumbered CrCl-computation functions (CockcroftGaultCrClMlPerMin,
    AssessRenalFunctionFromInputs - neither carries its own REQ-ID
    citation in the .dfy file) are attached here rather than given a new
    requirement ID, per the plan's own recommendation."""
    matrix = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    row = _row(matrix, "REQ-RENAL-2")
    methods = {e["code_location"] for e in row["evidence"]}
    assert methods == {
        "renal_adjustment.dfy::SelectFormula",
        "renal_adjustment.dfy::AssessRenalFunction",
        "renal_adjustment.dfy::CockcroftGaultCrClMlPerMin",
        "renal_adjustment.dfy::AssessRenalFunctionFromInputs",
    }


def test_prose_only_requirements_render_as_honest_gaps_intending_proven():
    """REQ-RENAL-3/4/6/7 are real future Dafny-formalization candidates,
    not yet built - intended_method PROVEN, so the gap note reads
    "intended PROVEN, realized GAP", correctly signaling unmet ambition
    rather than something nobody ever meant to prove."""
    matrix = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    for req_id in ("REQ-RENAL-3", "REQ-RENAL-4", "REQ-RENAL-6", "REQ-RENAL-7"):
        row = _row(matrix, req_id)
        assert row["intent_ok"] is False
        assert row["evidence"] == []
        assert "intended PROVEN, realized GAP" in row["notes"]


def test_req_renal_8_is_a_declared_gap_parked_for_process_data_not_a_proof_target():
    """REQ-RENAL-8 (classification-flag provenance): its trust boundary
    is permanent and will never be a Dafny proof target - genuinely
    different from REQ-RENAL-3/4/6/7's "not yet formalized" gaps, since
    nobody ever intends to Dafny-prove who populates a caller-supplied
    boolean. Its provenance answer is parked pending real-world process
    data (being gathered 2026-07-11), so it stays a GAP for now; when it
    lands it will be a DECLARED process fact, not a proof. intended_method
    DECLARED, so the note correctly reads "intended DECLARED, realized
    GAP", not PROVEN."""
    matrix = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    row = _row(matrix, "REQ-RENAL-8")
    assert row["intent_ok"] is False
    assert row["evidence"] == []
    assert "intended DECLARED, realized GAP" in row["notes"]


def test_committed_matrix_passes_the_structural_proven_check():
    matrix = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    assert_no_realized_proven(matrix)  # raises on violation
