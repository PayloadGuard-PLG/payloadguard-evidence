// Gate C1: drug-interaction set-membership checker, PayloadGuard-Evidence's
// third worked example. Every cell below is transcribed from
// sources/sps-doac-interactions-2024.md (NHS SPS, "Managing interactions
// with direct oral anticoagulants (DOACs)", published 5 Jan 2024, last
// updated 20 Jun 2025) -- see PHASE1_PLAN.md's REQ-DDI-* table and
// GATE_1C_AUDIT.md for the full derivation and the three findings this
// design resolves.

datatype DOAC = Apixaban | Dabigatran | Edoxaban | Rivaroxaban

datatype Agent =
    Amiodarone | Digoxin | Diltiazem | Dronedarone | Verapamil
  | Clarithromycin | ErythromycinSystemic
  | Rifampicin
  | OtherDOACOrHeparinOrWarfarin
  | SSRIOrSNRI
  | Fluconazole
  | Itraconazole | Ketoconazole
  | Aspirin | Clopidogrel | Ticagrelor
  | Carbamazepine | Phenytoin | Phenobarbital
  | LevetiracetamOrValproateContaining
  | Ciclosporin
  | Tacrolimus
  | Ibuprofen | Naproxen

// Gate 1c Finding 1 (resolved): every one of the source's 17 sections is
// headed by exactly this distinction -- Outcome alone can't tell a reader
// which way to monitor (bleeding vs. thrombosis), and the source treats
// it as primary information, not a footnote.
datatype RiskDirection = BleedingRisk | ThrombosisRisk | NoRisk | UnknownRisk

// Gate 1c Finding 3 (resolved): CautionLowRelevance is distinct from both
// Caution and NoInteractionExpected -- honest about the source's own
// hedge ("unlikely to be clinically relevant") for the two cells
// (verapamil+rivaroxaban/apixaban, fluconazole+rivaroxaban) where the
// source never gives the clean, unqualified negative it gives digoxin.
datatype Outcome =
    NoInteractionExpected | Caution | CautionLowRelevance | Avoid
  | Contraindicated | DoseReductionAdvised | NotCovered

datatype InteractionResult = InteractionResult(outcome: Outcome, direction: RiskDirection)

// REQ-DDI-5 (built): the two treatment indications
// sources/sps-doac-interactions-2024.md's Rifampicin and
// Carbamazepine/Phenytoin/Phenobarbital rows name for apixaban --
// "prevention of stroke and systemic embolism in people with
// non-valvular atrial fibrillation" and "prevention of recurrent deep
// vein thrombosis (DVT) and pulmonary embolism (PE)" -- and *only*
// these two. Deliberately closed to exactly what the source names, not
// a third case for VTE-prophylaxis (hip/knee replacement): that
// indication exists in the eMC SmPC's posology material
// (sources/emc-smpc-apixaban-posology-2024.md) but the interaction
// source this function is scoped to never states an apixaban outcome
// for it -- adding it here would conflate two different source
// documents' scope, not extend this one honestly.
datatype TreatmentIndication = AFStrokePrevention | RecurrentVTEPrevention

