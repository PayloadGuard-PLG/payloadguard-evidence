"""R5 differential-testing harness (RISK_MANAGEMENT_FINDINGS.md):
regression coverage for the generated Dafny driver and the captured
comparison results.

This suite never invokes a live `dafny` binary itself - this repo's CI
has no Dafny/Z3 toolchain installed (see .github/workflows/tests.yml's
own comment on that), matching every other Dafny-capture test here
(tests/test_dafny_wiring.py etc.). `differential_test_results.json` and
`dosage_differential_driver.dfy` are captured/generated once, by hand,
against the real installed toolchain (run_verify_dosage_differential.py,
generate_dosage_differential_driver.py) and committed - this suite
checks the committed artifacts are internally consistent and that
Python's live behavior still matches what was captured, not that Dafny
itself still agrees (that would require re-running Dafny, which CI
can't do).
"""

import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ART_DIR = REPO_ROOT / "examples" / "dosage_calculator"
sys.path.insert(0, str(ART_DIR))
sys.path.insert(0, str(REPO_ROOT))

import pytest

from dosage import calculate_hourly_dose  # noqa: E402
from dosage_differential_vectors import VECTORS  # noqa: E402
from generate_dosage_differential_driver import (  # noqa: E402
    _dafny_real_literal,
    render,
)


def _load_results():
    return json.loads((ART_DIR / "differential_test_results.json").read_text())


def test_committed_driver_matches_the_generator():
    """The generated-artifact-matches-its-generator check, same
    discipline as evidence/cli.py's and evidence/test_catalog.py's own
    tests. If this fails, dosage_differential_vectors.py changed
    without regenerating dosage_differential_driver.dfy."""
    expected = render(VECTORS)
    actual = (ART_DIR / "dosage_differential_driver.dfy").read_text()
    assert actual == expected, (
        "dosage_differential_driver.dfy is out of date. Regenerate with:\n"
        "  python generate_dosage_differential_driver.py"
    )


def test_captured_results_show_every_vector_matched():
    """The regression test proper: the last real `dafny run` capture
    agreed with dosage.py on every vector. If this fails, someone
    edited differential_test_results.json by hand instead of
    re-running run_verify_dosage_differential.py against the real
    toolchain."""
    data = _load_results()
    assert data["all_matched"] is True
    unmatched = [r["id"] for r in data["results"] if not r["matched"]]
    assert unmatched == [], f"Vectors that disagreed in the last capture: {unmatched}"


def test_captured_results_cover_every_current_vector():
    """Sanity check that the capture wasn't taken against a stale
    vector list - every vector in dosage_differential_vectors.py right
    now has a corresponding captured result, and vice versa."""
    data = _load_results()
    captured_ids = {r["id"] for r in data["results"]}
    current_ids = {v["id"] for v in VECTORS}
    assert captured_ids == current_ids, (
        "differential_test_results.json's vector IDs don't match "
        "dosage_differential_vectors.py - re-run "
        "run_verify_dosage_differential.py"
    )


def test_python_side_reproduces_the_captured_values_live():
    """Re-runs dosage.py's real calculate_hourly_dose (no Dafny needed)
    against every vector and confirms it still produces the dose the
    last capture recorded - catches a Python-side regression between
    captures without requiring a live Dafny re-run in CI."""
    data = _load_results()
    for record in data["results"]:
        vector = next(v for v in VECTORS if v["id"] == record["id"])
        live_dose = calculate_hourly_dose(
            weight_kg=70.0,
            concentration_mg_per_ml=vector["concentration_mg_per_ml"],
            infusion_rate_ml_per_hr=vector["infusion_rate_ml_per_hr"],
            max_safe_dose_mg_per_hr=vector["max_safe_dose_mg_per_hr"],
        )
        assert live_dose == record["python_dose"], (
            f"vector {record['id']!r}: live dosage.py returned {live_dose}, "
            f"captured result recorded {record['python_dose']} - "
            "re-run run_verify_dosage_differential.py"
        )


def test_real_literal_rejects_fractional_scientific_notation():
    """Qodo review finding on PR #55: _dafny_real_literal's scientific-
    notation branch used to convert through int(value) unconditionally,
    which is lossless for the two committed vectors (1e10, 1e308 - both
    already integer-valued) but silently truncates a fractional
    scientific-notation value to 0.0 (confirmed: int(1e-5) == 0). Must
    now refuse rather than guess, matching this repo's own false-zero-
    guard discipline."""
    with pytest.raises(ValueError, match="fractional"):
        _dafny_real_literal(1e-5)


def test_real_literal_still_handles_committed_large_integer_vectors():
    """The two real scientific-notation-repr'd values this file's
    vectors actually use (1e10, 1e308) stay lossless through the
    hardened path - both are exactly integer-valued floats, so int()
    on them is exact regardless of magnitude."""
    assert _dafny_real_literal(1e10) == "10000000000.0"
    assert _dafny_real_literal(1e308) == f"{int(1e308)}.0"


def test_overflow_vector_is_explicitly_documented_as_coincidental():
    """This harness's one real scoping caveat, checked mechanically so
    it can't silently disappear on a future edit: the overflow-domain
    vector's own note must state plainly that its agreement is
    coincidental to the chosen magnitudes, not a REQ-DOSE-003
    equivalence claim - Dafny cannot represent overflow at all, per
    dosage.dfy's own header comment."""
    vector = next(v for v in VECTORS if v["id"] == "overflow_negative_mirrors_test_dosage_concrete")
    assert "different reasoning" in vector["note"] or "coincidental" in vector["note"].lower()
