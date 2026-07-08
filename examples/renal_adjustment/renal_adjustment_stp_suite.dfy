// Phase 2, Gate C4: Spec-Testing Proofs (IronSpec methodology) for
// renal_adjustment.dfy, mirroring dosage_stp_suite.dfy's discipline
// exactly - see gate_c4_stp_plan.md for the full scoping and
// hand-derived predictions this suite tests.
//
// Each lemma restates a function's ACTUAL declared ensures clause(s) as
// `requires` premises on a fresh hypothetical output value, then proves
// either the correct value is forced (ACCEPT) or a wrong candidate value
// is provably excluded (REJECT, `ensures false`) - testing the
// SPECIFICATION alone, independent of the function body ever being
// evaluated.

include "renal_adjustment.dfy"

// ============================================================ RoundHalfUp

// General structural lemma: the postcondition alone forces a UNIQUE
// integer per x - the half-open intervals [n-0.5, n+0.5) tile the reals
// with no gap and no overlap. Predicted (gate_c4_stp_plan.md): verifies.
lemma STP_RoundHalfUp_Uniqueness(x: real, n1: int, n2: int)
  requires x >= 0.0
  requires (n1 as real) - 0.5 <= x < (n1 as real) + 0.5
  requires (n2 as real) - 0.5 <= x < (n2 as real) + 0.5
  ensures n1 == n2
{}

// Rows 2-6 of the 16-row table (boundary ties and just-under values),
// plus row 1's two values (NHS SPS: eGFR 53.0, CrCl 36.9).
lemma STP_Accept_RoundHalfUp_89_5(n: int)
  requires (n as real) - 0.5 <= 89.5 < (n as real) + 0.5
  ensures n == 90
{}

lemma STP_Accept_RoundHalfUp_89_499999(n: int)
  requires (n as real) - 0.5 <= 89.499999 < (n as real) + 0.5
  ensures n == 89
{}

lemma STP_Accept_RoundHalfUp_59_5(n: int)
  requires (n as real) - 0.5 <= 59.5 < (n as real) + 0.5
  ensures n == 60
{}

lemma STP_Accept_RoundHalfUp_59_499999(n: int)
  requires (n as real) - 0.5 <= 59.499999 < (n as real) + 0.5
  ensures n == 59
{}

lemma STP_Accept_RoundHalfUp_44_5(n: int)
  requires (n as real) - 0.5 <= 44.5 < (n as real) + 0.5
  ensures n == 45
{}

lemma STP_Accept_RoundHalfUp_44_499999(n: int)
  requires (n as real) - 0.5 <= 44.499999 < (n as real) + 0.5
  ensures n == 44
{}

lemma STP_Accept_RoundHalfUp_29_5(n: int)
  requires (n as real) - 0.5 <= 29.5 < (n as real) + 0.5
  ensures n == 30
{}

lemma STP_Accept_RoundHalfUp_29_499999(n: int)
  requires (n as real) - 0.5 <= 29.499999 < (n as real) + 0.5
  ensures n == 29
{}

lemma STP_Accept_RoundHalfUp_14_5(n: int)
  requires (n as real) - 0.5 <= 14.5 < (n as real) + 0.5
  ensures n == 15
{}

lemma STP_Accept_RoundHalfUp_14_499999(n: int)
  requires (n as real) - 0.5 <= 14.499999 < (n as real) + 0.5
  ensures n == 14
{}

lemma STP_Accept_RoundHalfUp_NhsSps_Egfr_53(n: int)
  requires (n as real) - 0.5 <= 53.0 < (n as real) + 0.5
  ensures n == 53
{}

lemma STP_Accept_RoundHalfUp_NhsSps_CrCl_36_9(n: int)
  requires (n as real) - 0.5 <= 36.9 < (n as real) + 0.5
  ensures n == 37
{}

// ================================================================ GStage

// Totality: every non-negative roundedEgfr satisfies at least one of the
// six guards - no undefined-input region. Predicted: verifies.
lemma STP_GStage_Totality(roundedEgfr: int)
  requires roundedEgfr >= 0
  ensures roundedEgfr >= 90 || (60 <= roundedEgfr <= 89) || (45 <= roundedEgfr <= 59)
       || (30 <= roundedEgfr <= 44) || (15 <= roundedEgfr <= 29) || roundedEgfr < 15
{}

