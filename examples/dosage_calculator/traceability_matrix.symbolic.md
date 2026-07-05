# IEC 62304 Traceability Matrix (variant C: symbolic evidence)

Generated (UTC): 2026-07-05T11:58:03.025604+00:00
Tool versions: {'crosshair': 'crosshair-tool 0.0.107'}
Declared bounds (intended envelope): {'per_condition_timeout_s': 30, 'max_iterations': 100000, 'seed': 1}
Effective bounds (demonstrated by capture): {'per_condition_timeout_s': 30}
Enforcement note: max_iterations and seed are declared-only in metadata; crosshair-tool 0.0.107 has no CLI flags to enforce them.

| Requirement | Method | Strength | Result | Detail | Notes |
|---|---|---|---|---|---|
| REQ-GIP-1-4-12 | crosshair | BOUNDED_CHECKED | no_counterexample | bounds: {'per_condition_timeout_s': 30, 'max_iterations': 100000, 'seed': 1} | intended PROVEN, realized BOUNDED_CHECKED, EXAMPLE_CHECKED |
| REQ-GIP-1-8-1 | crosshair | BOUNDED_CHECKED | no_counterexample | bounds: {'per_condition_timeout_s': 30, 'max_iterations': 100000, 'seed': 1} | intended PROVEN, realized BOUNDED_CHECKED, EXAMPLE_CHECKED |
| REQ-DOSE-003 | crosshair | BOUNDED_CHECKED | no_counterexample | bounds: {'per_condition_timeout_s': 30, 'max_iterations': 100000, 'seed': 1} | — |

## Caveats

- **BOUNDED_CHECKED**: No counterexample found within the recorded bounds; this is a bounded search, not a proof.

## Notes

- REQ-GIP-1-4-12: intended PROVEN, realized BOUNDED_CHECKED, EXAMPLE_CHECKED
- REQ-GIP-1-8-1: intended PROVEN, realized BOUNDED_CHECKED, EXAMPLE_CHECKED
