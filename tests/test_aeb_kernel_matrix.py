"""Phase 3 (evidence packaging) for aeb_kernel: proves the real,
committed metadata.a.yaml -> evidence.cli -> traceability_matrix.a
pipeline works end to end for this example's shape - REQ-AEB-5/6/7/8
bind one function each, REQ-AEB-1/3 both bind FCWRequiredActive and
REQ-AEB-2/4 both bind AEBRequiredActive (two requirements sharing one
proof, mirroring drug_interaction_checker's established many-to-one
pattern), and REQ-AEB-9/10 are honest DECLARED gaps (named,
sourced, not yet formalized - vehicle-class eligibility and stateful
malfunction-detection/mode-control, both out of this pure-function
kernel's scope by construction, not by omission).

Like renal_adjustment/drug_interaction_checker's own matrix tests, this
example omits --manifest/--concrete entirely (no crosshair/concrete_test
evidence exists anywhere in this metadata).
"""

import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from evidence.render.matrix_variants import assert_no_realized_proven  # noqa: E402

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ART_DIR = REPO_ROOT / "examples" / "aeb_kernel"


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
        ("REQ-AEB-5", "IsSubjectVehicleBrakingOnset"),
        ("REQ-AEB-6", "IsLeadVehicleBrakingOnset"),
        ("REQ-AEB-7", "IsBrakePedalApplicationOnset"),
        ("REQ-AEB-8", "IsFalseActivationCompliant"),
    ):
        row = _row(matrix, req_id)
        assert row["intent_ok"] is True
        assert len(row["evidence"]) == 1
        rec = row["evidence"][0]
        assert rec["method"] == "dafny"
        assert rec["strength"] == "PROVEN"
        assert rec["verifier_completion_status"] == "completed"
        assert rec["code_location"] == f"aeb_kernel.dfy::{dafny_method}"


def test_fcw_required_active_backs_both_req_1_and_req_3():
    """FCWRequiredActive's ensures clause is a single function covering
    both the lead-vehicle (S5.1.1) and pedestrian (S5.2.1) envelopes -
    two distinct requirements, one proof, mirroring
    drug_interaction_checker's CheckInteraction pattern."""
    matrix = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    for req_id in ("REQ-AEB-1", "REQ-AEB-3"):
        row = _row(matrix, req_id)
        assert row["intent_ok"] is True
        methods = [e["code_location"] for e in row["evidence"]]
        assert methods == ["aeb_kernel.dfy::FCWRequiredActive"]
        assert row["evidence"][0]["strength"] == "PROVEN"


def test_aeb_required_active_backs_both_req_2_and_req_4():
    matrix = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    for req_id in ("REQ-AEB-2", "REQ-AEB-4"):
        row = _row(matrix, req_id)
        assert row["intent_ok"] is True
        methods = [e["code_location"] for e in row["evidence"]]
        assert methods == ["aeb_kernel.dfy::AEBRequiredActive"]
        assert row["evidence"][0]["strength"] == "PROVEN"


def test_declared_scope_requirements_render_as_honest_gaps():
    """REQ-AEB-9 (vehicle-class eligibility) and REQ-AEB-10 (malfunction
    detection/mode controls) are named, sourced, and deliberately not
    Dafny targets for this kernel - intended_method DECLARED, so the gap
    note reads "intended DECLARED, realized GAP", not PROVEN. Both carry
    a system_scope field (unlike renal_adjustment's REQ-RENAL-3/4/6/7/8,
    which have neither kernel_scope nor system_scope set), so the
    renderer produces one structured evidence record with strength GAP
    and scope "system_scope", not an empty evidence array."""
    matrix = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    for req_id in ("REQ-AEB-9", "REQ-AEB-10"):
        row = _row(matrix, req_id)
        assert row["intent_ok"] is False
        assert len(row["evidence"]) == 1
        rec = row["evidence"][0]
        assert rec["strength"] == "GAP"
        assert rec["scope"] == "system_scope"
        assert rec["method"] is None
        assert "intended DECLARED, realized GAP" in row["notes"]


def test_committed_matrix_passes_the_structural_proven_check():
    matrix = json.loads((ART_DIR / "traceability_matrix.a.json").read_text())
    assert_no_realized_proven(matrix)  # raises on violation
