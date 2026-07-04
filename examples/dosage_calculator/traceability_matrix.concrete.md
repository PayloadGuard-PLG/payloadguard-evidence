# IEC 62304 Traceability Matrix (variant C: concrete evidence)

Generated (UTC): 2026-07-04T16:39:24.434189+00:00
Tool versions: {'crosshair': 'crosshair-tool 0.0.107'}
CrossHair bounds: {'per_condition_timeout_s': 30, 'max_iterations': 100000, 'seed': 1}

| Requirement | Method | Strength | Result | Detail | Notes |
|---|---|---|---|---|---|
| REQ-GIP-1-4-12 | concrete_test | EXAMPLE_CHECKED | passed | test `over_max_clamps_exactly_to_max`; inputs {'weight_kg': 70.0, 'concentration_mg_per_ml': 2.0, 'infusion_rate_ml_per_hr': 500.0, 'max_safe_dose_mg_per_hr': 10.0}; expected 10.0; observed 10.0 | intended method per metadata not realized; realized: BOUNDED_CHECKED, EXAMPLE_CHECKED |
| REQ-GIP-1-8-1 | concrete_test | EXAMPLE_CHECKED | passed | test `ordinary_negative_rate_clamps_to_zero`; inputs {'weight_kg': 70.0, 'concentration_mg_per_ml': 2.0, 'infusion_rate_ml_per_hr': -5.0, 'max_safe_dose_mg_per_hr': 10.0}; expected 0.0; observed 0.0 | intended method per metadata not realized; realized: BOUNDED_CHECKED, EXAMPLE_CHECKED |
| REQ-GIP-1-8-1 | concrete_test | EXAMPLE_CHECKED | passed | test `overflow_negative_rate_clamps_to_zero`; inputs {'weight_kg': 70.0, 'concentration_mg_per_ml': 1e+308, 'infusion_rate_ml_per_hr': -2.0, 'max_safe_dose_mg_per_hr': 10.0}; expected 0.0; observed 0.0 | intended method per metadata not realized; realized: BOUNDED_CHECKED, EXAMPLE_CHECKED |
| REQ-DOSE-003 | concrete_test | EXAMPLE_CHECKED | passed | test `normal_in_range_exact_value`; inputs {'weight_kg': 70.0, 'concentration_mg_per_ml': 2.0, 'infusion_rate_ml_per_hr': 3.0, 'max_safe_dose_mg_per_hr': 10.0}; expected 6.0; observed 6.0 | — |

## Caveats

- **EXAMPLE_CHECKED**: Holds for the specific recorded inputs only; no claim of generality beyond them.

## Notes

- REQ-GIP-1-4-12: intended method per metadata not realized; realized: BOUNDED_CHECKED, EXAMPLE_CHECKED
- REQ-GIP-1-8-1: intended method per metadata not realized; realized: BOUNDED_CHECKED, EXAMPLE_CHECKED
- REQ-GIP-1-8-1: intended method per metadata not realized; realized: BOUNDED_CHECKED, EXAMPLE_CHECKED