// Rows 2-6 (rounded values) plus the NHS SPS eGFR value.
lemma STP_Accept_GStage_90(g: GStageCategory)
  requires 90 >= 90 ==> g == G1
  requires (60 <= 90 <= 89) ==> g == G2
  requires (45 <= 90 <= 59) ==> g == G3a
  requires (30 <= 90 <= 44) ==> g == G3b
  requires (15 <= 90 <= 29) ==> g == G4
  requires 90 < 15 ==> g == G5
  ensures g == G1
{}

lemma STP_Accept_GStage_89(g: GStageCategory)
  requires 89 >= 90 ==> g == G1
  requires (60 <= 89 <= 89) ==> g == G2
  requires (45 <= 89 <= 59) ==> g == G3a
  requires (30 <= 89 <= 44) ==> g == G3b
  requires (15 <= 89 <= 29) ==> g == G4
  requires 89 < 15 ==> g == G5
  ensures g == G2
{}

lemma STP_Accept_GStage_60(g: GStageCategory)
  requires 60 >= 90 ==> g == G1
  requires (60 <= 60 <= 89) ==> g == G2
  requires (45 <= 60 <= 59) ==> g == G3a
  requires (30 <= 60 <= 44) ==> g == G3b
  requires (15 <= 60 <= 29) ==> g == G4
  requires 60 < 15 ==> g == G5
  ensures g == G2
{}

lemma STP_Accept_GStage_59(g: GStageCategory)
  requires 59 >= 90 ==> g == G1
  requires (60 <= 59 <= 89) ==> g == G2
  requires (45 <= 59 <= 59) ==> g == G3a
  requires (30 <= 59 <= 44) ==> g == G3b
  requires (15 <= 59 <= 29) ==> g == G4
  requires 59 < 15 ==> g == G5
  ensures g == G3a
{}

lemma STP_Accept_GStage_45(g: GStageCategory)
  requires 45 >= 90 ==> g == G1
  requires (60 <= 45 <= 89) ==> g == G2
  requires (45 <= 45 <= 59) ==> g == G3a
  requires (30 <= 45 <= 44) ==> g == G3b
  requires (15 <= 45 <= 29) ==> g == G4
  requires 45 < 15 ==> g == G5
  ensures g == G3a
{}

lemma STP_Accept_GStage_44(g: GStageCategory)
  requires 44 >= 90 ==> g == G1
  requires (60 <= 44 <= 89) ==> g == G2
  requires (45 <= 44 <= 59) ==> g == G3a
  requires (30 <= 44 <= 44) ==> g == G3b
  requires (15 <= 44 <= 29) ==> g == G4
  requires 44 < 15 ==> g == G5
  ensures g == G3b
{}

lemma STP_Accept_GStage_30(g: GStageCategory)
  requires 30 >= 90 ==> g == G1
  requires (60 <= 30 <= 89) ==> g == G2
  requires (45 <= 30 <= 59) ==> g == G3a
  requires (30 <= 30 <= 44) ==> g == G3b
  requires (15 <= 30 <= 29) ==> g == G4
  requires 30 < 15 ==> g == G5
  ensures g == G3b
{}

lemma STP_Accept_GStage_29(g: GStageCategory)
  requires 29 >= 90 ==> g == G1
  requires (60 <= 29 <= 89) ==> g == G2
  requires (45 <= 29 <= 59) ==> g == G3a
  requires (30 <= 29 <= 44) ==> g == G3b
  requires (15 <= 29 <= 29) ==> g == G4
  requires 29 < 15 ==> g == G5
  ensures g == G4
{}

lemma STP_Accept_GStage_15(g: GStageCategory)
  requires 15 >= 90 ==> g == G1
  requires (60 <= 15 <= 89) ==> g == G2
  requires (45 <= 15 <= 59) ==> g == G3a
  requires (30 <= 15 <= 44) ==> g == G3b
  requires (15 <= 15 <= 29) ==> g == G4
  requires 15 < 15 ==> g == G5
  ensures g == G4
{}

lemma STP_Accept_GStage_14(g: GStageCategory)
  requires 14 >= 90 ==> g == G1
  requires (60 <= 14 <= 89) ==> g == G2
  requires (45 <= 14 <= 59) ==> g == G3a
  requires (30 <= 14 <= 44) ==> g == G3b
  requires (15 <= 14 <= 29) ==> g == G4
  requires 14 < 15 ==> g == G5
  ensures g == G5
{}

