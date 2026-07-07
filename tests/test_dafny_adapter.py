"""Phase C, Gate C1: Dafny capture parser tests.

Covers the real committed captures (clean + broken), the false-zero
guard's core property (a substring match on "0 errors" elsewhere in the
output must not fool the parser - only the verifier's own summary line's
parsed error count matters), and the structural boundary that this
adapter does NOT reopen assert_no_realized_proven - constructing a
VerificationResult with Strength.PROVEN in Python is not the same as it
ever reaching a rendered matrix row.
"""

import json
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.dafny_adapter import parse_dafny_capture  # noqa: E402
from evidence.model import Strength  # noqa: E402
from evidence.render.matrix_variants import assert_no_realized_proven  # noqa: E402

ART_DIR = REPO_ROOT / "examples" / "dosage_calculator"


def test_parses_real_committed_clean_capture():
    raw = (ART_DIR / "raw_dafny_output.txt").read_text()
    manifest = json.loads((ART_DIR / "run_manifest_dafny.json").read_text())
    result = parse_dafny_capture(raw, manifest)
    assert result.strength is Strength.PROVEN
    assert result.method == "dafny"
    assert result.code_location == "dosage.dfy"
    assert result.verifier_completion_status == "completed"
    assert result.raw_status == "1 verified, 0 errors"


def test_refuses_real_committed_broken_capture():
    """The real broken capture fails on exit code alone (Dafny exits 4
    on a postcondition failure, confirmed in KNOWN_LIMITATIONS.md Gate
    C1) - refused at the cheapest, most definitive check before the
    summary line is ever parsed."""
    raw = (ART_DIR / "raw_dafny_output_broken.txt").read_text()
    manifest = json.loads((ART_DIR / "run_manifest_dafny_broken.json").read_text())
    assert manifest["exit_code"] != 0
    with pytest.raises(SystemExit, match="does not report a clean pass"):
        parse_dafny_capture(raw, manifest)


def test_refuses_nonzero_exit_code_before_parsing_output():
    manifest = {"target": "whatever.dfy", "exit_code": 1, "started_utc": "x"}
    with pytest.raises(SystemExit, match="does not report a clean pass"):
        parse_dafny_capture("irrelevant", manifest)


def test_refuses_missing_summary_line():
    """A crash, a timeout, or a subcommand that never attempted
    verification (confirmed real: `dafny audit` prints exactly "Dafny
    program verifier did not attempt verification" on some inputs) must
    be refused, not silently treated as success just because exit_code
    happens to be 0."""
    manifest = {"target": "whatever.dfy", "exit_code": 0, "started_utc": "x"}
    raw = "Dafny auditor completed with 0 findings\n\nDafny program verifier did not attempt verification"
    with pytest.raises(SystemExit, match="no verifier summary line"):
        parse_dafny_capture(raw, manifest)


def test_false_zero_guard_is_not_fooled_by_a_substring_trap():
    """The core false-zero property: a literal "0 errors" substring
    appearing anywhere else in the output must not cause a false
    accept - only the verifier's own summary line's parsed count
    matters. Constructed so a blind `"0 errors" in raw_output` check
    would incorrectly pass this; the regex-based check must not."""
    manifest = {"target": "whatever.dfy", "exit_code": 0, "started_utc": "x"}
    raw = (
        "Note: historically this file had 0 errors before a regression.\n"
        "Dafny program verifier finished with 3 verified, 2 errors"
    )
    assert "0 errors" in raw  # confirms the trap is real, not accidental
    with pytest.raises(SystemExit, match="reports 2 error"):
        parse_dafny_capture(raw, manifest)


def test_producing_a_proven_result_does_not_reopen_the_matrix_gate():
    """Belt and suspenders: even after constructing a real PROVEN
    VerificationResult via this adapter, assert_no_realized_proven still
    hard-blocks PROVEN from ever appearing in a rendered matrix row -
    Gate C2 (not built) is what would have to change that, not this
    module."""
    raw = (ART_DIR / "raw_dafny_output.txt").read_text()
    manifest = json.loads((ART_DIR / "run_manifest_dafny.json").read_text())
    result = parse_dafny_capture(raw, manifest)
    assert result.strength is Strength.PROVEN

    fake_matrix = {
        "rows": [
            {
                "requirement_id": "REQ-FIXTURE",
                "strength": result.strength.value,
            }
        ]
    }
    with pytest.raises(AssertionError, match="structural PROVEN check failed"):
        assert_no_realized_proven(fake_matrix)
