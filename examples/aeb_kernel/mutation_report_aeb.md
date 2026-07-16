# Gate C5: mutation testing report — `aeb_kernel.dfy` (all 6 functions)

Generated 2026-07-16T12:22:11.572308+00:00. 63 mutants total. Counts: filtered_magnitude_implied=5, filtered_static=12, killed=38, survived=4, unclassifiable=4

SOR: 0 mutants (no set-typed operations in this spec) — NOT APPLICABLE, checked.
HOR: 0 mutants (no heap/object state, old()/reads/modifies) — NOT APPLICABLE, checked.
AOR/LVR body mutation: NOT APPLICABLE to any function's own body — all six are pure comparison/match logic with no +, -, *, or / operator in any function body (confirmed by reading aeb_kernel.dfy directly); clause-level ROR/LOR/AOR/LVR/COI (on requires/ensures) still run for all six.

| Function | Operator | Clause | Mutation | Outcome | Detail |
|---|---|---|---|---|---|
| FCWRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == LeadVehicleTarget ==>': == -> <= | **filtered_static** | statically weaker (ensures) |
| FCWRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == LeadVehicleTarget ==>': == -> >= | **filtered_static** | statically weaker (ensures) |
| FCWRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == LeadVehicleTarget ==>': == -> != | **killed** | 5 verified, 1 errors |
| FCWRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == LeadVehicleTarget ==>': == -> < | **killed** | 5 verified, 1 errors |
| FCWRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == LeadVehicleTarget ==>': == -> > | **killed** | 5 verified, 1 errors |
| FCWRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == PedestrianTarget ==>': == -> <= | **filtered_static** | statically weaker (ensures) |
| FCWRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == PedestrianTarget ==>': == -> >= | **filtered_static** | statically weaker (ensures) |
| FCWRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == PedestrianTarget ==>': == -> != | **killed** | 5 verified, 1 errors |
| FCWRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == PedestrianTarget ==>': == -> < | **killed** | 5 verified, 1 errors |
| FCWRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == PedestrianTarget ==>': == -> > | **killed** | 5 verified, 1 errors |
| FCWRequiredActive | COI | `ensures` | COI: negate ensures clause 'target == LeadVehicleTarget ==>' | **unclassifiable** | <mutant>.dfy(62,43): Error: invalid UnaryExpression |
| FCWRequiredActive | COI | `ensures` | COI: negate ensures clause 'target == PedestrianTarget ==>' | **unclassifiable** | <mutant>.dfy(64,42): Error: invalid UnaryExpression |
| AEBRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == LeadVehicleTarget ==>': == -> <= | **filtered_static** | statically weaker (ensures) |
| AEBRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == LeadVehicleTarget ==>': == -> >= | **filtered_static** | statically weaker (ensures) |
| AEBRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == LeadVehicleTarget ==>': == -> != | **killed** | 5 verified, 1 errors |
| AEBRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == LeadVehicleTarget ==>': == -> < | **killed** | 5 verified, 1 errors |
| AEBRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == LeadVehicleTarget ==>': == -> > | **killed** | 5 verified, 1 errors |
| AEBRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == PedestrianTarget ==>': == -> <= | **filtered_static** | statically weaker (ensures) |
| AEBRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == PedestrianTarget ==>': == -> >= | **filtered_static** | statically weaker (ensures) |
| AEBRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == PedestrianTarget ==>': == -> != | **killed** | 5 verified, 1 errors |
| AEBRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == PedestrianTarget ==>': == -> < | **killed** | 5 verified, 1 errors |
| AEBRequiredActive | ROR | `ensures` | ROR on ensures clause 'target == PedestrianTarget ==>': == -> > | **killed** | 5 verified, 1 errors |
| AEBRequiredActive | COI | `ensures` | COI: negate ensures clause 'target == LeadVehicleTarget ==>' | **unclassifiable** | <mutant>.dfy(82,43): Error: invalid UnaryExpression |
| AEBRequiredActive | COI | `ensures` | COI: negate ensures clause 'target == PedestrianTarget ==>' | **unclassifiable** | <mutant>.dfy(84,42): Error: invalid UnaryExpression |
| IsSubjectVehicleBrakingOnset | ROR | `ensures` | ROR on ensures clause 'IsSubjectVehicleBrakingOnset(decelG) <==> decelG >= 0.15': >= -> <= | **killed** | 5 verified, 1 errors |
| IsSubjectVehicleBrakingOnset | ROR | `ensures` | ROR on ensures clause 'IsSubjectVehicleBrakingOnset(decelG) <==> decelG >= 0.15': >= -> == | **killed** | 5 verified, 1 errors |
| IsSubjectVehicleBrakingOnset | ROR | `ensures` | ROR on ensures clause 'IsSubjectVehicleBrakingOnset(decelG) <==> decelG >= 0.15': >= -> != | **killed** | 5 verified, 1 errors |
| IsSubjectVehicleBrakingOnset | ROR | `ensures` | ROR on ensures clause 'IsSubjectVehicleBrakingOnset(decelG) <==> decelG >= 0.15': >= -> < | **killed** | 5 verified, 1 errors |
| IsSubjectVehicleBrakingOnset | ROR | `ensures` | ROR on ensures clause 'IsSubjectVehicleBrakingOnset(decelG) <==> decelG >= 0.15': >= -> > | **killed** | 5 verified, 1 errors |
| IsSubjectVehicleBrakingOnset | COI | `ensures` | COI: negate ensures clause 'IsSubjectVehicleBrakingOnset(decelG) <==> decelG >= 0.15' | **killed** | 5 verified, 1 errors |
| IsSubjectVehicleBrakingOnset | LVR | `ensures` | LVR on ensures clause 'IsSubjectVehicleBrakingOnset(decelG) <==> decelG >= 0.15': 0.15 -> 0.14 | **filtered_magnitude_implied** | magnitude-implied (ensures) |
| IsSubjectVehicleBrakingOnset | LVR | `ensures` | LVR on ensures clause 'IsSubjectVehicleBrakingOnset(decelG) <==> decelG >= 0.15': 0.15 -> 0.16 | **killed** | 5 verified, 1 errors |
| IsLeadVehicleBrakingOnset | ROR | `ensures` | ROR on ensures clause 'IsLeadVehicleBrakingOnset(decelG) <==> decelG >= 0.05': >= -> <= | **killed** | 5 verified, 1 errors |
| IsLeadVehicleBrakingOnset | ROR | `ensures` | ROR on ensures clause 'IsLeadVehicleBrakingOnset(decelG) <==> decelG >= 0.05': >= -> == | **killed** | 5 verified, 1 errors |
| IsLeadVehicleBrakingOnset | ROR | `ensures` | ROR on ensures clause 'IsLeadVehicleBrakingOnset(decelG) <==> decelG >= 0.05': >= -> != | **killed** | 5 verified, 1 errors |
| IsLeadVehicleBrakingOnset | ROR | `ensures` | ROR on ensures clause 'IsLeadVehicleBrakingOnset(decelG) <==> decelG >= 0.05': >= -> < | **killed** | 5 verified, 1 errors |
| IsLeadVehicleBrakingOnset | ROR | `ensures` | ROR on ensures clause 'IsLeadVehicleBrakingOnset(decelG) <==> decelG >= 0.05': >= -> > | **killed** | 5 verified, 1 errors |
| IsLeadVehicleBrakingOnset | COI | `ensures` | COI: negate ensures clause 'IsLeadVehicleBrakingOnset(decelG) <==> decelG >= 0.05' | **killed** | 5 verified, 1 errors |
| IsLeadVehicleBrakingOnset | LVR | `ensures` | LVR on ensures clause 'IsLeadVehicleBrakingOnset(decelG) <==> decelG >= 0.05': 0.05 -> 0.04 | **filtered_magnitude_implied** | magnitude-implied (ensures) |
| IsLeadVehicleBrakingOnset | LVR | `ensures` | LVR on ensures clause 'IsLeadVehicleBrakingOnset(decelG) <==> decelG >= 0.05': 0.05 -> 0.06 | **killed** | 5 verified, 1 errors |
| IsBrakePedalApplicationOnset | ROR | `ensures` | ROR on ensures clause 'IsBrakePedalApplicationOnset(forceN) <==> forceN >= 11.0': >= -> <= | **killed** | 5 verified, 1 errors |
| IsBrakePedalApplicationOnset | ROR | `ensures` | ROR on ensures clause 'IsBrakePedalApplicationOnset(forceN) <==> forceN >= 11.0': >= -> == | **killed** | 5 verified, 1 errors |
| IsBrakePedalApplicationOnset | ROR | `ensures` | ROR on ensures clause 'IsBrakePedalApplicationOnset(forceN) <==> forceN >= 11.0': >= -> != | **killed** | 5 verified, 1 errors |
| IsBrakePedalApplicationOnset | ROR | `ensures` | ROR on ensures clause 'IsBrakePedalApplicationOnset(forceN) <==> forceN >= 11.0': >= -> < | **killed** | 5 verified, 1 errors |
| IsBrakePedalApplicationOnset | ROR | `ensures` | ROR on ensures clause 'IsBrakePedalApplicationOnset(forceN) <==> forceN >= 11.0': >= -> > | **killed** | 5 verified, 1 errors |
| IsBrakePedalApplicationOnset | COI | `ensures` | COI: negate ensures clause 'IsBrakePedalApplicationOnset(forceN) <==> forceN >= 11.0' | **killed** | 5 verified, 1 errors |
| IsBrakePedalApplicationOnset | LVR | `ensures` | LVR on ensures clause 'IsBrakePedalApplicationOnset(forceN) <==> forceN >= 11.0': 11.0 -> 10.99 | **filtered_magnitude_implied** | magnitude-implied (ensures) |
| IsBrakePedalApplicationOnset | LVR | `ensures` | LVR on ensures clause 'IsBrakePedalApplicationOnset(forceN) <==> forceN >= 11.0': 11.0 -> 11.01 | **killed** | 5 verified, 1 errors |
| IsFalseActivationCompliant | ROR | `requires` | ROR on requires clause 'peakAdditionalDecelG >= 0.0': >= -> <= | **survived** | 6 verified, 0 errors |
| IsFalseActivationCompliant | ROR | `requires` | ROR on requires clause 'peakAdditionalDecelG >= 0.0': >= -> == | **filtered_static** | statically weaker (requires) |
| IsFalseActivationCompliant | ROR | `requires` | ROR on requires clause 'peakAdditionalDecelG >= 0.0': >= -> != | **survived** | 6 verified, 0 errors |
| IsFalseActivationCompliant | ROR | `requires` | ROR on requires clause 'peakAdditionalDecelG >= 0.0': >= -> < | **survived** | 6 verified, 0 errors |
| IsFalseActivationCompliant | ROR | `requires` | ROR on requires clause 'peakAdditionalDecelG >= 0.0': >= -> > | **filtered_static** | statically weaker (requires) |
| IsFalseActivationCompliant | ROR | `ensures` | ROR on ensures clause 'IsFalseActivationCompliant(peakAdditionalDecelG) <==> peakAdditionalDecelG < 0.25': < -> <= | **filtered_static** | statically weaker (ensures) |
| IsFalseActivationCompliant | ROR | `ensures` | ROR on ensures clause 'IsFalseActivationCompliant(peakAdditionalDecelG) <==> peakAdditionalDecelG < 0.25': < -> >= | **killed** | 5 verified, 1 errors |
| IsFalseActivationCompliant | ROR | `ensures` | ROR on ensures clause 'IsFalseActivationCompliant(peakAdditionalDecelG) <==> peakAdditionalDecelG < 0.25': < -> == | **killed** | 5 verified, 1 errors |
| IsFalseActivationCompliant | ROR | `ensures` | ROR on ensures clause 'IsFalseActivationCompliant(peakAdditionalDecelG) <==> peakAdditionalDecelG < 0.25': < -> != | **filtered_static** | statically weaker (ensures) |
| IsFalseActivationCompliant | ROR | `ensures` | ROR on ensures clause 'IsFalseActivationCompliant(peakAdditionalDecelG) <==> peakAdditionalDecelG < 0.25': < -> > | **killed** | 5 verified, 1 errors |
| IsFalseActivationCompliant | COI | `ensures` | COI: negate ensures clause 'IsFalseActivationCompliant(peakAdditionalDecelG) <==> peakAdditionalDecelG < 0.25' | **killed** | 5 verified, 1 errors |
| IsFalseActivationCompliant | LVR | `requires` | LVR on requires clause 'peakAdditionalDecelG >= 0.0': 0.0 -> -0.01 | **survived** | 6 verified, 0 errors |
| IsFalseActivationCompliant | LVR | `requires` | LVR on requires clause 'peakAdditionalDecelG >= 0.0': 0.0 -> 0.01 | **filtered_magnitude_implied** | magnitude-implied (requires) |
| IsFalseActivationCompliant | LVR | `ensures` | LVR on ensures clause 'IsFalseActivationCompliant(peakAdditionalDecelG) <==> peakAdditionalDecelG < 0.25': 0.25 -> 0.24 | **killed** | 5 verified, 1 errors |
| IsFalseActivationCompliant | LVR | `ensures` | LVR on ensures clause 'IsFalseActivationCompliant(peakAdditionalDecelG) <==> peakAdditionalDecelG < 0.25': 0.25 -> 0.26 | **filtered_magnitude_implied** | magnitude-implied (ensures) |