lemma STP_Accept_GStage_NhsSps_Egfr_53(g: GStageCategory)
  requires 53 >= 90 ==> g == G1
  requires (60 <= 53 <= 89) ==> g == G2
  requires (45 <= 53 <= 59) ==> g == G3a
  requires (30 <= 53 <= 44) ==> g == G3b
  requires (15 <= 53 <= 29) ==> g == G4
  requires 53 < 15 ==> g == G5
  ensures g == G3a
{}

// ========================================================= SelectFormula

// Exhaustiveness/mutual-exclusivity: the two ensures clauses are exact
// negations of each other, so f is forced to exactly one of the two
// formulas for every input. Predicted: verifies.
lemma STP_SelectFormula_Exhaustive(
  anticoag: bool, nephro: bool, age: int, bmi: real, nti: bool, f: Formula
)
  requires age >= 0
  requires bmi > 0.0
  requires (anticoag || nephro || age >= 75 || bmi < 18.0 || bmi > 40.0 || nti) ==> f == CockcroftGaultFormula
  requires !(anticoag || nephro || age >= 75 || bmi < 18.0 || bmi > 40.0 || nti) ==> f == EGFRFormula
  ensures f == CockcroftGaultFormula || f == EGFRFormula
{}

// Rows 7-12: six branch cases from the 16-row table.
lemma STP_Accept_SelectFormula_Anticoagulant(f: Formula)
  requires (true || false || 40 >= 75 || 24.0 < 18.0 || 24.0 > 40.0 || false) ==> f == CockcroftGaultFormula
  requires !(true || false || 40 >= 75 || 24.0 < 18.0 || 24.0 > 40.0 || false) ==> f == EGFRFormula
  ensures f == CockcroftGaultFormula
{}

lemma STP_Accept_SelectFormula_Age75(f: Formula)
  requires (false || false || 75 >= 75 || 24.0 < 18.0 || 24.0 > 40.0 || false) ==> f == CockcroftGaultFormula
  requires !(false || false || 75 >= 75 || 24.0 < 18.0 || 24.0 > 40.0 || false) ==> f == EGFRFormula
  ensures f == CockcroftGaultFormula
{}

lemma STP_Accept_SelectFormula_Age74(f: Formula)
  requires (false || false || 74 >= 75 || 24.0 < 18.0 || 24.0 > 40.0 || false) ==> f == CockcroftGaultFormula
  requires !(false || false || 74 >= 75 || 24.0 < 18.0 || 24.0 > 40.0 || false) ==> f == EGFRFormula
  ensures f == EGFRFormula
{}

lemma STP_Accept_SelectFormula_BmiLow(f: Formula)
  requires (false || false || 40 >= 75 || 17.9 < 18.0 || 17.9 > 40.0 || false) ==> f == CockcroftGaultFormula
  requires !(false || false || 40 >= 75 || 17.9 < 18.0 || 17.9 > 40.0 || false) ==> f == EGFRFormula
  ensures f == CockcroftGaultFormula
{}

lemma STP_Accept_SelectFormula_BmiHigh(f: Formula)
  requires (false || false || 40 >= 75 || 40.1 < 18.0 || 40.1 > 40.0 || false) ==> f == CockcroftGaultFormula
  requires !(false || false || 40 >= 75 || 40.1 < 18.0 || 40.1 > 40.0 || false) ==> f == EGFRFormula
  ensures f == CockcroftGaultFormula
{}

lemma STP_Accept_SelectFormula_NoConditions(f: Formula)
  requires (false || false || 40 >= 75 || 24.0 < 18.0 || 24.0 > 40.0 || false) ==> f == CockcroftGaultFormula
  requires !(false || false || 40 >= 75 || 24.0 < 18.0 || 24.0 > 40.0 || false) ==> f == EGFRFormula
  ensures f == EGFRFormula
{}

// ======================================================= ComposedCeiling
//
// GATE C4 FINDING, CONFIRMED FOR REAL (not just predicted): run against
// renal_adjustment_underconstrained.dfy (the original, two-clause
// version), the REJECT lemmas below FAILED to verify - see
// renal_adjustment_stp_suite_against_underconstrained.dfy, a genuinely
// failing captured run (0 verified, 4 errors including this function's
// two). Fixed in renal_adjustment.dfy by adding a third pinning ensures
// clause. These lemmas restate all THREE of the function's current
// ensures clauses (not just the original two) - that third clause is
// exactly what makes the ACCEPT lemmas below provable and the REJECT
// lemmas correctly find a contradiction now.

