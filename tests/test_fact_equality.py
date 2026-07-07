"""Turn 2.0 B2: the fact-equality gate as a committed test. Variant
artifacts must be fact-identical under normalization (shape divergence is
design; fact divergence is a defect). Corruption cases copy artifacts to a
pytest tmp_path and mutate the copies — no corrupted fixture is committed.
"""

import json
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.reconcile import BASE_ARTIFACT, VARIANT_ARTIFACTS, run_gate  # noqa: E402

ART_DIR = REPO_ROOT / "examples" / "dosage_calculator"


def test_gate_passes_on_committed_artifacts():
    """9 facts, not 7 (2026-07-07, Gate 2/C2-C4 wiring extended to
    variants A/B): +1 real dafny fact each for REQ-GIP-1-4-12 and
    REQ-GIP-1-8-1. intent_ok is True for all three requirements now -
    the two formerly-intended-but-never-realized PROVEN requirements are
    finally realized, for the first time since Phase A."""
    result = run_gate(ART_DIR)
    assert result["facts"] == 9
    assert result["intent"] == {
        "REQ-GIP-1-4-12": True,
        "REQ-GIP-1-8-1": True,
        "REQ-DOSE-003": True,
    }


def _copy_artifacts(tmp_path):
    for name in list(VARIANT_ARTIFACTS) + [BASE_ARTIFACT]:
        (tmp_path / name).write_text((ART_DIR / name).read_text())


def test_gate_fails_on_fact_divergence(tmp_path):
    _copy_artifacts(tmp_path)
    mutated = json.loads((tmp_path / "traceability_matrix.b.json").read_text())
    mutated["rows"][3]["result_status"] = "passed_MUTATED"
    (tmp_path / "traceability_matrix.b.json").write_text(json.dumps(mutated))
    with pytest.raises(AssertionError, match="A/B/C fact sets differ"):
        run_gate(tmp_path)


def test_gate_fails_on_intent_divergence(tmp_path):
    _copy_artifacts(tmp_path)
    mutated = json.loads((tmp_path / "traceability_matrix.concrete.json").read_text())
    for row in mutated["rows"]:
        if row["requirement_id"] == "REQ-DOSE-003":
            row["intent_ok"] = False
    (tmp_path / "traceability_matrix.concrete.json").write_text(json.dumps(mutated))
    with pytest.raises(AssertionError, match="intent_ok differs"):
        run_gate(tmp_path)


def test_gate_fails_on_base_subset_divergence(tmp_path):
    _copy_artifacts(tmp_path)
    mutated = json.loads((tmp_path / BASE_ARTIFACT).read_text())
    mutated["rows"].pop()
    (tmp_path / BASE_ARTIFACT).write_text(json.dumps(mutated))
    with pytest.raises(AssertionError, match="base matrix diverges"):
        run_gate(tmp_path)
