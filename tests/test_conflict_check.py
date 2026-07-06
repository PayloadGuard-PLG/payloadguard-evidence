"""Gate 2 CONFLICT rule, Type 1 (identity mismatch) — committed test.

Exercises the three ratified test cases (KNOWN_LIMITATIONS.md, Gate 2)
against real committed data wherever possible, and in-memory mutated
fixtures for the failure cases (no corrupted fixture is committed).
"""

import json
import pathlib
import sys

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.conflict import (  # noqa: E402
    concrete_binding_conflicts,
    outcome_conflicts,
    run_conflict_gate,
    run_outcome_gate,
    symbolic_binding_conflicts,
)
from evidence.render.matrix_variants import build_matrix  # noqa: E402

ART_DIR = REPO_ROOT / "examples" / "dosage_calculator"


def _load(name):
    text = (ART_DIR / name).read_text()
    return yaml.safe_load(text) if name.endswith(".yaml") else json.loads(text)


def test_gate_passes_on_committed_variant_a():
    result = run_conflict_gate(
        _load("metadata.a.yaml"), _load("concrete_results.json"), _load("run_manifest.json")
    )
    assert result["conflicts"] == 0
    assert result["bindings_checked"] > 0


def test_gate_passes_on_committed_variant_b():
    result = run_conflict_gate(
        _load("metadata.b.yaml"), _load("concrete_results.json"), _load("run_manifest.json")
    )
    assert result["conflicts"] == 0
    assert result["bindings_checked"] > 0


def test_gate_passes_on_committed_variant_c():
    """Gate 4's asymmetry (variant C declared no top-down binding, so
    Type 1 had nothing to check there) closed 2026-07-06: metadata.c.yaml
    now carries the same top-down evidence declarations as variant A,
    for cross-checking only - C's binding stays evidence-store-carried."""
    metadata = _load("metadata.c.yaml")
    result = run_conflict_gate(
        metadata, _load("concrete_results.json"), _load("run_manifest.json")
    )
    assert result["conflicts"] == 0
    # 3 requirements x 1 concrete_test each + 3 symbolic = 6 concrete-side
    # bindings' worth of declarations feeding the check (4 test_id
    # declarations total: kernel_detects, ordinary_negative,
    # overflow_negative, normal_in_range) + 3 symbolic = 7.
    assert result["bindings_checked"] == 7


def test_negative_case_scope_split_is_not_a_conflict():
    """Gate 2's ratified negative test case: REQ-GIP-1-4-12's kernel_scope
    (evidenced) vs. system_scope (explicit GAP, no claim at all) is a
    documented absence, not a conflict. The real committed metadata
    carries this split and must still pass clean."""
    metadata = _load("metadata.a.yaml")
    req = next(r for r in metadata["requirements"] if r["id"] == "REQ-GIP-1-4-12")
    assert "system_scope" in req and "kernel_scope" in req
    result = run_conflict_gate(
        metadata, _load("concrete_results.json"), _load("run_manifest.json")
    )
    assert result["conflicts"] == 0


def test_positive_type1_concrete_identity_mismatch():
    """Gate 2's ratified positive Type 1 case: a top-down declared binding
    disagrees with the bottom-up evidence-store's self-declared owner."""
    metadata = {
        "requirements": [
            {
                "id": "REQ-X",
                "evidence": [{"method": "concrete_test", "test_id": "some_case"}],
            }
        ]
    }
    concrete_store = {
        "cases": [{"test_id": "some_case", "requirement_id": "REQ-Y-NOT-X"}]
    }
    conflicts = concrete_binding_conflicts(metadata, concrete_store)
    assert conflicts == [
        {
            "type": "identity_mismatch",
            "class": "concrete_binding",
            "declared_owner": "REQ-X",
            "declared_via": "REQ-X",
            "test_id": "some_case",
            "evidence_store_owner": "REQ-Y-NOT-X",
        }
    ]
    with pytest.raises(AssertionError, match="Type 1, identity mismatch"):
        run_conflict_gate(metadata, concrete_store, {"target": "irrelevant.py", "requirements": []})


def test_positive_type1_shadow_binding_mismatch():
    """Same failure shape via variant B's shadow-pseudo-requirement form."""
    metadata = {
        "requirements": [
            {
                "id": "REQ-X.concrete-1",
                "parent_requirement": "REQ-X",
                "implementation": "tests/test_dosage_concrete.py::some_case",
            }
        ]
    }
    concrete_store = {
        "cases": [{"test_id": "some_case", "requirement_id": "REQ-Y-NOT-X"}]
    }
    conflicts = concrete_binding_conflicts(metadata, concrete_store)
    assert len(conflicts) == 1
    assert conflicts[0]["declared_owner"] == "REQ-X"
    assert conflicts[0]["evidence_store_owner"] == "REQ-Y-NOT-X"


