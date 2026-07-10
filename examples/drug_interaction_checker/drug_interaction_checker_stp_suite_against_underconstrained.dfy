// Phase 2, Gate C4: honesty exhibit, same rationale as
// renal_adjustment_stp_suite_against_underconstrained.dfy. These three
// ACCEPT lemmas restate ONLY drug_interaction_checker_underconstrained.dfy's
// three original ensures clauses (the NotCovered/Contraindicated/Digoxin
// pins) as premises on a fresh hypothetical result -- no other
// constraint is assumed. Each targets a cell tied to one of Gate 1c's
// three findings, to make the connection concrete rather than abstract.
// Expected, predicted before running: all three FAIL to verify, because
// the underconstrained spec's three clauses say nothing about any of
// these three specific cells.

include "drug_interaction_checker_underconstrained.dfy"

// Gate 1c Finding 1 (RiskDirection) / Finding 2 (the recovered Rifampicin
// cells): (Dabigatran, Rifampicin) should be Avoid/ThrombosisRisk, but
// nothing in the underconstrained spec's three clauses says so.
lemma STP_Accept_CheckInteraction_DabigatranRifampicin_AGAINST_UNDERCONSTRAINED(
  r: InteractionResult
)
  requires r.outcome == NotCovered ==> (Dabigatran == Apixaban && Rifampicin == Dronedarone)
  requires r.outcome == Contraindicated ==> Dabigatran == Dabigatran
  requires Rifampicin == Digoxin ==> r == InteractionResult(NoInteractionExpected, NoRisk)
  ensures r == InteractionResult(Avoid, ThrombosisRisk)
{}

// Gate 1c Finding 3 (CautionLowRelevance): (Rivaroxaban, Verapamil) should
// be CautionLowRelevance/BleedingRisk -- the exact cell the original
// hand-trace flagged as unresolved before Finding 3 was decided.
lemma STP_Accept_CheckInteraction_RivaroxabanVerapamil_AGAINST_UNDERCONSTRAINED(
  r: InteractionResult
)
  requires r.outcome == NotCovered ==> (Rivaroxaban == Apixaban && Verapamil == Dronedarone)
  requires r.outcome == Contraindicated ==> Rivaroxaban == Dabigatran
  requires Verapamil == Digoxin ==> r == InteractionResult(NoInteractionExpected, NoRisk)
  ensures r == InteractionResult(CautionLowRelevance, BleedingRisk)
{}

// A plain dose-reduction cell, unconnected to any of the three findings,
// showing the gap isn't limited to the cells Gate 1c happened to flag --
// it's the whole table minus 3 clauses.
lemma STP_Accept_CheckInteraction_EdoxabanCiclosporin_AGAINST_UNDERCONSTRAINED(
  r: InteractionResult
)
  requires r.outcome == NotCovered ==> (Edoxaban == Apixaban && Ciclosporin == Dronedarone)
  requires r.outcome == Contraindicated ==> Edoxaban == Dabigatran
  requires Ciclosporin == Digoxin ==> r == InteractionResult(NoInteractionExpected, NoRisk)
  ensures r == InteractionResult(DoseReductionAdvised, BleedingRisk)
{}
