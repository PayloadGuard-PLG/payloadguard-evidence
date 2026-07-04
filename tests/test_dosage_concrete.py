"""Concrete evidence foundation (T4-0) against the FIXED kernel only.

CASES is the single source of truth for the concrete evidence records: the
pytest below parametrizes over it, and run_verify_concrete.py imports it to
produce concrete_results.json. Requirement IDs are taken from
examples/dosage_calculator/metadata.yaml:
  - reverse-flow cases -> REQ-GIP-1-8-1
  - finite in-range result for valid inputs -> REQ-DOSE-003
  - over-limit dose clamped to the configured maximum -> REQ-GIP-1-4-12
"""

import pytest

from dosage import calculate_hourly_dose

CASES = [
    {
        # requirement: REQ-GIP-1-8-1 (reverse delivery: negative rate -> zero dose)
        "test_id": "ordinary_negative_rate_clamps_to_zero",
        "requirement_id": "REQ-GIP-1-8-1",
        "function": "dosage.py::calculate_hourly_dose",
        "inputs": {
            "weight_kg": 70.0,
            "concentration_mg_per_ml": 2.0,
            "infusion_rate_ml_per_hr": -5.0,
            "max_safe_dose_mg_per_hr": 10.0,
        },
        "expected": 0.0,
    },
    {
        # requirement: REQ-GIP-1-8-1 (reverse delivery: -inf overflow path -> zero dose)
        "test_id": "overflow_negative_rate_clamps_to_zero",
        "requirement_id": "REQ-GIP-1-8-1",
        "function": "dosage.py::calculate_hourly_dose",
        "inputs": {
            "weight_kg": 70.0,
            "concentration_mg_per_ml": 1e308,
            "infusion_rate_ml_per_hr": -2.0,
            "max_safe_dose_mg_per_hr": 10.0,
        },
        "expected": 0.0,
    },
    {
        # requirement: REQ-DOSE-003 (finite, in-range result for valid inputs)
        "test_id": "normal_in_range_exact_value",
        "requirement_id": "REQ-DOSE-003",
        "function": "dosage.py::calculate_hourly_dose",
        "inputs": {
            "weight_kg": 70.0,
            "concentration_mg_per_ml": 2.0,
            "infusion_rate_ml_per_hr": 3.0,
            "max_safe_dose_mg_per_hr": 10.0,
        },
        "expected": 6.0,
    },
    {
        # requirement: REQ-GIP-1-4-12 (dose above limit clamps exactly to the maximum)
        "test_id": "over_max_clamps_exactly_to_max",
        "requirement_id": "REQ-GIP-1-4-12",
        "function": "dosage.py::calculate_hourly_dose",
        "inputs": {
            "weight_kg": 70.0,
            "concentration_mg_per_ml": 2.0,
            "infusion_rate_ml_per_hr": 500.0,
            "max_safe_dose_mg_per_hr": 10.0,
        },
        "expected": 10.0,
    },
]


@pytest.mark.parametrize("case", CASES, ids=[c["test_id"] for c in CASES])
def test_dosage_concrete(case):
    """Requirement: see case['requirement_id'] (mapping per metadata.yaml)."""
    observed = calculate_hourly_dose(**case["inputs"])
    assert observed == case["expected"]
