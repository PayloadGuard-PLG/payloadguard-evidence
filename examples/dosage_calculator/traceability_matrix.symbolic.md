# IEC 62304 Traceability Matrix (variant C: symbolic evidence)

Generated (UTC): 2026-07-16T04:25:26.821408+00:00
Tool versions: {'crosshair': 'crosshair-tool 0.0.107'}
Declared bounds (intended envelope): {'per_condition_timeout_s': 30, 'max_iterations': 100000, 'seed': 1}
Effective bounds (demonstrated by capture): {'per_condition_timeout_s': 30}
Enforcement note: max_iterations and seed are declared-only in metadata; crosshair-tool 0.0.107 has no CLI flags to enforce them.

| Requirement | Method | Strength | Result | Detail | Notes |
|---|---|---|---|---|---|
| REQ-GIP-1-4-12 | crosshair | BOUNDED_CHECKED | no_counterexample | bounds: {'per_condition_timeout_s': 30, 'max_iterations': 100000, 'seed': 1} | — |
| REQ-GIP-1-8-1 | crosshair | BOUNDED_CHECKED | no_counterexample | bounds: {'per_condition_timeout_s': 30, 'max_iterations': 100000, 'seed': 1} | — |
| REQ-DOSE-003 | crosshair | BOUNDED_CHECKED | no_counterexample | bounds: {'per_condition_timeout_s': 30, 'max_iterations': 100000, 'seed': 1} | — |
| REQ-GIP-1-4-12 [system_scope] | — | GAP | — | deferred scope `system_scope` — no evidence at this phase | system_scope declared but not evidenced at this phase; deferred to integration testing (explicit GAP, not omission) |

## Caveats

- **BOUNDED_CHECKED**: No counterexample found within the recorded bounds; this is a bounded search, not a proof.
- **GAP**: Not established. Human input required.

## Notes

- REQ-GIP-1-4-12: system_scope declared but not evidenced at this phase; deferred to integration testing (explicit GAP, not omission)
