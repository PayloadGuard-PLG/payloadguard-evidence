"""Phase C, Gate 2/C2-C4 wiring (2026-07-07): the first real Dafny-sourced
PROVEN evidence to ever reach a live, rendered traceability matrix row.

Scope, as decided with Steven before this was built: variant C only
(extending Gate 5's existing dual-matrix pattern with a third partition,
traceability_matrix.formal.json); the Z3 precondition-satisfiability
check gates PROVEN inside the binder itself (dafny_record(), not a
separate pipeline stage); metadata.c.yaml declares the dafny evidence
explicitly, cross-checked by Gate 2 CONFLICT Type 1. Variant A/B's own
extension is an explicitly deferred follow-up ("post hoc verify A and B
after C is proven") - covered here only by confirming they are
completely unaffected, not by giving them dafny evidence too.
"""

import json
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.conflict import dafny_binding_conflicts, run_conflict_gate  # noqa: E402
from evidence.reconcile import (  # noqa: E402
    KNOWN_FORMAL_INTENT_DIVERGENCE,
    run_formal_check,
    run_gate,
)
from evidence.render.matrix_variants import (  # noqa: E402
    assert_no_realized_proven,
    build_matrix,
    dafny_record,
)

ART_DIR = REPO_ROOT / "examples" / "dosage_calculator"


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


# --------------------------------------------------- real committed artifact

def test_real_formal_artifact_has_two_proven_rows():
    formal = _load("traceability_matrix.formal.json")
    proven = [r for r in formal["rows"] if r.get("strength") == "PROVEN"]
    assert {r["requirement_id"] for r in proven} == {
        "REQ-GIP-1-4-12",
        "REQ-GIP-1-8-1",
    }
    for row in proven:
        assert row["method"] == "dafny"
        assert row["verifier_completion_status"] == "completed"
        assert row["intent_ok"] is True


def test_real_formal_artifact_passes_the_structural_proven_check():
    """assert_no_realized_proven (ruling R3) must accept this real,
    legitimate dafny-sourced PROVEN row - not just in theory (Gate C2's
    tests) but against the actual generated artifact."""
    assert_no_realized_proven(_load("traceability_matrix.formal.json"))  # must not raise


def test_symbolic_and_concrete_views_are_unaffected_by_the_wiring():
    """Regression: dafny_store defaults to None for c-symbolic/c-concrete
    - no dafny rows should ever appear there, and intent_ok for the two
    newly-proven requirements must stay exactly what it was before this
    wiring existed (False - the whole reason the formal view's divergence
    is real and worth naming, not imagined)."""
    for name in ("traceability_matrix.symbolic.json", "traceability_matrix.concrete.json"):
        matrix = _load(name)
        assert all(r.get("method") != "dafny" for r in matrix["rows"])
        for row in matrix["rows"]:
            if row["requirement_id"] in ("REQ-GIP-1-4-12", "REQ-GIP-1-8-1"):
                assert row["intent_ok"] is False


def test_variant_a_and_b_are_completely_untouched():
    """Deferred, not silently done anyway: A/B must show no dafny
    evidence and no intent_ok flip - confirms 'post hoc verify A and B'
    is still ahead, not accidentally already done."""
    for name in ("traceability_matrix.a.json", "traceability_matrix.b.json"):
        matrix = _load(name)
        raw = json.dumps(matrix)
        assert '"dafny"' not in raw
        for row in matrix["rows"]:
            req = row.get("parent_requirement") or row.get("requirement_id")
            if req in ("REQ-GIP-1-4-12", "REQ-GIP-1-8-1"):
                assert row["intent_ok"] is False


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


def test_dafny_binding_conflict_is_a_noop_when_dafny_store_is_none():
    """The symbolic/concrete views' own regression guard: dafny_store is
    None there (not merely empty), and the conflict check must not fire
    just because the metadata happens to declare dafny evidence meant
    for the third view."""
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
    metadata = __import__("yaml").safe_load((ART_DIR / "metadata.c.yaml").read_text())
    concrete_store = _load("concrete_results.json")
    manifest = _load("run_manifest.json")
    result = run_conflict_gate(metadata, concrete_store, manifest, dafny_store=_dafny_store())
    assert result["conflicts"] == 0


# ------------------------------------------------- reconcile.run_formal_check

def test_run_formal_check_passes_on_the_real_committed_artifacts():
    reference = run_gate(ART_DIR)["intent"]
    result = run_formal_check(ART_DIR, reference)
    assert set(result["known_divergence"]) == KNOWN_FORMAL_INTENT_DIVERGENCE


def _copy_artifacts_for_formal_check(tmp_path):
    for name in (
        "traceability_matrix.a.json",
        "traceability_matrix.b.json",
        "traceability_matrix.symbolic.json",
        "traceability_matrix.concrete.json",
        "traceability_matrix.formal.json",
        "traceability_matrix.json",
    ):
        (tmp_path / name).write_text((ART_DIR / name).read_text())


def test_run_formal_check_catches_an_unnamed_divergence(tmp_path):
    """Anything diverging OUTSIDE the two named requirements must still
    hard-fail - the carve-out is narrow, not a blanket pass. REQ-DOSE-003
    has no row in the formal view today (it declares no dafny evidence),
    so a synthetic row is added with intent_ok deliberately opposite the
    reference (True) - a clean, unambiguous unnamed divergence."""
    _copy_artifacts_for_formal_check(tmp_path)
    mutated = json.loads((tmp_path / "traceability_matrix.formal.json").read_text())
    mutated["rows"].append(
        {
            "requirement_id": "REQ-DOSE-003",
            "requirement_text": "synthetic fixture row",
            "code_location": None,
            "method": None,
            "strength": "GAP",
            "caveat": "x",
            "result_status": None,
            "bounds": None,
            "counterexample": None,
            "test_id": None,
            "inputs": None,
            "expected": None,
            "observed": None,
            "verifier_completion_status": None,
            "intent_ok": False,
            "notes": [],
        }
    )
    (tmp_path / "traceability_matrix.formal.json").write_text(json.dumps(mutated))

    reference = run_gate(tmp_path)["intent"]
    assert reference["REQ-DOSE-003"] is True  # confirms the mutation is a real flip
    with pytest.raises(AssertionError, match="unexpected divergence"):
        run_formal_check(tmp_path, reference)


def test_run_formal_check_catches_a_wrong_direction_divergence(tmp_path):
    """If a named requirement somehow ISN'T True in the formal view
    (e.g. a corrupted regeneration), that must fail too - the carve-out
    only permits the specific direction dafny evidence is supposed to
    produce. Both of REQ-GIP-1-4-12's rows (the dafny PROVEN row and its
    system_scope GAP row) are mutated together so extract_intent's own
    per-artifact-uniformity check (a separate, unrelated invariant) isn't
    what fires instead of the divergence check under test."""
    _copy_artifacts_for_formal_check(tmp_path)
    mutated = json.loads((tmp_path / "traceability_matrix.formal.json").read_text())
    for row in mutated["rows"]:
        if row["requirement_id"] == "REQ-GIP-1-4-12":
            row["intent_ok"] = False
    (tmp_path / "traceability_matrix.formal.json").write_text(json.dumps(mutated))

    reference = run_gate(tmp_path)["intent"]
    with pytest.raises(AssertionError, match="expected .* to be newly proven"):
        run_formal_check(tmp_path, reference)


# --------------------------------------------------------- end-to-end build

def test_build_matrix_c_formal_end_to_end_matches_committed():
    import yaml

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
