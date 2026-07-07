"""Phase C, Gate 2/C2-C4 wiring (2026-07-07): the first real Dafny-sourced
PROVEN evidence to ever reach a live, rendered traceability matrix row -
built for variant C first ("hmm. can we post hoc verify A and B after C
variant is proven?"), then extended to variants A and B the same day
("go ahead and extend variant A and B now").

Design decisions, ratified before building: the Z3 precondition-
satisfiability check gates PROVEN inside the binder itself
(dafny_record(), not a separate pipeline stage); metadata declares the
dafny evidence explicitly (variant A/C's `evidence` list, variant B's
`.formal-N` shadow rows keyed by a .dfy implementation), cross-checked
by Gate 2 CONFLICT Type 1. Extending A/B required passing dafny_store
into ALL of variant C's build_matrix() calls too (not just "c-formal"),
so every artifact's own intent_ok computation sees the same complete
evidence picture - the CLI needed a --dafny-captures option to keep
working once metadata.a.yaml/metadata.b.yaml declared dafny evidence;
the fact-equality gate's intent comparison needed to become subset-
based, since traceability_matrix.formal.json permanently, deliberately
has no opinion about REQ-DOSE-003 (out of dosage.dfy's scope) while
every other artifact does.
"""

import json
import pathlib
import subprocess
import sys

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.conflict import dafny_binding_conflicts, run_conflict_gate  # noqa: E402
from evidence.reconcile import run_gate  # noqa: E402
from evidence.render.matrix_variants import (  # noqa: E402
    assert_no_realized_proven,
    build_matrix,
    dafny_record,
)

ART_DIR = REPO_ROOT / "examples" / "dosage_calculator"
PROVEN_REQS = {"REQ-GIP-1-4-12", "REQ-GIP-1-8-1"}


def _load(name):
    return json.loads((ART_DIR / name).read_text())


def _dafny_store():
    manifest = json.loads((ART_DIR / "run_manifest_dafny.json").read_text())
    return {
        "dosage.dfy::CalculateHourlyDose": {
            "spec_source": (ART_DIR / "dosage.dfy").read_text(),
            "raw_output": (ART_DIR / "raw_dafny_output.txt").read_text(),
            "manifest": manifest,
            "dafny_method": "CalculateHourlyDose",
        }
    }


# --------------------------------------------------- real committed artifacts

def test_real_formal_artifact_has_two_proven_rows():
    formal = _load("traceability_matrix.formal.json")
    proven = [r for r in formal["rows"] if r.get("strength") == "PROVEN"]
    assert {r["requirement_id"] for r in proven} == PROVEN_REQS
    for row in proven:
        assert row["method"] == "dafny"
        assert row["verifier_completion_status"] == "completed"
        assert row["intent_ok"] is True


def test_real_formal_artifact_passes_the_structural_proven_check():
    """assert_no_realized_proven (ruling R3) must accept this real,
    legitimate dafny-sourced PROVEN row - not just in theory (Gate C2's
    tests) but against the actual generated artifact."""
    assert_no_realized_proven(_load("traceability_matrix.formal.json"))  # must not raise


def test_variant_a_has_dafny_evidence_and_a_proven_record():
    matrix = _load("traceability_matrix.a.json")
    by_req = {row["requirement_id"]: row for row in matrix["rows"]}
    for req_id in PROVEN_REQS:
        methods = {rec["method"] for rec in by_req[req_id]["evidence"]}
        assert "dafny" in methods
        assert by_req[req_id]["intent_ok"] is True
        dafny_rec = next(r for r in by_req[req_id]["evidence"] if r["method"] == "dafny")
        assert dafny_rec["strength"] == "PROVEN"
        assert dafny_rec["verifier_completion_status"] == "completed"
    # REQ-DOSE-003 never declares dafny evidence - dosage.dfy explicitly
    # doesn't cover it - so it must show no dafny record, still True via
    # crosshair/concrete_test alone (unchanged from before this wiring).
    assert all(r["method"] != "dafny" for r in by_req["REQ-DOSE-003"]["evidence"])
    assert by_req["REQ-DOSE-003"]["intent_ok"] is True


