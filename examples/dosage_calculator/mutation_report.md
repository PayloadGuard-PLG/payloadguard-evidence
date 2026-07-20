# Gate C5: mutation testing report — `dosage.dfy::CalculateHourlyDose`

Generated 2026-07-20T09:51:36.539163+00:00. 56 mutants total. Counts: filtered_ar_group_incompatible=1, filtered_chain_incompatible=4, filtered_magnitude_implied=4, filtered_static=6, killed=41

SOR: 0 mutants (no set-typed operations in this spec) — NOT APPLICABLE, checked.
HOR: 0 mutants (no heap/object state, old()/reads/modifies) — NOT APPLICABLE, checked.
AOR: 0 mutants against this spec's requires/ensures clauses (no arithmetic in any clause) + 3 against ExpectedDose's function body (its one `*` operator), restricted per MutDafny's own group rule (+/-/* freely interchange; never introduce `/`, eliminating the division-by-zero false-kill risk by construction).
LVR: every numeric literal in this spec is exactly `0.0` (7 sites: 5 clause-level, 2 in ExpectedDose's function body); each mutated to `+/- 0.01` (the clinical-precision floor). Clause-level LT/LE/GT/GE-adjacent literals are filtered per the requires/ensures magnitude-implication principle; EQ/NE-adjacent and all function-body literals are never filtered.

| Operator | Clause | Mutation | Outcome | Detail |
|---|---|---|---|---|
| ROR | `requires` | ROR on requires clause 'concentrationMgPerMl > 0.0': > -> <= | **killed** | 0 verified, 2 errors |
| ROR | `requires` | ROR on requires clause 'concentrationMgPerMl > 0.0': > -> >= | **killed** | 1 verified, 1 errors |
| ROR | `requires` | ROR on requires clause 'concentrationMgPerMl > 0.0': > -> == | **killed** | 1 verified, 1 errors |
| ROR | `requires` | ROR on requires clause 'concentrationMgPerMl > 0.0': > -> != | **killed** | 0 verified, 2 errors |
| ROR | `requires` | ROR on requires clause 'concentrationMgPerMl > 0.0': > -> < | **killed** | 0 verified, 2 errors |
| ROR | `requires` | ROR on requires clause 'maxSafeDoseMgPerHr > 0.0': > -> <= | **killed** | 0 verified, 3 errors |
| ROR | `requires` | ROR on requires clause 'maxSafeDoseMgPerHr > 0.0': > -> >= | **killed** | 1 verified, 1 errors |
| ROR | `requires` | ROR on requires clause 'maxSafeDoseMgPerHr > 0.0': > -> == | **killed** | 1 verified, 1 errors |
| ROR | `requires` | ROR on requires clause 'maxSafeDoseMgPerHr > 0.0': > -> != | **killed** | 0 verified, 3 errors |
| ROR | `requires` | ROR on requires clause 'maxSafeDoseMgPerHr > 0.0': > -> < | **killed** | 0 verified, 3 errors |
| ROR | `ensures` | ROR on ensures clause 'dose == ExpectedDose(concentrationMgPerMl, infusionRateMlPerHr, maxSafeDoseMgPerHr)': == -> <= | **filtered_static** | statically weaker (ensures) |
| ROR | `ensures` | ROR on ensures clause 'dose == ExpectedDose(concentrationMgPerMl, infusionRateMlPerHr, maxSafeDoseMgPerHr)': == -> >= | **filtered_static** | statically weaker (ensures) |
| ROR | `ensures` | ROR on ensures clause 'dose == ExpectedDose(concentrationMgPerMl, infusionRateMlPerHr, maxSafeDoseMgPerHr)': == -> != | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause 'dose == ExpectedDose(concentrationMgPerMl, infusionRateMlPerHr, maxSafeDoseMgPerHr)': == -> < | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause 'dose == ExpectedDose(concentrationMgPerMl, infusionRateMlPerHr, maxSafeDoseMgPerHr)': == -> > | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> >= | **filtered_chain_incompatible** | chain-direction incompatible with a sibling comparison in the same chain - would be a Dafny parse error, not a semantic test (Dafny Reference Manual Sec 5.2.1-5.2.2) |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> == | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> != | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> < | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> > | **filtered_chain_incompatible** | chain-direction incompatible with a sibling comparison in the same chain - would be a Dafny parse error, not a semantic test (Dafny Reference Manual Sec 5.2.1-5.2.2) |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> >= | **filtered_chain_incompatible** | chain-direction incompatible with a sibling comparison in the same chain - would be a Dafny parse error, not a semantic test (Dafny Reference Manual Sec 5.2.1-5.2.2) |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> == | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> != | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> < | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> > | **filtered_chain_incompatible** | chain-direction incompatible with a sibling comparison in the same chain - would be a Dafny parse error, not a semantic test (Dafny Reference Manual Sec 5.2.1-5.2.2) |
| ROR | `ensures` | ROR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': > -> <= | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': > -> >= | **filtered_static** | statically weaker (ensures) |
| ROR | `ensures` | ROR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': > -> == | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': > -> != | **filtered_static** | statically weaker (ensures) |
| ROR | `ensures` | ROR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': > -> < | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': == -> <= | **filtered_static** | statically weaker (ensures) |
| ROR | `ensures` | ROR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': == -> >= | **filtered_static** | statically weaker (ensures) |
| ROR | `ensures` | ROR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': == -> != | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': == -> < | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': == -> > | **killed** | 1 verified, 1 errors |
| LOR | `ensures` | LOR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': || -> && | **killed** | 1 verified, 2 errors |
| AOR | `function_body` | AOR on ExpectedDose's function body: * -> + | **killed** | 1 verified, 1 errors |
| AOR | `function_body` | AOR on ExpectedDose's function body: * -> - | **killed** | 1 verified, 1 errors |
| AOR | `function_body` | AOR on ExpectedDose's function body: * -> / | **filtered_ar_group_incompatible** | arithmetic-operator group incompatible (MutDafny's own restriction: never introduce / from +/-/*, avoiding a division-by-zero false-kill by construction) |
| COI | `ensures` | COI: negate ensures clause 'dose == ExpectedDose(concentrationMgPerMl, infusionRateMlPerHr, maxSafeDoseMgPerHr)' | **killed** | 1 verified, 1 errors |
| COI | `ensures` | COI: negate ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr' | **killed** | 1 verified, 1 errors |
| COI | `ensures` | COI: negate ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0' | **killed** | 1 verified, 2 errors |
| LVR | `requires` | LVR on requires clause 'concentrationMgPerMl > 0.0': 0.0 -> -0.01 | **killed** | 0 verified, 2 errors |
| LVR | `requires` | LVR on requires clause 'concentrationMgPerMl > 0.0': 0.0 -> 0.01 | **filtered_magnitude_implied** | magnitude-implied (requires) |
| LVR | `requires` | LVR on requires clause 'maxSafeDoseMgPerHr > 0.0': 0.0 -> -0.01 | **killed** | 0 verified, 3 errors |
| LVR | `requires` | LVR on requires clause 'maxSafeDoseMgPerHr > 0.0': 0.0 -> 0.01 | **filtered_magnitude_implied** | magnitude-implied (requires) |
| LVR | `ensures` | LVR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': 0.0 -> -0.01 | **filtered_magnitude_implied** | magnitude-implied (ensures) |
| LVR | `ensures` | LVR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': 0.0 -> 0.01 | **killed** | 1 verified, 1 errors |
| LVR | `ensures` | LVR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': 0.0 -> -0.01 | **filtered_magnitude_implied** | magnitude-implied (ensures) |
| LVR | `ensures` | LVR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': 0.0 -> 0.01 | **killed** | 1 verified, 1 errors |
| LVR | `ensures` | LVR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': 0.0 -> -0.01 | **killed** | 1 verified, 1 errors |
| LVR | `ensures` | LVR on ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0': 0.0 -> 0.01 | **killed** | 1 verified, 1 errors |
| LVR | `function_body` | LVR on ExpectedDose's function body: 0.0 -> -0.01 | **killed** | 1 verified, 1 errors |
| LVR | `function_body` | LVR on ExpectedDose's function body: 0.0 -> 0.01 | **killed** | 1 verified, 1 errors |
| LVR | `function_body` | LVR on ExpectedDose's function body: 0.0 -> -0.01 | **killed** | 1 verified, 1 errors |
| LVR | `function_body` | LVR on ExpectedDose's function body: 0.0 -> 0.01 | **killed** | 1 verified, 1 errors |
