// Preserved review artifact -- Gate C4 (Phase 2) honesty exhibit, same
// rationale as dosage_underconstrained.dfy / renal_adjustment_underconstrained.dfy:
// this is drug_interaction_checker.dfy byte-for-byte as it was first
// verified and committed (Gate C1, 2026-07-10), before Gate C4's
// Spec-Testing Proofs found it severely under-constrained.
//
// THE GAP, confirmed mechanically
// (drug_interaction_checker_stp_suite_against_underconstrained.dfy), not
// by inspection alone: only 3 of CheckInteraction's 63 match arms were
// backed by any ensures clause at all (the NotCovered/Contraindicated/
// Digoxin pins). For every other cell -- e.g. (Dabigatran, Ketoconazole)
// -- nothing in the declared specification forced the correct value; an
// IronSpec-style ACCEPT lemma restating only the declared ensures
// clauses as premises FAILS to prove the correct answer is even
// *possible*, let alone forced, for that cell. This is a stronger gap
// than renal_adjustment's Gate C4 finding (which bounded without
// pinning) -- here most cells had no constraint at all, bound or pin.
// See drug_interaction_checker.dfy's current header for the fix (60
// comprehensive pinning ensures clauses, one per match arm) and
// GATE_1C_AUDIT.md / KNOWN_LIMITATIONS.md's "Phase E Gate C4" section
// for the full account.

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

// Gate 1c Finding 2 (resolved): Rifampicin and Carbamazepine/Phenytoin/
// Phenobarbital each make apixaban's outcome depend on a third axis,
// clinical indication (REQ-DDI-5, not built in v1) -- their other three
// DOAC cells are real, sourced, and provable now. The precondition below
// makes the still-blocked apixaban cell a provable exclusion at every
// call site, not a silently wrong or undefined answer. (Written as an
// explicit disjunction, not a set literal, to stay within syntax already
// confirmed supported by Gate C3's precondition-satisfiability translator
// -- comparisons and booleans, not set membership, which hasn't been
// verified against that translator yet.)
//
// v1 is classify-only (REQ-DDI-6, staged): DoseReductionAdvised means the
// source names a specific numeric target for that cell, not that this
// function proves the number -- the exact mg figure is v1 informational
// text only, per sources/sps-doac-interactions-2024.md.
function CheckInteraction(doac: DOAC, agent: Agent,
                           hasOtherBleedingRiskFactors: bool): InteractionResult
  requires !(doac == Apixaban &&
             (agent == Rifampicin || agent == Carbamazepine ||
              agent == Phenytoin || agent == Phenobarbital))
  // Real claims, not a vacuous match -- a function with no ensures
  // clauses gives Dafny nothing to prove (match-exhaustiveness is a
  // resolve-time syntax check, not a verification task; confirmed
  // empirically -- an earlier draft with no ensures reported "0
  // verified, 0 errors," a false-clean result, not committed). Full
  // per-cell pinning of all 63 match arms belongs to Gate C4's STP
  // lemmas (matching how GStage/SelectFormula/ComposedCeiling each
  // commit to a real claim in their own signature, with exhaustive
  // per-value pinning left to the STP suite, not duplicated here).
  ensures CheckInteraction(doac, agent, hasOtherBleedingRiskFactors).outcome == NotCovered
          ==> (doac == Apixaban && agent == Dronedarone)   // REQ-DDI-4: the only real source gap
  ensures CheckInteraction(doac, agent, hasOtherBleedingRiskFactors).outcome == Contraindicated
          ==> doac == Dabigatran   // every Contraindicated cell in this table is a dabigatran cell
  ensures agent == Digoxin
          ==> CheckInteraction(doac, agent, hasOtherBleedingRiskFactors) == InteractionResult(NoInteractionExpected, NoRisk)
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
  case (Apixaban, Rifampicin) => InteractionResult(NotCovered, UnknownRisk) // unreachable: excluded by the precondition above

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
  case (Apixaban, Carbamazepine) => InteractionResult(NotCovered, UnknownRisk) // unreachable: excluded by the precondition above

  case (Dabigatran, Phenytoin) => InteractionResult(Avoid, ThrombosisRisk)
  case (Edoxaban, Phenytoin) => InteractionResult(Caution, ThrombosisRisk)
  case (Rivaroxaban, Phenytoin) => InteractionResult(Caution, ThrombosisRisk)
  case (Apixaban, Phenytoin) => InteractionResult(NotCovered, UnknownRisk) // unreachable: excluded by the precondition above

  case (Dabigatran, Phenobarbital) => InteractionResult(Avoid, ThrombosisRisk)
  case (Edoxaban, Phenobarbital) => InteractionResult(Caution, ThrombosisRisk)
  case (Rivaroxaban, Phenobarbital) => InteractionResult(Caution, ThrombosisRisk)
  case (Apixaban, Phenobarbital) => InteractionResult(NotCovered, UnknownRisk) // unreachable: excluded by the precondition above

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