def test_variant_b_has_dafny_shadow_rows_and_a_proven_record():
    matrix = _load("traceability_matrix.b.json")
    dafny_rows = [r for r in matrix["rows"] if r.get("method") == "dafny"]
    assert {r["parent_requirement"] for r in dafny_rows} == PROVEN_REQS
    for row in dafny_rows:
        assert row["requirement_id"].endswith(".formal-1")
        assert row["strength"] == "PROVEN"
        assert row["verifier_completion_status"] == "completed"
        assert row["intent_ok"] is True
    parents = {row["requirement_id"]: row for row in matrix["rows"] if row.get("parent_requirement") is None}
    for req_id in PROVEN_REQS:
        assert parents[req_id]["intent_ok"] is True
    assert parents["REQ-DOSE-003"]["intent_ok"] is True


def test_full_fact_equality_gate_passes_with_intent_true_everywhere():
    """The end state this whole extension was for: run_gate() (unchanged
    core logic, now including traceability_matrix.formal.json as a full
    peer) passes with intent_ok True for both formally-proven
    requirements across every variant artifact."""
    result = run_gate(ART_DIR)
    assert result["intent"] == {
        "REQ-GIP-1-4-12": True,
        "REQ-GIP-1-8-1": True,
        "REQ-DOSE-003": True,
    }


def test_reconcile_intent_comparison_is_subset_not_strict_equality(tmp_path):
    """The load-bearing fix that made folding formal.json into run_gate()
    possible: a variant missing a requirement entirely (formal.json never
    has one for REQ-DOSE-003) must not fail the gate on that basis alone
    - only an actual VALUE mismatch on a shared requirement, or a
    completely unknown requirement id, is still a hard failure."""
    for name in (
        "traceability_matrix.a.json",
        "traceability_matrix.b.json",
        "traceability_matrix.symbolic.json",
        "traceability_matrix.concrete.json",
        "traceability_matrix.formal.json",
        "traceability_matrix.json",
    ):
        (tmp_path / name).write_text((ART_DIR / name).read_text())

    # Sanity: the real committed formal.json already lacks a REQ-DOSE-003
    # row, and the gate already passes on the untouched copies.
    run_gate(tmp_path)

    # Now flip an ACTUAL shared value - must still fail.
    mutated = json.loads((tmp_path / "traceability_matrix.formal.json").read_text())
    for row in mutated["rows"]:
        if row["requirement_id"] == "REQ-GIP-1-4-12":
            row["intent_ok"] = False
    (tmp_path / "traceability_matrix.formal.json").write_text(json.dumps(mutated))
    with pytest.raises(AssertionError, match="intent_ok differs"):
        run_gate(tmp_path)


def test_reconcile_still_rejects_a_completely_unknown_requirement(tmp_path):
    """Subset semantics must not become 'anything goes': a requirement id
    the other artifacts have never heard of at all is still a hard
    failure - caught here by the facts-equality check (an even earlier,
    stricter gate than the intent comparison, since a genuinely new
    requirement id necessarily introduces a genuinely new fact tuple no
    other artifact shares)."""
    for name in (
        "traceability_matrix.a.json",
        "traceability_matrix.b.json",
        "traceability_matrix.symbolic.json",
        "traceability_matrix.concrete.json",
        "traceability_matrix.formal.json",
        "traceability_matrix.json",
    ):
        (tmp_path / name).write_text((ART_DIR / name).read_text())
    mutated = json.loads((tmp_path / "traceability_matrix.formal.json").read_text())
    mutated["rows"].append(
        {
            "requirement_id": "REQ-DOES-NOT-EXIST",
            "requirement_text": "synthetic fixture row",
            "code_location": None,
            "method": "dafny",
            "strength": "PROVEN",
            "caveat": "x",
            "result_status": "proven",
            "bounds": None,
            "counterexample": None,
            "test_id": None,
            "inputs": None,
            "expected": None,
            "observed": None,
            "verifier_completion_status": "completed",
            "intent_ok": True,
            "notes": [],
        }
    )
    (tmp_path / "traceability_matrix.formal.json").write_text(json.dumps(mutated))
    with pytest.raises(AssertionError, match="fact sets differ"):
        run_gate(tmp_path)


# ------------------------------------------------------------- the Z3 gate

