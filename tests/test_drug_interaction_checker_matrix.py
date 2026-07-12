"""Phase 3 (evidence packaging) for drug_interaction_checker: proves the
real, committed metadata.a.yaml -> evidence.cli -> traceability_matrix.a
pipeline works end to end for this example's genuinely new shape - one
Dafny function (CheckInteraction) backing five requirement rows
(REQ-DDI-1/2/3/4/5, REQ-DDI-5 built 2026-07-12), plus a second Dafny
function (DoseReductionTargetMg) backing a sixth (REQ-DDI-6, also built
2026-07-12) - the first time this repo's matrix binder has bound two
different Dafny methods from the same spec file to two different
requirements in one metadata file. No GAP rows remain in this example
as of REQ-DDI-6 - see git history / DEVLOG.md for the earlier state
where REQ-DDI-5/6 were honest, deliberate GAP rows before either was
built.

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


def test_req_ddi_5_shares_check_interaction_capture_as_a_fifth_binding():
    """REQ-DDI-5 (the TreatmentIndication axis, built 2026-07-12) binds
    the SAME CheckInteraction capture REQ-DDI-1/2/3/4 already bind - a
    fifth requirement sharing one proof, not a new capture. Real,
    PROVEN evidence, not a GAP row - this requirement was a deliberate
    GAP until REQ-DDI-5 was actually built."""
    matrix = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    by_id = {row["requirement_id"]: row for row in matrix["rows"]}
    row = by_id["REQ-DDI-5"]
    assert row["intent_ok"] is True
    assert len(row["evidence"]) == 1
    rec = row["evidence"][0]
    assert rec["method"] == "dafny"
    assert rec["strength"] == "PROVEN"
    assert rec["verifier_completion_status"] == "completed"
    assert rec["code_location"] == "drug_interaction_checker.dfy::CheckInteraction"


def test_req_ddi_6_binds_its_own_separate_dose_reduction_capture():
    """REQ-DDI-6 (the numeric dose-reduction targets, built 2026-07-12)
    binds DoseReductionTargetMg - a DIFFERENT Dafny method than
    CheckInteraction, the first time this repo's matrix binder has
    bound two different methods from the same spec file across two
    requirements in one metadata file. Real, PROVEN evidence, not a
    GAP row."""
    matrix = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    by_id = {row["requirement_id"]: row for row in matrix["rows"]}
    row = by_id["REQ-DDI-6"]
    assert row["intent_ok"] is True
    assert len(row["evidence"]) == 1
    rec = row["evidence"][0]
    assert rec["method"] == "dafny"
    assert rec["strength"] == "PROVEN"
    assert rec["verifier_completion_status"] == "completed"
    assert rec["code_location"] == "drug_interaction_checker.dfy::DoseReductionTargetMg"


def test_no_gap_rows_remain_in_this_example():
    """As of REQ-DDI-6 (2026-07-12), every one of this example's six
    requirements has real, bound evidence - confirmed directly across
    the whole matrix, not just the two rows the tests above check
    individually."""
    matrix = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    for row in matrix["rows"]:
        assert row["intent_ok"] is True, row["requirement_id"]
        assert len(row["evidence"]) >= 1, row["requirement_id"]


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
