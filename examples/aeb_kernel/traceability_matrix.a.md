# IEC 62304 Traceability Matrix (variant A: evidence array per requirement)

Generated (UTC): 2026-07-20T14:22:54.843415+00:00
Tool versions: {'dafny': '4.11.0+fcb2042d6d043a2634f0854338c08feeaaaf4ae2'}
Declared bounds (intended envelope): N/A (no crosshair evidence in this metadata)
Effective bounds (demonstrated by capture): N/A (no crosshair evidence in this metadata)
Enforcement note: 

| Requirement | Method | Strength | Result | Detail | Notes |
|---|---|---|---|---|---|
| **REQ-AEB-1** | dafny | PROVEN | proven | verifier_completion_status: completed | — |
| **REQ-AEB-2** | dafny | PROVEN | proven | verifier_completion_status: completed | — |
| **REQ-AEB-3** | dafny | PROVEN | proven | verifier_completion_status: completed | — |
| **REQ-AEB-4** | dafny | PROVEN | proven | verifier_completion_status: completed | — |
| **REQ-AEB-5** | dafny | PROVEN | proven | verifier_completion_status: completed | — |
| **REQ-AEB-6** | dafny | PROVEN | proven | verifier_completion_status: completed | — |
| **REQ-AEB-7** | dafny | PROVEN | proven | verifier_completion_status: completed | — |
| **REQ-AEB-8** | dafny | PROVEN | proven | verifier_completion_status: completed | — |
| **REQ-AEB-9** | — | GAP | — | deferred scope `system_scope` — no evidence at this phase | no evidence bound for this requirement; intended DECLARED, realized GAP; system_scope declared but not evidenced at this phase; deferred to integration testing (explicit GAP, not omission) |
| **REQ-AEB-10** | — | GAP | — | deferred scope `system_scope` — no evidence at this phase | no evidence bound for this requirement; intended DECLARED, realized GAP; system_scope declared but not evidenced at this phase; deferred to integration testing (explicit GAP, not omission) |

## Caveats

- **PROVEN**: Formally proven against the stated specification.
- **GAP**: Not established. Human input required.
- **PROVEN / definitional**: Definitional proof: the postcondition restates the implementation (ensures is equivalent to the body), so the proof obligation is a tautology discharged by reflexivity. Certified: totality, type-safety, match-exhaustiveness, and the literal boundary structure of the definition. NOT certified: an independent property beyond the definition, or fidelity to the source requirement.

## Notes

- REQ-AEB-9: no evidence bound for this requirement
- REQ-AEB-9: intended DECLARED, realized GAP
- REQ-AEB-9: system_scope declared but not evidenced at this phase; deferred to integration testing (explicit GAP, not omission)
- REQ-AEB-10: no evidence bound for this requirement
- REQ-AEB-10: intended DECLARED, realized GAP
- REQ-AEB-10: system_scope declared but not evidenced at this phase; deferred to integration testing (explicit GAP, not omission)