// Gate 1c Finding 2 / REQ-DDI-5 (built 2026-07-12): Rifampicin and
// Carbamazepine/Phenytoin/Phenobarbital each make apixaban's outcome
// depend on a third axis, clinical indication -- previously excluded
// entirely by a precondition (Phase E, 2026-07-10) because the function
// had no way to express "the indication is known and is one of the
// source's two named categories." Once TreatmentIndication is closed to
// exactly those two categories, every constructible input is provable
// (the source gives apixaban the identical "use with caution" outcome
// for both named indications) -- so the exclusion is no longer needed
// and CheckInteraction is now total, no requires clause at all.
//
// v1 is classify-only (REQ-DDI-6, staged): DoseReductionAdvised means the
// source names a specific numeric target for that cell, not that this
// function proves the number -- the exact mg figure is v1 informational
// text only, per sources/sps-doac-interactions-2024.md.
function CheckInteraction(doac: DOAC, agent: Agent,
                           hasOtherBleedingRiskFactors: bool,
                           treatmentIndication: TreatmentIndication): InteractionResult
  // Gate C4 (Phase 2) finding, confirmed for real, not just predicted:
  // an earlier version of this function had only 3 ensures clauses (the
  // NotCovered/Contraindicated/Digoxin pins below) -- real IronSpec-
  // style ACCEPT lemmas restating ONLY those 3 clauses as premises
  // FAILED to prove the correct value for any other cell (e.g.
  // (Dabigatran, Ketoconazole) -- see
  // drug_interaction_checker_stp_suite_against_underconstrained.dfy, a
  // genuinely failing captured run: 0 verified, 3 errors). Unlike
  // renal_adjustment's Gate C4 finding (postconditions bounded without
  // pinning), most cells here had NO constraint at all, bound or pin --
  // the match body's correctness was never actually a claim of this
  // function's signature, only an artifact of the implementation.
  // Fixed by restating every one of the 63 match arms as an explicit
  // pinning ensures clause below, one per arm, mirroring the match body
  // 1:1 -- verbose, but an honest reflection of this function's actual
  // shape (a flat lookup table, not a clean range partition like
  // GStage's six boundary clauses).
  ensures agent == Amiodarone ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures agent == Digoxin ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(NoInteractionExpected, NoRisk)
  ensures agent == Diltiazem ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures agent == Clarithromycin ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures agent == OtherDOACOrHeparinOrWarfarin ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Avoid, BleedingRisk)
  ensures agent == Aspirin ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Avoid, BleedingRisk)
  ensures agent == Clopidogrel ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Avoid, BleedingRisk)
  ensures agent == Ticagrelor ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Avoid, BleedingRisk)
  ensures agent == LevetiracetamOrValproateContaining ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, ThrombosisRisk)
  ensures agent == Ibuprofen ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures agent == Naproxen ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures (doac == Dabigatran && agent == Dronedarone) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Avoid, BleedingRisk)
  ensures (doac == Rivaroxaban && agent == Dronedarone) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Avoid, BleedingRisk)
  ensures (doac == Edoxaban && agent == Dronedarone) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(DoseReductionAdvised, BleedingRisk)
  ensures (doac == Apixaban && agent == Dronedarone) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(NotCovered, UnknownRisk)
  ensures (doac == Dabigatran && agent == Verapamil) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(DoseReductionAdvised, BleedingRisk)
  ensures (doac == Rivaroxaban && agent == Verapamil) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(CautionLowRelevance, BleedingRisk)
  ensures (doac == Apixaban && agent == Verapamil) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(CautionLowRelevance, BleedingRisk)
  ensures (doac == Edoxaban && agent == Verapamil) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures (doac == Edoxaban && agent == ErythromycinSystemic) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(DoseReductionAdvised, BleedingRisk)
  ensures (doac == Dabigatran && agent == ErythromycinSystemic) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures (doac == Apixaban && agent == ErythromycinSystemic) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures (doac == Rivaroxaban && agent == ErythromycinSystemic) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures (doac == Dabigatran && agent == Rifampicin) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Avoid, ThrombosisRisk)
  ensures (doac == Edoxaban && agent == Rifampicin) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, ThrombosisRisk)
  ensures (doac == Rivaroxaban && agent == Rifampicin) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, ThrombosisRisk)
  // REQ-DDI-5 (built): sources/sps-doac-interactions-2024.md lines 80-84 --
  // "use apixaban with caution" for both named indications, the same
  // outcome either way; provable now that TreatmentIndication is closed
  // to exactly those two.
  ensures (doac == Apixaban && agent == Rifampicin && (treatmentIndication == AFStrokePrevention || treatmentIndication == RecurrentVTEPrevention)) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, ThrombosisRisk)
  ensures (doac == Dabigatran && agent == SSRIOrSNRI && hasOtherBleedingRiskFactors) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(DoseReductionAdvised, BleedingRisk)
  ensures (doac == Dabigatran && agent == SSRIOrSNRI && !hasOtherBleedingRiskFactors) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures (doac == Apixaban && agent == SSRIOrSNRI) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures (doac == Edoxaban && agent == SSRIOrSNRI) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures (doac == Rivaroxaban && agent == SSRIOrSNRI) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures (doac == Apixaban && agent == Fluconazole) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures (doac == Dabigatran && agent == Fluconazole) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures (doac == Rivaroxaban && agent == Fluconazole) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(CautionLowRelevance, BleedingRisk)
  ensures (doac == Edoxaban && agent == Fluconazole) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(NoInteractionExpected, NoRisk)
  ensures (doac == Dabigatran && agent == Itraconazole) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Contraindicated, BleedingRisk)
  ensures (doac == Apixaban && agent == Itraconazole) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Avoid, BleedingRisk)
  ensures (doac == Rivaroxaban && agent == Itraconazole) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Avoid, BleedingRisk)
  ensures (doac == Edoxaban && agent == Itraconazole) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Avoid, BleedingRisk)
  ensures (doac == Dabigatran && agent == Ketoconazole) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Contraindicated, BleedingRisk)
  ensures (doac == Apixaban && agent == Ketoconazole) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Avoid, BleedingRisk)
  ensures (doac == Rivaroxaban && agent == Ketoconazole) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Avoid, BleedingRisk)
  ensures (doac == Edoxaban && agent == Ketoconazole) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(DoseReductionAdvised, BleedingRisk)
  ensures (doac == Dabigatran && agent == Carbamazepine) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Avoid, ThrombosisRisk)
  ensures (doac == Edoxaban && agent == Carbamazepine) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, ThrombosisRisk)
  ensures (doac == Rivaroxaban && agent == Carbamazepine) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, ThrombosisRisk)
  // REQ-DDI-5 (built): same source rows (135-136), same two-indication
  // shape and outcome as Rifampicin above.
  ensures (doac == Apixaban && agent == Carbamazepine && (treatmentIndication == AFStrokePrevention || treatmentIndication == RecurrentVTEPrevention)) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, ThrombosisRisk)
  ensures (doac == Dabigatran && agent == Phenytoin) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Avoid, ThrombosisRisk)
  ensures (doac == Edoxaban && agent == Phenytoin) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, ThrombosisRisk)
  ensures (doac == Rivaroxaban && agent == Phenytoin) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, ThrombosisRisk)
  ensures (doac == Apixaban && agent == Phenytoin && (treatmentIndication == AFStrokePrevention || treatmentIndication == RecurrentVTEPrevention)) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, ThrombosisRisk)
  ensures (doac == Dabigatran && agent == Phenobarbital) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Avoid, ThrombosisRisk)
  ensures (doac == Edoxaban && agent == Phenobarbital) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, ThrombosisRisk)
  ensures (doac == Rivaroxaban && agent == Phenobarbital) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, ThrombosisRisk)
  ensures (doac == Apixaban && agent == Phenobarbital && (treatmentIndication == AFStrokePrevention || treatmentIndication == RecurrentVTEPrevention)) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, ThrombosisRisk)
  ensures (doac == Dabigatran && agent == Ciclosporin) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Contraindicated, BleedingRisk)
  ensures (doac == Edoxaban && agent == Ciclosporin) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(DoseReductionAdvised, BleedingRisk)
  ensures (doac == Apixaban && agent == Ciclosporin) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures (doac == Rivaroxaban && agent == Ciclosporin) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures (doac == Dabigatran && agent == Tacrolimus) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Avoid, BleedingRisk)
  ensures (doac == Apixaban && agent == Tacrolimus) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures (doac == Edoxaban && agent == Tacrolimus) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
  ensures (doac == Rivaroxaban && agent == Tacrolimus) ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors, treatmentIndication) == InteractionResult(Caution, BleedingRisk)
{
  match (doac, agent)

  // Uniform across all four DOACs -- the source gives one outcome
  // regardless of which DOAC is asked about.
  case (_, Amiodarone) => InteractionResult(Caution, BleedingRisk)
  case (_, Digoxin) => InteractionResult(NoInteractionExpected, NoRisk)
  case (_, Diltiazem) => InteractionResult(Caution, BleedingRisk)
  case (_, Clarithromycin) => InteractionResult(Caution, BleedingRisk)
  case (_, OtherDOACOrHeparinOrWarfarin) => InteractionResult(Avoid, BleedingRisk)
  case (_, Aspirin) => InteractionResult(Avoid, BleedingRisk)
  case (_, Clopidogrel) => InteractionResult(Avoid, BleedingRisk)
  case (_, Ticagrelor) => InteractionResult(Avoid, BleedingRisk)
  case (_, LevetiracetamOrValproateContaining) => InteractionResult(Caution, ThrombosisRisk)
  // NSAIDs: source says "Use concomitantly with caution or avoid if
  // possible" -- identical hedge phrasing to SSRIs/SNRIs below, resolved
  // the same way for consistency (the floor stated is Caution; "or
  // avoid if possible" is professional judgment above that floor, not a
  // separately-triggered outcome kind).
  case (_, Ibuprofen) => InteractionResult(Caution, BleedingRisk)
  case (_, Naproxen) => InteractionResult(Caution, BleedingRisk)

  // Dronedarone: per-DOAC. Apixaban is never mentioned in this section
  // at all -- a real source gap, not assumed safe (Gate 1c, REQ-DDI-4).
  case (Dabigatran, Dronedarone) => InteractionResult(Avoid, BleedingRisk)
  case (Rivaroxaban, Dronedarone) => InteractionResult(Avoid, BleedingRisk)
  case (Edoxaban, Dronedarone) => InteractionResult(DoseReductionAdvised, BleedingRisk)
  case (Apixaban, Dronedarone) => InteractionResult(NotCovered, UnknownRisk)

  // Verapamil: dabigatran gets a dose reduction; rivaroxaban/apixaban are
  // explicitly downgraded ("unlikely to be clinically relevant") --
  // CautionLowRelevance, Gate 1c Finding 3. Edoxaban gets the row's
  // plain baseline.
  case (Dabigatran, Verapamil) => InteractionResult(DoseReductionAdvised, BleedingRisk)
  case (Rivaroxaban, Verapamil) => InteractionResult(CautionLowRelevance, BleedingRisk)
  case (Apixaban, Verapamil) => InteractionResult(CautionLowRelevance, BleedingRisk)
  case (Edoxaban, Verapamil) => InteractionResult(Caution, BleedingRisk)

  // Erythromycin (systemic): only this named macrolide, not
  // clarithromycin, gets edoxaban's specific dose reduction.
  case (Edoxaban, ErythromycinSystemic) => InteractionResult(DoseReductionAdvised, BleedingRisk)
  case (Dabigatran, ErythromycinSystemic) => InteractionResult(Caution, BleedingRisk)
  case (Apixaban, ErythromycinSystemic) => InteractionResult(Caution, BleedingRisk)
  case (Rivaroxaban, ErythromycinSystemic) => InteractionResult(Caution, BleedingRisk)

  // Rifampicin: dabigatran/edoxaban/rivaroxaban recovered by Gate 1c
  // Finding 2's precondition redesign; apixaban excluded above.
  case (Dabigatran, Rifampicin) => InteractionResult(Avoid, ThrombosisRisk)
  case (Edoxaban, Rifampicin) => InteractionResult(Caution, ThrombosisRisk)
  case (Rivaroxaban, Rifampicin) => InteractionResult(Caution, ThrombosisRisk)
  // REQ-DDI-5 (built): both named treatment indications give the same
  // outcome, so the match arm doesn't need to branch on
  // treatmentIndication -- the closed TreatmentIndication type is what
  // makes this cell provable at all, not a value it needs to inspect.
  case (Apixaban, Rifampicin) => InteractionResult(Caution, ThrombosisRisk)

  // SSRIs/SNRIs (REQ-DDI-3): dabigatran's dose reduction is conditional
  // on the caller-supplied hasOtherBleedingRiskFactors flag -- same
  // trust boundary as REQ-RENAL-8's classification flags.
  case (Dabigatran, SSRIOrSNRI) =>
    if hasOtherBleedingRiskFactors
    then InteractionResult(DoseReductionAdvised, BleedingRisk)
    else InteractionResult(Caution, BleedingRisk)
  case (Apixaban, SSRIOrSNRI) => InteractionResult(Caution, BleedingRisk)
  case (Edoxaban, SSRIOrSNRI) => InteractionResult(Caution, BleedingRisk)
  case (Rivaroxaban, SSRIOrSNRI) => InteractionResult(Caution, BleedingRisk)

  // Fluconazole: three distinct per-DOAC outcomes on one row --
  // apixaban/dabigatran caution, rivaroxaban downgraded (Finding 3),
  // edoxaban an explicit no-interaction.
  case (Apixaban, Fluconazole) => InteractionResult(Caution, BleedingRisk)
  case (Dabigatran, Fluconazole) => InteractionResult(Caution, BleedingRisk)
  case (Rivaroxaban, Fluconazole) => InteractionResult(CautionLowRelevance, BleedingRisk)
  case (Edoxaban, Fluconazole) => InteractionResult(NoInteractionExpected, NoRisk)

  // Itraconazole: contraindicated with dabigatran, not recommended
  // (Avoid) with the other three; no DOAC-specific dose reduction named
  // for itraconazole (unlike ketoconazole, below).
  case (Dabigatran, Itraconazole) => InteractionResult(Contraindicated, BleedingRisk)
  case (Apixaban, Itraconazole) => InteractionResult(Avoid, BleedingRisk)
  case (Rivaroxaban, Itraconazole) => InteractionResult(Avoid, BleedingRisk)
  case (Edoxaban, Itraconazole) => InteractionResult(Avoid, BleedingRisk)

  // Ketoconazole: same contraindicated/not-recommended shape as
  // itraconazole, but edoxaban specifically gets a dose reduction here.
  case (Dabigatran, Ketoconazole) => InteractionResult(Contraindicated, BleedingRisk)
  case (Apixaban, Ketoconazole) => InteractionResult(Avoid, BleedingRisk)
  case (Rivaroxaban, Ketoconazole) => InteractionResult(Avoid, BleedingRisk)
  case (Edoxaban, Ketoconazole) => InteractionResult(DoseReductionAdvised, BleedingRisk)

  // Carbamazepine / Phenytoin / Phenobarbital: same shape as Rifampicin
  // -- three recovered cells each, apixaban excluded above.
  case (Dabigatran, Carbamazepine) => InteractionResult(Avoid, ThrombosisRisk)
  case (Edoxaban, Carbamazepine) => InteractionResult(Caution, ThrombosisRisk)
  case (Rivaroxaban, Carbamazepine) => InteractionResult(Caution, ThrombosisRisk)
  // REQ-DDI-5 (built): same rationale as (Apixaban, Rifampicin) above.
  case (Apixaban, Carbamazepine) => InteractionResult(Caution, ThrombosisRisk)

  case (Dabigatran, Phenytoin) => InteractionResult(Avoid, ThrombosisRisk)
  case (Edoxaban, Phenytoin) => InteractionResult(Caution, ThrombosisRisk)
  case (Rivaroxaban, Phenytoin) => InteractionResult(Caution, ThrombosisRisk)
  // REQ-DDI-5 (built): same rationale as (Apixaban, Rifampicin) above.
  case (Apixaban, Phenytoin) => InteractionResult(Caution, ThrombosisRisk)

  case (Dabigatran, Phenobarbital) => InteractionResult(Avoid, ThrombosisRisk)
  case (Edoxaban, Phenobarbital) => InteractionResult(Caution, ThrombosisRisk)
  case (Rivaroxaban, Phenobarbital) => InteractionResult(Caution, ThrombosisRisk)
  // REQ-DDI-5 (built): same rationale as (Apixaban, Rifampicin) above.
  case (Apixaban, Phenobarbital) => InteractionResult(Caution, ThrombosisRisk)

  // Ciclosporin: contraindicated with dabigatran; edoxaban gets a dose
  // reduction; apixaban/rivaroxaban a plain caution.
  case (Dabigatran, Ciclosporin) => InteractionResult(Contraindicated, BleedingRisk)
  case (Edoxaban, Ciclosporin) => InteractionResult(DoseReductionAdvised, BleedingRisk)
  case (Apixaban, Ciclosporin) => InteractionResult(Caution, BleedingRisk)
  case (Rivaroxaban, Ciclosporin) => InteractionResult(Caution, BleedingRisk)

  // Tacrolimus: dabigatran is "avoid," deliberately kept distinct from
  // ciclosporin's dabigatran "contraindicated" -- different words in the
  // source, not treated as synonyms.
  case (Dabigatran, Tacrolimus) => InteractionResult(Avoid, BleedingRisk)
  case (Apixaban, Tacrolimus) => InteractionResult(Caution, BleedingRisk)
  case (Edoxaban, Tacrolimus) => InteractionResult(Caution, BleedingRisk)
  case (Rivaroxaban, Tacrolimus) => InteractionResult(Caution, BleedingRisk)
}

