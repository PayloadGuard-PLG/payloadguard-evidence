// Phase 2, Gate C4: Spec-Testing Proofs (IronSpec methodology) for
// drug_interaction_checker.dfy, mirroring renal_adjustment_stp_suite.dfy's
// discipline. Each lemma restates the function's ACTUAL declared ensures
// clauses as premises on a fresh hypothetical output value, then proves
// either the correct value is forced (ACCEPT) or a wrong candidate value
// is provably excluded (REJECT, `ensures false`) -- testing the
// SPECIFICATION alone.
//
// Scope, stated explicitly rather than left implicit: this suite does
// NOT restate all pinning ensures clauses as separate lemmas -- that
// would be close to pure duplication, since each ensures clause already
// is the ACCEPT proof for its own cell. Instead: ACCEPT lemmas cover the
// worked examples already established in GATE_1C_AUDIT.md's hand-traces
// (for narrative continuity with Gate 1c), and REJECT lemmas target the
// three highest-stakes cells in the table -- the Contraindicated ones --
// proving a plausible but wrong, weaker candidate value is genuinely
// excluded, not just absent from the match body by construction.
//
// REQ-DDI-5 (built 2026-07-12): CheckInteraction gained a fourth
// parameter, treatmentIndication. Every lemma below that predates this
// change passes AFStrokePrevention as an arbitrary, unused placeholder
// -- none of these cells' outcomes depend on indication, so any
// constructible value proves the same lemma. The two new lemmas at the
// end of each section below are the ones that actually exercise the new
// parameter.

include "drug_interaction_checker.dfy"

// ================================================== Worked-example ACCEPT

// GATE_1C_AUDIT.md hand-trace 1: dabigatran + ketoconazole is
// contraindicated -- the pinning ensures clause forces this directly.
lemma STP_Accept_CheckInteraction_DabigatranKetoconazole(hasFlag: bool)
  ensures CheckInteraction(Dabigatran, Ketoconazole, hasFlag, AFStrokePrevention) == InteractionResult(Contraindicated, BleedingRisk)
{}

// GATE_1C_AUDIT.md hand-trace 2: edoxaban + ciclosporin gets a dose
// reduction -- the outcome KIND is proven; the specific "30mg daily"
// figure is REQ-DDI-6 (v2, not built).
lemma STP_Accept_CheckInteraction_EdoxabanCiclosporin(hasFlag: bool)
  ensures CheckInteraction(Edoxaban, Ciclosporin, hasFlag, AFStrokePrevention) == InteractionResult(DoseReductionAdvised, BleedingRisk)
{}

// GATE_1C_AUDIT.md hand-trace 3: apixaban + dronedarone is the one real
// source gap -- NotCovered, not an assumed negative.
lemma STP_Accept_CheckInteraction_ApixabanDronedarone(hasFlag: bool)
  ensures CheckInteraction(Apixaban, Dronedarone, hasFlag, AFStrokePrevention) == InteractionResult(NotCovered, UnknownRisk)
{}

// GATE_1C_AUDIT.md hand-trace 4: dabigatran + SSRIOrSNRI's dose
// reduction is conditional on the caller-supplied flag -- both branches
// proven, not just the one that happens to be exercised first.
lemma STP_Accept_CheckInteraction_DabigatranSSRI_WithRiskFactors()
  ensures CheckInteraction(Dabigatran, SSRIOrSNRI, true, AFStrokePrevention) == InteractionResult(DoseReductionAdvised, BleedingRisk)
{}

lemma STP_Accept_CheckInteraction_DabigatranSSRI_NoRiskFactors()
  ensures CheckInteraction(Dabigatran, SSRIOrSNRI, false, AFStrokePrevention) == InteractionResult(Caution, BleedingRisk)
{}

// GATE_1C_AUDIT.md hand-trace 5 / Gate 1c Finding 3: rivaroxaban +
// verapamil -- the exact cell the original hand-trace flagged as
// unresolved before Finding 3 decided CautionLowRelevance.
lemma STP_Accept_CheckInteraction_RivaroxabanVerapamil(hasFlag: bool)
  ensures CheckInteraction(Rivaroxaban, Verapamil, hasFlag, AFStrokePrevention) == InteractionResult(CautionLowRelevance, BleedingRisk)
{}