def test_dafny_record_refuses_an_unsatisfiable_precondition():
    """The Z3 gate lives inside the binder (dafny_record), as decided.
    A capture whose spec has a vacuous precondition must be refused even
    if the capture itself is a real, clean Dafny pass."""
    manifest = json.loads((ART_DIR / "run_manifest_dafny.json").read_text())
    vacuous_source = """
    method Vacuous(x: int) returns (r: int)
      requires x > 0 && x < 0
      ensures r == 999999
    {
      r := 0;
    }
    """
    capture = {
        "spec_source": vacuous_source,
        "dafny_method": "Vacuous",
        "raw_output": "Dafny program verifier finished with 1 verified, 0 errors",
        "manifest": {**manifest, "target": "whatever.dfy"},
    }
    with pytest.raises(SystemExit, match="precondition check reports 'unsat'"):
        dafny_record(capture, "whatever.dfy::Vacuous")


def test_dafny_record_still_enforces_the_false_zero_guard():
    """The second, independent gate (Gate C1's parser) still applies -
    a broken capture must be refused even with a perfectly satisfiable
    precondition."""
    capture = {
        "spec_source": (ART_DIR / "dosage.dfy").read_text(),
        "dafny_method": "CalculateHourlyDose",
        "raw_output": "Dafny program verifier finished with 0 verified, 2 errors",
        "manifest": {"target": "dosage.dfy", "exit_code": 4, "started_utc": "x"},
    }
    with pytest.raises(SystemExit, match="does not report a clean pass"):
        dafny_record(capture, "dosage.dfy::CalculateHourlyDose")


def test_dafny_record_accepts_the_real_committed_capture():
    store = _dafny_store()
    record = dafny_record(store["dosage.dfy::CalculateHourlyDose"], "dosage.dfy::CalculateHourlyDose")
    assert record["strength"] == "PROVEN"
    assert record["method"] == "dafny"
    assert record["verifier_completion_status"] == "completed"


# ------------------------------------------------------ CONFLICT Type 1

def test_dafny_binding_conflict_catches_a_spec_target_mismatch():
    metadata = {
        "requirements": [
            {
                "id": "REQ-FIXTURE",
                "evidence": [
                    {"method": "dafny", "spec_target": "wrong.dfy", "dafny_method": "CalculateHourlyDose"}
                ],
            }
        ]
    }
    store = _dafny_store()  # keyed by dosage.dfy::CalculateHourlyDose, manifest target is dosage.dfy
    # Declare a key that resolves (same dafny_method, mismatched spec_target
    # relative to what's actually in the store) by pointing at a
    # differently-keyed but still-present capture to exercise the
    # target-mismatch branch specifically, not the missing-key branch.
    store["wrong.dfy::CalculateHourlyDose"] = dict(store["dosage.dfy::CalculateHourlyDose"])
    conflicts = dafny_binding_conflicts(metadata, store)
    assert len(conflicts) == 1
    assert conflicts[0]["class"] == "dafny_binding"
    assert conflicts[0]["declared_target_file"] == "wrong.dfy"
    assert conflicts[0]["manifest_target_file"] == "dosage.dfy"


def test_dafny_binding_conflict_catches_a_missing_capture():
    metadata = {
        "requirements": [
            {
                "id": "REQ-FIXTURE",
                "evidence": [
                    {"method": "dafny", "spec_target": "nope.dfy", "dafny_method": "Nope"}
                ],
            }
        ]
    }
    conflicts = dafny_binding_conflicts(metadata, {})
    assert len(conflicts) == 1
    assert conflicts[0]["declared_key"] == "nope.dfy::Nope"
    assert conflicts[0]["evidence_store_owner"] is None


def test_dafny_binding_conflict_catches_a_shadow_spec_target_mismatch():
    """Variant B's dafny shadow shape, not just A/C's evidence list -
    the parent id is what gets reported as the declared owner."""
    metadata = {
        "requirements": [
            {
                "id": "REQ-FIXTURE.formal-1",
                "parent_requirement": "REQ-FIXTURE",
                "implementation": "wrong.dfy::CalculateHourlyDose",
            }
        ]
    }
    store = _dafny_store()
    store["wrong.dfy::CalculateHourlyDose"] = dict(store["dosage.dfy::CalculateHourlyDose"])
    conflicts = dafny_binding_conflicts(metadata, store)
    assert len(conflicts) == 1
    assert conflicts[0]["declared_owner"] == "REQ-FIXTURE"
    assert conflicts[0]["declared_via"] == "REQ-FIXTURE.formal-1"
    assert conflicts[0]["declared_target_file"] == "wrong.dfy"


