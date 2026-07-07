# Gate C5: mutation testing report — `dosage.dfy::CalculateHourlyDose`

Generated 2026-07-07T16:24:16.480026+00:00. 39 mutants total. Counts: filtered_static=6, killed=29, unclassifiable=4

SOR: 0 mutants (no set-typed operations in this spec) — NOT APPLICABLE, checked.
HOR: 0 mutants (no heap/object state, old()/reads/modifies) — NOT APPLICABLE, checked.
AOR: 0 mutants against this spec's requires/ensures clauses — the one arithmetic operator lives in ExpectedDose's function body, out of this v1's clause-mutation scope (named, deferred — see evidence/dafny_mutate.py's module docstring).

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
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> >= | **unclassifiable** | <mutant>.dfy(79,22): Error: this operator chain cannot continue with an ascending operator |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> == | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> != | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> < | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> > | **unclassifiable** | <mutant>.dfy(79,21): Error: this operator chain cannot continue with an ascending operator |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> >= | **unclassifiable** | <mutant>.dfy(79,22): Error: this operator chain cannot continue with a descending operator |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> == | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> != | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> < | **killed** | 1 verified, 1 errors |
| ROR | `ensures` | ROR on ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr': <= -> > | **unclassifiable** | <mutant>.dfy(79,22): Error: this operator chain cannot continue with a descending operator |
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
| COI | `ensures` | COI: negate ensures clause 'dose == ExpectedDose(concentrationMgPerMl, infusionRateMlPerHr, maxSafeDoseMgPerHr)' | **killed** | 1 verified, 1 errors |
| COI | `ensures` | COI: negate ensures clause '0.0 <= dose <= maxSafeDoseMgPerHr' | **killed** | 1 verified, 1 errors |
| COI | `ensures` | COI: negate ensures clause 'infusionRateMlPerHr > 0.0 || dose == 0.0' | **killed** | 1 verified, 2 errors |
