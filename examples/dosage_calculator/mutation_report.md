# Gate C5: mutation testing report — `dosage.dfy::CalculateHourlyDose`

Generated 2026-07-07T16:49:20.900659+00:00. 42 mutants total. Counts: filtered_ar_group_incompatible=1, filtered_chain_incompatible=4, filtered_static=6, killed=31

SOR: 0 mutants (no set-typed operations in this spec) — NOT APPLICABLE, checked.
HOR: 0 mutants (no heap/object state, old()/reads/modifies) — NOT APPLICABLE, checked.
AOR: 0 mutants against this spec's requires/ensures clauses (no arithmetic in any clause) + 3 against ExpectedDose's function body (its one `*` operator), restricted per MutDafny's own group rule (+/-/* freely interchange; never introduce `/`, eliminating the division-by-zero false-kill risk by construction).

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
