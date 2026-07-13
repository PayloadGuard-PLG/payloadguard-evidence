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
// reduction -- the outcome KIND is proven here; the specific "30mg
// daily" figure is proven separately below (REQ-DDI-6, built
// 2026-07-12).
lemma STP_Accept_CheckInteraction_EdoxabanCiclosporin(hasFlag: bool)
  ensures CheckInteraction(Edoxaban, Ciclosporin, hasFlag, AFStrokePrevention) == InteractionResult(DoseReductionAdvised, BleedingRisk)
{}

// REQ-DDI-6 (built 2026-07-12): DoseReductionTargetMg's two real,
// sourced figures, one worked example per DOAC rather than restating
// all five cells (matching this suite's own stated non-exhaustive
// discipline) -- continues the EdoxabanCiclosporin hand-trace above
// with the actual mg figure, plus the other DOAC's own figure so both
// real values in this function are proven at least once, not just one.
lemma STP_Accept_DoseReductionTargetMg_EdoxabanCiclosporin()
  ensures DoseReductionTargetMg(Edoxaban, Ciclosporin, AFStrokePrevention) == 30
{}

lemma STP_Accept_DoseReductionTargetMg_DabigatranVerapamil()
  ensures DoseReductionTargetMg(Dabigatran, Verapamil, AFStrokePrevention) == 110
{}

// REJECT: guards against the real authoring mistake this two-DOAC,
// two-figure function invites -- swapping which constant belongs to
// which DOAC. 110 is real (Dabigatran+Verapamil), but wrong for this
// cell; proves it's genuinely excluded, not just absent from the match
// arm by coincidence.
lemma STP_Reject_DoseReductionTargetMg_EdoxabanCiclosporin_Not110()
  requires DoseReductionTargetMg(Edoxaban, Ciclosporin, AFStrokePrevention) == 110 // wrong: real answer is 30, dabigatran's figure not edoxaban's
  ensures false
{}

// REQ-DDI-6 EXTENDED 2026-07-13 (Gate C6 review, Finding 2):
// DoseReductionTargetMg's Dabigatran+Verapamil cell is now
// indication-scoped, matching the real source
// (sources/sps-doac-interactions-2024.md lines 57-65: "for AF-stroke-
// prevention and DVT/PE-prevention-and-treatment indications
// specifically"). Second ACCEPT lemma proves the other admitted
// indication gives the identical figure (both named indications get
// the same 110mg rule, confirmed against
// sources/emc-smpc-dabigatran-indications-2025.md), mirroring how
// REQ-DDI-5's own apixaban clauses get two ACCEPT lemmas, one per
// admitted indication, not just one.
lemma STP_Accept_DoseReductionTargetMg_DabigatranVerapamil_RecurrentVTEPrevention()
  ensures DoseReductionTargetMg(Dabigatran, Verapamil, RecurrentVTEPrevention) == 110
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

// Corrected 2026-07-13 (Qodo review, PR #40): OrthopaedicVTEProphylaxis
// (added for REQ-DDI-6's own scoping, a different cell entirely) made
// this cell silently callable with a third indication the interaction
// source never addresses for apixaban -- the match arm used to return
// Caution unconditionally, a real scope leak. Proves the fix: the same
// cell is now NotCovered for the orthopaedic indication, matching
// (Apixaban, Dronedarone)'s established silent-cell convention.
lemma STP_Accept_CheckInteraction_ApixabanRifampicin_OrthopaedicVTEProphylaxis_NotCovered(hasFlag: bool)
  ensures CheckInteraction(Apixaban, Rifampicin, hasFlag, OrthopaedicVTEProphylaxis) == InteractionResult(NotCovered, UnknownRisk)
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

// A sixth REJECT, specific to the 2026-07-13 Qodo-review fix: before
// this fix, OrthopaedicVTEProphylaxis silently fell through to the same
// Caution the two named indications get, since the match arm never
// inspected treatmentIndication at all. Proves that regression is now
// genuinely excluded, not just replaced by a comment.
lemma STP_Reject_CheckInteraction_ApixabanRifampicin_OrthopaedicVTEProphylaxis_NotCaution(hasFlag: bool)
  requires CheckInteraction(Apixaban, Rifampicin, hasFlag, OrthopaedicVTEProphylaxis) == InteractionResult(Caution, ThrombosisRisk) // wrong: was the pre-fix scope-leak default
  ensures false
{}

// ============================================== Domain-coherence lemma

// Gate C6 review, Fix 2B (2026-07-13, nl_confirmation_drug_interaction_
// checker_dfy.md's "Addendum 3"): proves DoseReductionTargetMg's
// precondition domain EXACTLY equals "CheckInteraction says
// DoseReductionAdvised" minus the two known, deliberate exclusions --
// not asserted by grep against the real spec (the review's own original
// wording), a real theorem instead. Self-maintaining: adding a new
// DoseReductionAdvised cell to CheckInteraction, or a new pinned figure
// to DoseReductionTargetMg, without updating the other, breaks this
// lemma's own verification -- nothing else in this suite would catch
// that drift.
//
// A real, caught mistake while building this, not smoothed over: the
// review's own proposed lemma text (before the third
// TreatmentIndication constructor and its indication guard on the
// Dabigatran+Verapamil requires clause existed) omitted the third
// conjunct below -- and would NOT verify once that guard was added.
// CheckInteraction's own (Dabigatran, Verapamil) ensures clause claims
// DoseReductionAdvised unconditionally, for every TreatmentIndication
// value including OrthopaedicVTEProphylaxis (the OUTCOME KIND doesn't
// depend on indication -- verapamil interacts with dabigatran
// regardless of what it's prescribed for); only the exact MG FIGURE is
// indication-scoped. Confirmed by hand-deriving and independently
// verifying a standalone probe before editing this file, not assumed
// from the review's text transferring unchanged.
lemma DoseTargetDomainAgreesWithCheckInteraction(doac: DOAC, agent: Agent, f: bool, ti: TreatmentIndication)
  ensures (CheckInteraction(doac, agent, f, ti).outcome == DoseReductionAdvised
           && !(doac == Dabigatran && agent == SSRIOrSNRI)
           && !(doac == Dabigatran && agent == Verapamil && ti == OrthopaedicVTEProphylaxis))
      <==> ((doac == Dabigatran && agent == Verapamil && (ti == AFStrokePrevention || ti == RecurrentVTEPrevention))
         || (doac == Edoxaban && (agent == Dronedarone || agent == ErythromycinSystemic || agent == Ketoconazole || agent == Ciclosporin)))
{}