// GATE_1C_AUDIT.md hand-trace 6 / Gate 1c Finding 2: dabigatran +
// rifampicin -- one of the six cells recovered by the precondition
// redesign; direction correctly flips to ThrombosisRisk (rifampicin
// decreases DOAC levels, the opposite failure mode from most of this
// table).
lemma STP_Accept_CheckInteraction_DabigatranRifampicin(hasFlag: bool)
  ensures CheckInteraction(Dabigatran, Rifampicin, hasFlag, AFStrokePrevention) == InteractionResult(Avoid, ThrombosisRisk)
{}

// REQ-DDI-5 (built 2026-07-12): apixaban+rifampicin, the cell the
// precondition used to exclude outright -- now provable for both named
// treatment indications, both branches proven explicitly, mirroring the
// DabigatranSSRI both-branches pair above rather than trusting one
// indication value stands in for the other.
lemma STP_Accept_CheckInteraction_ApixabanRifampicin_AFStrokePrevention(hasFlag: bool)
  ensures CheckInteraction(Apixaban, Rifampicin, hasFlag, AFStrokePrevention) == InteractionResult(Caution, ThrombosisRisk)
{}

lemma STP_Accept_CheckInteraction_ApixabanRifampicin_RecurrentVTEPrevention(hasFlag: bool)
  ensures CheckInteraction(Apixaban, Rifampicin, hasFlag, RecurrentVTEPrevention) == InteractionResult(Caution, ThrombosisRisk)
{}

// ============================================ Safety-critical REJECT set
//
// The three Contraindicated cells are the highest-stakes rows in this
// table -- proving a plausible-but-wrong weaker candidate (Caution) is
// genuinely excluded, not just absent from the match arm by accident of
// how it happened to be written.

lemma STP_Reject_CheckInteraction_DabigatranKetoconazole_NotMerelyCaution(hasFlag: bool)
  requires CheckInteraction(Dabigatran, Ketoconazole, hasFlag, AFStrokePrevention) == InteractionResult(Caution, BleedingRisk) // wrong: real answer is Contraindicated
  ensures false
{}

lemma STP_Reject_CheckInteraction_DabigatranItraconazole_NotMerelyCaution(hasFlag: bool)
  requires CheckInteraction(Dabigatran, Itraconazole, hasFlag, AFStrokePrevention) == InteractionResult(Caution, BleedingRisk) // wrong: real answer is Contraindicated
  ensures false
{}

lemma STP_Reject_CheckInteraction_DabigatranCiclosporin_NotMerelyCaution(hasFlag: bool)
  requires CheckInteraction(Dabigatran, Ciclosporin, hasFlag, AFStrokePrevention) == InteractionResult(Caution, BleedingRisk) // wrong: real answer is Contraindicated
  ensures false
{}

// A fourth REJECT, targeting Gate 1c Finding 3's specific ambiguity:
// rivaroxaban+verapamil is NOT the unqualified negative digoxin gets --
// collapsing it to NoInteractionExpected (one of the two options Finding
// 3 explicitly rejected) is provably wrong.
lemma STP_Reject_CheckInteraction_RivaroxabanVerapamil_NotNoInteractionExpected(hasFlag: bool)
  requires CheckInteraction(Rivaroxaban, Verapamil, hasFlag, AFStrokePrevention) == InteractionResult(NoInteractionExpected, NoRisk) // wrong: source never states this unqualified
  ensures false
{}

// A fifth REJECT, specific to REQ-DDI-5's migration: before this cell
// was built, it returned NotCovered (Apixaban, Rifampicin was an
// unreachable match arm, precondition-excluded). Proves the new spec
// hasn't silently regressed to that old default for a known,
// now-sourced indication -- guards the migration itself, not just the
// destination value.
lemma STP_Reject_CheckInteraction_ApixabanRifampicin_NotStillNotCovered(hasFlag: bool)
  requires CheckInteraction(Apixaban, Rifampicin, hasFlag, AFStrokePrevention) == InteractionResult(NotCovered, UnknownRisk) // wrong: was the pre-REQ-DDI-5 unreachable-arm default
  ensures false
{}