def test_positive_type1_symbolic_file_mismatch():
    """A requirement declaring an implementation in a different file than
    the one the crosshair manifest actually captured."""
    metadata = {
        "requirements": [
            {"id": "REQ-Z", "implementation": "other_file.py::some_fn"}
        ]
    }
    manifest = {"target": "dosage.py"}
    conflicts = symbolic_binding_conflicts(metadata, manifest)
    assert conflicts == [
        {
            "type": "identity_mismatch",
            "class": "symbolic_binding",
            "requirement_id": "REQ-Z",
            "declared_target_file": "other_file.py",
            "manifest_target_file": "dosage.py",
        }
    ]


def test_build_matrix_folds_in_type1_check():
    """Step 3 (2026-07-06): the fold-in itself, proven by driving the real
    entry point rather than the underlying check function directly. A
    conflict must be rejected before build_matrix() assembles a single
    record - this is what makes Type 1 run no matter how build_matrix()
    is invoked, not just inside the full generate_artifacts.py pipeline."""
    metadata = {
        "requirements": [
            {
                "id": "REQ-X",
                "evidence": [{"method": "concrete_test", "test_id": "some_case"}],
            }
        ]
    }
    concrete_store = {"cases": [{"test_id": "some_case", "requirement_id": "REQ-Y-NOT-X"}]}
    manifest = {"target": "irrelevant.py"}
    with pytest.raises(AssertionError, match="Type 1, identity mismatch"):
        build_matrix("a", metadata, manifest, concrete_store)


def test_missing_declared_test_id_is_a_hard_error_not_a_silent_pass():
    """A declared test_id that doesn't exist in the evidence store at all
    is a different failure mode than a conflict (there's no second claim
    to disagree with) - it must not be silently treated as clean."""
    metadata = {
        "requirements": [
            {"id": "REQ-X", "evidence": [{"method": "concrete_test", "test_id": "missing"}]}
        ]
    }
    with pytest.raises(SystemExit, match="not found in concrete_store"):
        concrete_binding_conflicts(metadata, {"cases": []})


# ---------------------------------------------------------- Type 2 (outcome)

def test_type2_gate_passes_on_committed_manifests():
    """All four committed manifests target distinct files, so none share
    an identity and there is nothing to disagree about - a real, honest
    zero, not an untested check."""
    manifests = {
        name: _load(name)
        for name in (
            "run_manifest.json",
            "run_manifest_broken.json",
            "run_manifest_naive_widening.json",
            "run_manifest_overflow_probe.json",
        )
    }
    result = run_outcome_gate(manifests)
    assert result["conflicts"] == 0
    assert result["manifests_checked"] == 4
    assert result["distinct_identities"] == 4  # no two share an identity


def test_positive_type2_outcome_mismatch():
    """The ratified positive Type 2 case: two manifests agree on tool,
    target, and enforced timeout (the same verification act) but report
    different exit codes - a real conflict, not covered by Type 1."""
    manifests = {
        "run_a": {
            "tool": "crosshair",
            "target": "dosage.py",
            "exit_code": 0,
            "effective_bounds": {"per_condition_timeout_s": 30},
        },
        "run_b_recapture": {
            "tool": "crosshair",
            "target": "dosage.py",
            "exit_code": 1,
            "effective_bounds": {"per_condition_timeout_s": 30},
        },
    }
    conflicts = outcome_conflicts(manifests)
    assert len(conflicts) == 1
    assert conflicts[0]["type"] == "outcome_mismatch"
    assert conflicts[0]["outcomes"] == {"run_a": 0, "run_b_recapture": 1}
    with pytest.raises(AssertionError, match="Type 2, outcome mismatch"):
        run_outcome_gate(manifests)


def test_type2_different_targets_are_not_compared():
    """Two manifests for genuinely different targets are not a conflict
    even if their outcomes differ - Type 2 only compares claims about the
    SAME verification act."""
    manifests = {
        "clean": {
            "tool": "crosshair",
            "target": "dosage.py",
            "exit_code": 0,
            "effective_bounds": {"per_condition_timeout_s": 30},
        },
        "broken": {
            "tool": "crosshair",
            "target": "dosage_broken.py",
            "exit_code": 1,
            "effective_bounds": {"per_condition_timeout_s": 30},
        },
    }
    assert outcome_conflicts(manifests) == []
