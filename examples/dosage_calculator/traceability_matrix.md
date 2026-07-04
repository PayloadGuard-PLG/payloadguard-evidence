# IEC 62304 Traceability Matrix

Generated (UTC): 2026-07-04T15:33:32.526979+00:00
Tool versions: {'crosshair': 'crosshair-tool 0.0.107'}
CrossHair bounds: {'per_condition_timeout_s': 30, 'max_iterations': 100000, 'seed': 1}

| Requirement | Code | Method | Strength | Result | Notes |
|---|---|---|---|---|---|
| REQ-GIP-1-4-12 | dosage.py::calculate_hourly_dose | crosshair | BOUNDED_CHECKED | no_counterexample | intended PROVEN, realized BOUNDED_CHECKED |
| REQ-GIP-1-8-1 | dosage.py::calculate_hourly_dose | crosshair | BOUNDED_CHECKED | no_counterexample | intended PROVEN, realized BOUNDED_CHECKED |
| REQ-DOSE-003 | dosage.py::calculate_hourly_dose | crosshair | BOUNDED_CHECKED | no_counterexample | — |

## Caveats

- **BOUNDED_CHECKED**: No counterexample found within the recorded bounds; this is a bounded search, not a proof.
  - Bounds: {'per_condition_timeout_s': 30, 'max_iterations': 100000, 'seed': 1}

## Notes

- REQ-GIP-1-4-12: intended PROVEN, realized BOUNDED_CHECKED
- REQ-GIP-1-8-1: intended PROVEN, realized BOUNDED_CHECKED