lemma STP_Accept_ComposedCeiling_RenalMoreConservative(c: real)
  requires c <= 10.0
  requires c <= 6.0
  requires c == 10.0 || c == 6.0
  ensures c == 6.0
{}

lemma STP_Reject_ComposedCeiling_RenalMoreConservative_WrongValueExcluded(c: real)
  requires c <= 10.0
  requires c <= 6.0
  requires c == 10.0 || c == 6.0
  requires c == 0.0 // wrong: the true answer is 6.0 (the more
                    // conservative/smaller ceiling); now excluded by
                    // the third (pinning) ensures clause, which forces
                    // c to be one of the two inputs, not an arbitrary
                    // value satisfying just the two <= bounds
  ensures false
{}

lemma STP_Accept_ComposedCeiling_ExistingMoreConservative(c: real)
  requires c <= 6.0
  requires c <= 10.0
  requires c == 6.0 || c == 10.0
  ensures c == 6.0
{}

lemma STP_Reject_ComposedCeiling_ExistingMoreConservative_WrongValueExcluded(c: real)
  requires c <= 6.0
  requires c <= 10.0
  requires c == 6.0 || c == 10.0
  requires c == 0.0 // wrong: the true answer is 6.0
  ensures false
{}

// ==================================================== AssessRenalFunction
//
// GATE C4 FINDING, CONFIRMED FOR REAL (not just predicted): run against
// renal_adjustment_underconstrained.dfy, the REJECT lemmas below FAILED
// to verify - see renal_adjustment_stp_suite_against_underconstrained.dfy.
// Fixed in renal_adjustment.dfy by adding two pinning ensures clauses
// (one per formula branch). These lemmas restate all FOUR of the
// function's current ensures clauses.

lemma STP_Accept_AssessRenalFunction_EgfrPath_NhsSps(r: RenalAssessment)
  requires EGFRFormula == EGFRFormula ==> r.EGFRAssessment?
  requires EGFRFormula == CockcroftGaultFormula ==> r.CrClAssessment?
  requires EGFRFormula == EGFRFormula ==> r == EGFRAssessment(GStage(RoundHalfUp(53.0)))
  requires EGFRFormula == CockcroftGaultFormula ==> r == CrClAssessment(RoundHalfUp(53.0))
  ensures r == EGFRAssessment(G3a)
{}

lemma STP_Reject_AssessRenalFunction_EgfrPath_WrongStageExcluded(r: RenalAssessment)
  requires EGFRFormula == EGFRFormula ==> r.EGFRAssessment?
  requires EGFRFormula == CockcroftGaultFormula ==> r.CrClAssessment?
  requires EGFRFormula == EGFRFormula ==> r == EGFRAssessment(GStage(RoundHalfUp(53.0)))
  requires EGFRFormula == CockcroftGaultFormula ==> r == CrClAssessment(RoundHalfUp(53.0))
  requires r == EGFRAssessment(G1) // wrong: NHS SPS eGFR 53.0 stages to
                                    // G3a, not G1; now excluded by the
                                    // pinning clause referencing
                                    // GStage(RoundHalfUp(...)) directly
  ensures false
{}

lemma STP_Accept_AssessRenalFunction_CrClPath_NhsSps(r: RenalAssessment)
  requires CockcroftGaultFormula == EGFRFormula ==> r.EGFRAssessment?
  requires CockcroftGaultFormula == CockcroftGaultFormula ==> r.CrClAssessment?
  requires CockcroftGaultFormula == EGFRFormula ==> r == EGFRAssessment(GStage(RoundHalfUp(36.9)))
  requires CockcroftGaultFormula == CockcroftGaultFormula ==> r == CrClAssessment(RoundHalfUp(36.9))
  ensures r == CrClAssessment(37)
{}

lemma STP_Reject_AssessRenalFunction_CrClPath_WrongValueExcluded(r: RenalAssessment)
  requires CockcroftGaultFormula == EGFRFormula ==> r.EGFRAssessment?
  requires CockcroftGaultFormula == CockcroftGaultFormula ==> r.CrClAssessment?
  requires CockcroftGaultFormula == EGFRFormula ==> r == EGFRAssessment(GStage(RoundHalfUp(36.9)))
  requires CockcroftGaultFormula == CockcroftGaultFormula ==> r == CrClAssessment(RoundHalfUp(36.9))
  requires r == CrClAssessment(1) // wrong: NHS SPS Cockcroft-Gault CrCl
                                   // 36.9 rounds to 37, not 1; now
                                   // excluded by the pinning clause
  ensures false
{}
