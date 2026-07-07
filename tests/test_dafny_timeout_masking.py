"""Phase C, Gate C3, vector 3: timeout/resource-limit masking hardening in
evidence/dafny_adapter.py. Covers the real committed "out of resource"
capture plus the synthetic cases needed to exercise the summary-line
hardening independent of the exit-code check (which already refuses every
real capture committed in this repo - see the module docstring in
evidence/dafny_adapter.py for why both checks matter anyway).
"""

import json
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.dafny_adapter import parse_dafny_capture  # noqa: E402

ART_DIR = REPO_ROOT / "examples" / "dosage_calculator"


def test_real_resource_limited_capture_is_refused():
    """Real, committed capture: the actual dosage.dfy spec run for real
    under `--resource-limit=1`. Confirmed exit_code=4, so this is caught
    by the exit-code check first - the refusal itself is what matters
    here, not which check fired."""
    raw = (ART_DIR / "raw_dafny_output_resource_limited.txt").read_text()
    manifest = json.loads((ART_DIR / "run_manifest_dafny_resource_limited.json").read_text())
    assert "out of resource" in raw
    assert manifest["exit_code"] != 0
    with pytest.raises(SystemExit, match="does not report a clean pass"):
        parse_dafny_capture(raw, manifest)


def test_out_of_resource_marker_refused_even_with_a_zero_exit_code():
    """Defense in depth: if exit_code were ever 0 alongside an 'out of
    resource' summary tail (not observed in this repo's real captures, but
    not something the parser should have to trust blindly either), the
    summary-line hardening must catch it on its own, independent of the
    exit-code check."""
    manifest = {"target": "whatever.dfy", "exit_code": 0, "started_utc": "x"}
    raw = "Dafny program verifier finished with 0 verified, 0 errors, 1 out of resource"
    with pytest.raises(SystemExit, match="incomplete verification"):
        parse_dafny_capture(raw, manifest)


def test_out_of_memory_marker_refused_even_with_a_zero_exit_code():
    manifest = {"target": "whatever.dfy", "exit_code": 0, "started_utc": "x"}
    raw = "Dafny program verifier finished with 2 verified, 0 errors, 1 out of memory"
    with pytest.raises(SystemExit, match="incomplete verification"):
        parse_dafny_capture(raw, manifest)


def test_timed_out_marker_refused_even_with_a_zero_exit_code():
    manifest = {"target": "whatever.dfy", "exit_code": 0, "started_utc": "x"}
    raw = "Dafny program verifier finished with 2 verified, 0 errors, 1 timed out"
    with pytest.raises(SystemExit, match="incomplete verification"):
        parse_dafny_capture(raw, manifest)


def test_ambiguous_multiple_summary_lines_are_refused():
    """A capture with more than one summary-line match must be refused
    outright rather than silently trusting whichever one regex finds
    first - Tier 1, don't guess which is authoritative."""
    manifest = {"target": "whatever.dfy", "exit_code": 0, "started_utc": "x"}
    raw = (
        "Dafny program verifier finished with 1 verified, 0 errors\n"
        "Dafny program verifier finished with 1 verified, 0 errors"
    )
    with pytest.raises(SystemExit, match="2 verifier"):
        parse_dafny_capture(raw, manifest)


def test_real_committed_clean_capture_still_accepted():
    """Regression: Gate C1's real clean capture (no incomplete-run marker,
    exactly one summary line) must still parse to PROVEN after the vector
    3 hardening - the new checks must not regress the happy path."""
    raw = (ART_DIR / "raw_dafny_output.txt").read_text()
    manifest = json.loads((ART_DIR / "run_manifest_dafny.json").read_text())
    result = parse_dafny_capture(raw, manifest)
    assert result.verifier_completion_status == "completed"
