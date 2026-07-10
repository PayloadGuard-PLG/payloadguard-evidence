// Phase 2, Gate C4: Spec-Testing Proofs (IronSpec methodology) for
// drug_interaction_checker.dfy, mirroring renal_adjustment_stp_suite.dfy's
// discipline. Each lemma restates the function's ACTUAL declared ensures
// clauses as premises on a fresh hypothetical output value, then proves
// either the correct value is forced (ACCEPT) or a wrong candidate value
// is provably excluded (REJECT, `ensures false`) -- testing the
// SPECIFICATION alone.
//
// Scope, stated explicitly rather than left implicit: this suite does
// NOT restate all 60 pinning ensures clauses as separate lemmas -- that
// would be close to pure duplication, since each ensures clause already
// is the ACCEPT proof for its own cell. Instead: ACCEPT lemmas cover the
// worked examples already established in GATE_1C_AUDIT.md's hand-traces
// (for narrative continuity with Gate 1c), and REJECT lemmas target the
// three highest-stakes cells in the table -- the Contraindicated ones --
// proving a plausible but wrong, weaker candidate value is genuinely
// excluded, not just absent from the match body by construction.

include "drug_interaction_checker.dfy"

// ================================================== Worked-example ACCEPT

// GATE_1C_AUDIT.md hand-trace 1: dabigatran + ketoconazole is
// contraindicated -- the pinning ensures clause forces this directly.
lemma STP_Accept_CheckInteraction_DabigatranKetoconazole(hasFlag: bool)
  ensures CheckInteraction(Dabigatran, Ketoconazole, hasFlag) == InteractionResult(Contraindicated, BleedingRisk)
{}

// GATE_1C_AUDIT.md hand-trace 2: edoxaban + ciclosporin gets a dose
// reduction -- the outcome KIND is proven; the specific "30mg daily"
// figure is REQ-DDI-6 (v2, not built).
lemma STP_Accept_CheckInteraction_EdoxabanCiclosporin(hasFlag: bool)
  ensures CheckInteraction(Edoxaban, Ciclosporin, hasFlag) == InteractionResult(DoseReductionAdvised, BleedingRisk)
{}

// GATE_1C_AUDIT.md hand-trace 3: apixaban + dronedarone is the one real
// source gap -- NotCovered, not an assumed negative.
lemma STP_Accept_CheckInteraction_ApixabanDronedarone(hasFlag: bool)
  ensures CheckInteraction(Apixaban, Dronedarone, hasFlag) == InteractionResult(NotCovered, UnknownRisk)
{}

// GATE_1C_AUDIT.md hand-trace 4: dabigatran + SSRIOrSNRI's dose
// reduction is conditional on the caller-supplied flag -- both branches
// proven, not just the one that happens to be exercised first.
lemma STP_Accept_CheckInteraction_DabigatranSSRI_WithRiskFactors()
  ensures CheckInteraction(Dabigatran, SSRIOrSNRI, true) == InteractionResult(DoseReductionAdvised, BleedingRisk)
{}

lemma STP_Accept_CheckInteraction_DabigatranSSRI_NoRiskFactors()
  ensures CheckInteraction(Dabigatran, SSRIOrSNRI, false) == InteractionResult(Caution, BleedingRisk)
{}

// GATE_1C_AUDIT.md hand-trace 5 / Gate 1c Finding 3: rivaroxaban +
// verapamil -- the exact cell the original hand-trace flagged as
// unresolved before Finding 3 decided CautionLowRelevance.
lemma STP_Accept_CheckInteraction_RivaroxabanVerapamil(hasFlag: bool)
  ensures CheckInteraction(Rivaroxaban, Verapamil, hasFlag) == InteractionResult(CautionLowRelevance, BleedingRisk)
{}

// GATE_1C_AUDIT.md hand-trace 6 / Gate 1c Finding 2: dabigatran +
// rifampicin -- one of the six cells recovered by the precondition
// redesign; direction correctly flips to ThrombosisRisk (rifampicin
// decreases DOAC levels, the opposite failure mode from most of this
// table).
lemma STP_Accept_CheckInteraction_DabigatranRifampicin(hasFlag: bool)
  ensures CheckInteraction(Dabigatran, Rifampicin, hasFlag) == InteractionResult(Avoid, ThrombosisRisk)
{}

// ============================================ Safety-critical REJECT set
//
// The three Contraindicated cells are the highest-stakes rows in this
// table -- proving a plausible-but-wrong weaker candidate (Caution) is
// genuinely excluded, not just absent from the match arm by accident of
// how it happened to be written.

lemma STP_Reject_CheckInteraction_DabigatranKetoconazole_NotMerelyCaution(hasFlag: bool)
  requires CheckInteraction(Dabigatran, Ketoconazole, hasFlag) == InteractionResult(Caution, BleedingRisk) // wrong: real answer is Contraindicated
  ensures false
{}

lemma STP_Reject_CheckInteraction_DabigatranItraconazole_NotMerelyCaution(hasFlag: bool)
  requires CheckInteraction(Dabigatran, Itraconazole, hasFlag) == InteractionResult(Caution, BleedingRisk) // wrong: real answer is Contraindicated
  ensures false
{}

lemma STP_Reject_CheckInteraction_DabigatranCiclosporin_NotMerelyCaution(hasFlag: bool)
  requires CheckInteraction(Dabigatran, Ciclosporin, hasFlag) == InteractionResult(Caution, BleedingRisk) // wrong: real answer is Contraindicated
  ensures false
{}

// A fourth REJECT, targeting Gate 1c Finding 3's specific ambiguity:
// rivaroxaban+verapamil is NOT the unqualified negative digoxin gets --
// collapsing it to NoInteractionExpected (one of the two options Finding
// 3 explicitly rejected) is provably wrong.
lemma STP_Reject_CheckInteraction_RivaroxabanVerapamil_NotNoInteractionExpected(hasFlag: bool)
  requires CheckInteraction(Rivaroxaban, Verapamil, hasFlag) == InteractionResult(NoInteractionExpected, NoRisk) // wrong: source never states this unqualified
  ensures false
{}
