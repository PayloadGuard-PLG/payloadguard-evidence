"""Phase C, Gate C2: ruling R3 — PROVEN's exclusivity migration.

R2 (Phase A/B) hard-failed on ANY record anywhere claiming PROVEN, full
stop. R3 (this gate) earns the right to lift that ONLY for Dafny-sourced,
completed records; CrossHair and concrete_test records must remain
PERMANENTLY excluded from PROVEN, checked explicitly here rather than
relying on the fact that no binder happens to produce one today. Two
cases per the roadmap's requirement: a positive (real Dafny PROVEN
accepted) and explicit negatives (CrossHair/concrete_test can never carry
PROVEN, and a Dafny-shaped record without a completed run is still
refused) - not just proven by omission.
"""

import json
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.dafny_adapter import parse_dafny_capture  # noqa: E402
from evidence.render.matrix_variants import assert_no_realized_proven  # noqa: E402

ART_DIR = REPO_ROOT / "examples" / "dosage_calculator"


def _fake_matrix(rec):
    return {"rows": [{"requirement_id": "REQ-FIXTURE", "evidence": [rec]}]}


def test_positive_real_dafny_proven_record_is_accepted():
    """A real, fully-checked Dafny PROVEN record — produced the same way
    Gate C1's adapter produces it, not hand-waved — passes R3."""
    raw = (ART_DIR / "raw_dafny_output.txt").read_text()
    manifest = json.loads((ART_DIR / "run_manifest_dafny.json").read_text())
    result = parse_dafny_capture(raw, manifest)

    rec = {
        "method": result.method,
        "strength": result.strength.value,
        "verifier_completion_status": result.verifier_completion_status,
    }
    assert_no_realized_proven(_fake_matrix(rec))  # must not raise


def test_negative_crosshair_record_can_never_carry_proven():
    """Checked explicitly, not by omission: a crosshair-method record
    claiming PROVEN is refused even though it carries a completed status,
    and even though the fixture is otherwise well-formed."""
    rec = {
        "method": "crosshair",
        "strength": "PROVEN",
        "verifier_completion_status": "completed",
    }
    with pytest.raises(AssertionError, match="realized strength PROVEN"):
        assert_no_realized_proven(_fake_matrix(rec))


def test_negative_concrete_test_record_can_never_carry_proven():
    """Same property, other permanently-excluded method."""
    rec = {
        "method": "concrete_test",
        "strength": "PROVEN",
        "verifier_completion_status": "completed",
    }
    with pytest.raises(AssertionError, match="realized strength PROVEN"):
        assert_no_realized_proven(_fake_matrix(rec))


def test_negative_missing_method_can_never_carry_proven():
    """A record with no method at all (e.g. a scope-GAP row) must not
    slip through by having no method to check against."""
    rec = {"strength": "PROVEN", "verifier_completion_status": "completed"}
    with pytest.raises(AssertionError, match="realized strength PROVEN"):
        assert_no_realized_proven(_fake_matrix(rec))


def test_negative_dafny_method_without_completed_status_is_still_refused():
    """Defense in depth: even a record naming method="dafny" is refused if
    it doesn't also carry a completed verifier_completion_status - R3 does
    not trust the method label alone. Covers a hand-assembled or corrupted
    record that never actually went through parse_dafny_capture's checks."""
    rec = {"method": "dafny", "strength": "PROVEN", "verifier_completion_status": None}
    with pytest.raises(AssertionError, match="realized strength PROVEN"):
        assert_no_realized_proven(_fake_matrix(rec))


def test_negative_dafny_method_with_incomplete_status_is_still_refused():
    rec = {"method": "dafny", "strength": "PROVEN", "verifier_completion_status": "incomplete"}
    with pytest.raises(AssertionError, match="realized strength PROVEN"):
        assert_no_realized_proven(_fake_matrix(rec))


def test_row_level_strength_cell_honors_the_same_rule():
    """Variant B/C rows carry strength/method directly on the row, not
    inside an evidence list - the same R3 gate must cover that shape too."""
    matrix = {
        "rows": [
            {
                "requirement_id": "REQ-FIXTURE",
                "method": "crosshair",
                "strength": "PROVEN",
                "verifier_completion_status": "completed",
            }
        ]
    }
    with pytest.raises(AssertionError, match="realized strength PROVEN"):
        assert_no_realized_proven(matrix)


def test_committed_matrix_artifacts_still_pass_unchanged():
    """R3 must not regress the existing, fully-CrossHair/concrete-sourced
    committed artifacts - none of them contain a dafny record today, so
    they must pass exactly as they did under R2."""
    for name in (
        "traceability_matrix.a.json",
        "traceability_matrix.b.json",
        "traceability_matrix.symbolic.json",
        "traceability_matrix.concrete.json",
    ):
        matrix = json.loads((ART_DIR / name).read_text())
        assert_no_realized_proven(matrix)  # must not raise