def test_dafny_binding_conflict_is_a_noop_when_dafny_store_is_none():
    """A caller that never intends to bind dafny evidence at all - the
    conflict check must not fire just because metadata happens to
    declare it."""
    metadata = {
        "requirements": [
            {
                "id": "REQ-FIXTURE",
                "evidence": [
                    {"method": "dafny", "spec_target": "nope.dfy", "dafny_method": "Nope"}
                ],
            }
        ]
    }
    assert dafny_binding_conflicts(metadata, None) == []


def test_real_metadata_and_dafny_store_have_no_conflicts():
    for meta_name in ("metadata.a.yaml", "metadata.b.yaml", "metadata.c.yaml"):
        metadata = yaml.safe_load((ART_DIR / meta_name).read_text())
        concrete_store = _load("concrete_results.json")
        manifest = _load("run_manifest.json")
        result = run_conflict_gate(metadata, concrete_store, manifest, dafny_store=_dafny_store())
        assert result["conflicts"] == 0, meta_name


# --------------------------------------------------------- end-to-end build

def test_build_matrix_c_formal_end_to_end_matches_committed():
    metadata = yaml.safe_load((ART_DIR / "metadata.c.yaml").read_text())
    manifest = _load("run_manifest.json")
    concrete_store = _load("concrete_results.json")
    dafny_manifest = json.loads((ART_DIR / "run_manifest_dafny.json").read_text())
    matrix, _ = build_matrix(
        "c-formal",
        metadata,
        manifest,
        concrete_store,
        tool_versions={
            "crosshair": manifest["tool_version"],
            "dafny": dafny_manifest["tool_version"],
        },
        dafny_store=_dafny_store(),
    )
    committed = _load("traceability_matrix.formal.json")
    produced = dict(matrix)
    produced["generated_utc"] = "TIMESTAMP"
    committed = dict(committed)
    committed["generated_utc"] = "TIMESTAMP"
    assert produced == committed


# --------------------------------------------------------------------- CLI

def _run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "evidence.cli", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize(
    "variant,metadata_name,committed_name",
    [
        ("a", "metadata.a.yaml", "traceability_matrix.a.json"),
        ("b", "metadata.b.yaml", "traceability_matrix.b.json"),
    ],
)
def test_cli_build_matches_committed_with_dafny_captures(tmp_path, variant, metadata_name, committed_name):
    """The CLI regression this wiring would otherwise have caused: once
    metadata.a.yaml/metadata.b.yaml declare dafny evidence, the CLI must
    be given --dafny-captures or build_matrix() refuses outright - this
    is what keeps that path working, not just variant C's."""
    out_json = tmp_path / "out.json"
    result = _run_cli(
        "build",
        "--variant", variant,
        "--metadata", str(ART_DIR / metadata_name),
        "--manifest", str(ART_DIR / "run_manifest.json"),
        "--concrete", str(ART_DIR / "concrete_results.json"),
        "--dafny-captures", str(ART_DIR / "dafny_captures_index.json"),
        "--out-json", str(out_json),
    )
    assert result.returncode == 0, result.stderr
    produced = json.loads(out_json.read_text())
    committed = _load(committed_name)
    produced["generated_utc"] = "TIMESTAMP"
    committed["generated_utc"] = "TIMESTAMP"
    assert produced == committed


def test_cli_refuses_variant_a_without_dafny_captures():
    """Confirms the regression is real, not hypothetical: without
    --dafny-captures, the CLI must refuse (not silently drop the dafny
    evidence) once metadata.a.yaml declares it."""
    result = _run_cli(
        "build",
        "--variant", "a",
        "--metadata", str(ART_DIR / "metadata.a.yaml"),
        "--manifest", str(ART_DIR / "run_manifest.json"),
        "--concrete", str(ART_DIR / "concrete_results.json"),
    )
    assert result.returncode != 0
    assert "dafny_store" in result.stderr or "dafny evidence" in result.stderr
