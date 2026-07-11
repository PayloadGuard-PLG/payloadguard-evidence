# IEC 62304 Traceability Matrix (variant C: formally proven evidence)

Generated (UTC): 2026-07-11T18:39:46.902160+00:00
Tool versions: {'crosshair': 'crosshair-tool 0.0.107', 'dafny': '4.11.0+fcb2042d6d043a2634f0854338c08feeaaaf4ae2'}
Declared bounds (intended envelope): {'per_condition_timeout_s': 30, 'max_iterations': 100000, 'seed': 1}
Effective bounds (demonstrated by capture): {'per_condition_timeout_s': 30}
Enforcement note: max_iterations and seed are declared-only in metadata; crosshair-tool 0.0.107 has no CLI flags to enforce them.

| Requirement | Method | Strength | Result | Detail | Notes |
|---|---|---|---|---|---|
| REQ-GIP-1-4-12 | dafny | PROVEN | proven | verifier_completion_status: completed | — |
| REQ-GIP-1-8-1 | dafny | PROVEN | proven | verifier_completion_status: completed | — |
| REQ-GIP-1-4-12 [system_scope] | — | GAP | — | deferred scope `system_scope` — no evidence at this phase | system_scope declared but not evidenced at this phase; deferred to integration testing (explicit GAP, not omission) |

## Caveats

- **PROVEN**: Formally proven against the stated specification.
- **GAP**: Not established. Human input required.

## Notes

- REQ-GIP-1-4-12: system_scope declared but not evidenced at this phase; deferred to integration testing (explicit GAP, not omission)
