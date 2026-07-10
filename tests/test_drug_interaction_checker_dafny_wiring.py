"""Phase E, Gate C2: confirming the PROVEN-exclusivity binder
(evidence.render.matrix_variants.dafny_record + assert_no_realized_proven,
ruling R3) generalizes to drug_interaction_checker's real capture -- the
first time since dosage_calculator (2026-07-07) this mechanism has been
exercised against an independently-authored spec's real, committed
output. renal_adjustment never reached this point: its captures were
never wired into a metadata.yaml/traceability matrix at all, so
dafny_record() was never called against them.

Deliberately narrower scope than test_dafny_wiring.py: this example has
no metadata.yaml or committed traceability matrix yet (Phase 2, not
Phase 3 -- evidence packaging hasn't started), so there's no full
build_matrix()/CLI/fact-equality pipeline to test against, only the
binder itself. That's a real, honest scope boundary, not an oversight --
matches every other Gate C* test file's discipline of testing only what
actually exists for this example at this phase.
"""

import json
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.render.matrix_variants import (  # noqa: E402
    assert_no_realized_proven,
    dafny_record,
)

ART_DIR = REPO_ROOT / "examples" / "drug_interaction_checker"


def _real_capture():
    return {
        "spec_source": (ART_DIR / "drug_interaction_checker.dfy").read_text(),
        "raw_output": (ART_DIR / "raw_dafny_output_ddi.txt").read_text(),
        "manifest": json.loads((ART_DIR / "run_manifest_dafny_ddi.json").read_text()),
        "dafny_method": "CheckInteraction",
    }


def test_dafny_record_produces_a_real_proven_record():
    """dafny_record() against the real, committed capture -- not a
    synthetic fixture -- exercises both gates it's documented to run:
    Gate C3 vector 1 (Z3 precondition satisfiability, now able to model
    CheckInteraction's datatype comparisons per the Gate C3 extension)
    and Gate C1 (parse_dafny_capture's false-zero guard). Both pass for
    real against this spec's actual output."""
    record = dafny_record(_real_capture(), "drug_interaction_checker.dfy::CheckInteraction")
    assert record["method"] == "dafny"
    assert record["strength"] == "PROVEN"
    assert record["verifier_completion_status"] == "completed"


def test_real_record_passes_r3_cleanly():
    """The real record, wrapped in a minimal matrix, must pass
    assert_no_realized_proven without complaint -- confirms R3 doesn't
    reject dafny_record()'s own honest output for this example."""
    record = dafny_record(_real_capture(), "drug_interaction_checker.dfy::CheckInteraction")
    matrix = {"rows": [{"requirement_id": "REQ-DDI-2", "evidence": [record]}]}
    assert_no_realized_proven(matrix)  # must not raise


def test_r3_still_refuses_wrong_method_for_this_records_shape():
    """R3 does not trust dafny_record()'s own diligence (per that
    function's docstring) -- it must independently refuse a
    hand-tampered copy of this real record claiming a non-dafny method,
    confirmed against this example's actual record shape, not just a
    synthetic fixture."""
    record = dafny_record(_real_capture(), "drug_interaction_checker.dfy::CheckInteraction")
    tampered = dict(record, method="crosshair")
    matrix = {"rows": [{"requirement_id": "REQ-DDI-2", "evidence": [tampered]}]}
    with pytest.raises(AssertionError, match="not dafny"):
        assert_no_realized_proven(matrix)


def test_r3_still_refuses_incomplete_verifier_status_for_this_records_shape():
    """Same independent-refusal confirmation for the second half of R3's
    check -- a dafny-method record without verifier_completion_status ==
    'completed' must still be refused, even though it otherwise matches
    this example's real, honest record shape exactly."""
    record = dafny_record(_real_capture(), "drug_interaction_checker.dfy::CheckInteraction")
    tampered = dict(record, verifier_completion_status="incomplete")
    matrix = {"rows": [{"requirement_id": "REQ-DDI-2", "evidence": [tampered]}]}
    with pytest.raises(AssertionError, match="completed"):
        assert_no_realized_proven(matrix)