// REQ-DDI-6 (built 2026-07-12): CheckInteraction's 60+ ensures clauses
// prove the OUTCOME KIND (DoseReductionAdvised) for six real cells, but
// not the specific mg figure -- that was v1 informational text only.
// This function proves the figure, scoped to exactly the five cells
// where sources/sps-doac-interactions-2024.md actually states a number:
// (Dabigatran, Verapamil) -> 110mg twice daily; (Edoxaban, Dronedarone),
// (Edoxaban, ErythromycinSystemic), (Edoxaban, Ketoconazole), (Edoxaban,
// Ciclosporin) -> 30mg daily/once daily each (sourced individually per
// row, not one shared constant -- confirmed the figure is the same
// value for unrelated reasons in each case, not because they're the
// same rule).
//
// (Dabigatran, SSRIOrSNRI) is deliberately EXCLUDED even though it also
// yields DoseReductionAdvised (when hasOtherBleedingRiskFactors is
// true): the source only says "consider a dose reduction (as per the
// Summary of Product Characteristics)" for that cell, no mg figure --
// it is v1/v2 informational text forever, not a temporary gap. Apixaban
// never appears in this function's precondition at all -- not a special
// case written in, but a direct consequence of CheckInteraction never
// producing a DoseReductionAdvised outcome for apixaban anywhere in its
// 63 match arms.
//
// requires-gated bare-int totality, matching SelectFormula/
// AssessRenalFunction's existing precedent in renal_adjustment.dfy,
// rather than introducing this repo's first Option<int> pattern.
function DoseReductionTargetMg(doac: DOAC, agent: Agent): int
  requires (doac == Dabigatran && agent == Verapamil)
        || (doac == Edoxaban && agent == Dronedarone)
        || (doac == Edoxaban && agent == ErythromycinSystemic)
        || (doac == Edoxaban && agent == Ketoconazole)
        || (doac == Edoxaban && agent == Ciclosporin)
  ensures (doac == Dabigatran && agent == Verapamil) ==> DoseReductionTargetMg(doac, agent) == 110
  ensures (doac == Edoxaban && agent == Dronedarone) ==> DoseReductionTargetMg(doac, agent) == 30
  ensures (doac == Edoxaban && agent == ErythromycinSystemic) ==> DoseReductionTargetMg(doac, agent) == 30
  ensures (doac == Edoxaban && agent == Ketoconazole) ==> DoseReductionTargetMg(doac, agent) == 30
  ensures (doac == Edoxaban && agent == Ciclosporin) ==> DoseReductionTargetMg(doac, agent) == 30
{
  match (doac, agent)
  case (Dabigatran, Verapamil) => 110
  case (Edoxaban, Dronedarone) => 30
  case (Edoxaban, ErythromycinSystemic) => 30
  case (Edoxaban, Ketoconazole) => 30
  case (Edoxaban, Ciclosporin) => 30
  // Dafny's match requires exhaustiveness over the full (DOAC, Agent)
  // type regardless of the requires clause above -- every other
  // combination is genuinely unreachable at any real call site, the
  // same pattern CheckInteraction itself no longer needs (REQ-DDI-5)
  // but this narrower-precondition function still does. `assert false`
  // makes Dafny prove this branch is unreachable rather than silently
  // returning a plausible-looking 0mg value on a hypothetical
  // precondition-violating call from unverified code -- verified
  // empirically to still type-check and verify cleanly.
  case _ => (assert false; 0) // unreachable: excluded by the precondition above
}
