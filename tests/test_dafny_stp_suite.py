"""Phase C, Gate C4: Spec-Testing Proofs (IronSpec methodology).

These tests check the real, committed Dafny captures directly (raw
output + manifest), the same way tests/test_dafny_adapter.py does for
Gate C1 - they do NOT go through evidence.dafny_adapter.parse_dafny_capture,
because an STP suite's capture isn't itself a requirement's verification
evidence (it's a proof ABOUT the spec's tightness, a meta-level check),
so it isn't a candidate for a VerificationResult/PROVEN strength at all -
matching Gate C1/C2/C3's own precedent of standalone, non-wired
capabilities.
"""

import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

ART_DIR = REPO_ROOT / "examples" / "dosage_calculator"


def _capture(name):
    raw = (ART_DIR / f"raw_dafny_output_{name}.txt").read_text()
    manifest = json.loads((ART_DIR / f"run_manifest_dafny_{name}.json").read_text())
    return raw, manifest


def test_underconstrained_spec_still_verifies_cleanly_on_its_own():
    """The preserved original spec's bug is a WEAKNESS, not a
    verification failure - dosage_underconstrained.dfy must still pass
    Dafny's own check by itself. The gap only shows up under an STP."""
    raw, manifest = _capture("underconstrained")
    assert manifest["exit_code"] == 0
    assert "1 verified, 0 errors" in raw


def test_stp_suite_passes_against_the_fixed_spec():
    """All STP lemmas (3 ACCEPT + 2 REJECT + 1 ACCEPT for the
    reverse-flow case) verify cleanly against the fixed dosage.dfy,
    included via `include "dosage.dfy"`."""
    raw, manifest = _capture("stp_suite")
    assert manifest["exit_code"] == 0
    assert "0 errors" in raw
    assert "verified" in raw


def test_stp_suite_fails_against_the_preserved_weak_spec():
    """The mechanized 'before' proof: the same two REJECT lemmas, run
    against the preserved original weak spec instead of the fix, FAIL to
    verify - real, negative capture, not smoothed over. This is the
    concrete evidence that Gate C4's methodology caught a real gap, not
    a synthetic one."""
    raw, manifest = _capture("stp_suite_against_underconstrained")
    assert manifest["exit_code"] != 0
    assert "2 errors" in raw
    assert "postcondition could not be proved" in raw


def test_reject_lemmas_target_in_bounds_wrong_values_not_out_of_bounds_ones():
    """Regression on a mistake caught during this build: an early draft
    used 500.0 (the raw unclamped product) as the 'wrong' ceiling-clamped
    value, but 500.0 already violates the weak spec's own 0<=dose<=max
    bound directly - so excluding it doesn't test the actual gap. The
    committed suites use 50.0 instead (in-bounds, still wrong), which
    correctly stays a real gap. Guard against silently reintroducing the
    weaker test."""
    stp_suite = (ART_DIR / "dosage_stp_suite.dfy").read_text()
    against_weak = (ART_DIR / "dosage_stp_suite_against_underconstrained.dfy").read_text()
    for text in (stp_suite, against_weak):
        assert "dose == 50.0" in text
        assert "dose == 500.0" not in text


def test_fixed_spec_pins_the_dose_value_no_longer_just_bounds_it():
    """The actual fix, checked directly against the real dosage.dfy
    source: the pinning ensures clause referencing ExpectedDose must be
    present, not just the original two bounding clauses."""
    source = (ART_DIR / "dosage.dfy").read_text()
    assert "function ExpectedDose(" in source
    assert "ensures dose == ExpectedDose(" in source


def test_preserved_underconstrained_spec_lacks_the_pinning_clause():
    """The honesty exhibit must be a byte-for-byte preservation of the
    gap, not a partially-fixed copy - it must not declare an
    ExpectedDose function or reference one in an ensures clause (the
    header comment's prose discussion of the fix, in English, doesn't
    count)."""
    source = (ART_DIR / "dosage_underconstrained.dfy").read_text()
    assert "function ExpectedDose(" not in source
    assert "ensures dose == ExpectedDose(" not in source
