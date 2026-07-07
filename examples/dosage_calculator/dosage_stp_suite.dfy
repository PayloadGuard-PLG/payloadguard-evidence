// Phase C, Gate C4: Spec-Testing Proofs (IronSpec methodology) for the
// FIXED dosage.dfy spec.
//
// An STP proves that a specific, manually chosen (input, output) pair is
// ACCEPTED or REJECTED by the SPECIFICATION ITSELF - the requires/ensures
// clauses, taken as a logical predicate - independent of whether any
// implementation is ever called. This is the direct, mechanized version
// of the review Gate 1 did by hand for REQ-GIP-1-4-12 (finding the
// original Python/CrossHair spec only encoded clamping, not the "shall
// trigger an alarm" text): an STP would have caught that gap
// mechanically. Applied to this repo's own new Dafny spec, it caught a
// DIFFERENT instance of the same bug class - see dosage.dfy's header
// comment and dosage_underconstrained.dfy for the finding and fix.
//
// Three logically distinct branches of CalculateHourlyDose are each
// tested with one ACCEPT lemma (the correct value is provably forced by
// the spec) and, where a real gap existed before the fix, one REJECT
// lemma (a wrong candidate value is provably EXCLUDED by the spec - i.e.
// assuming it holds leads to a proved contradiction, `ensures false`):
//
//   1. Normal in-range case (rawDose within [0, max])
//   2. Ceiling-clamped case (rawDose > max)
//   3. Reverse-flow case (rawDose < 0)
//
// All lemmas below verify cleanly against this file's `include`d,
// FIXED dosage.dfy - confirmed for real
// (run_verify_dafny_stp_suite.py). The same REJECT lemmas for cases 1
// and 2, run instead against the preserved original weak spec, FAIL to
// verify - see dosage_stp_suite_against_underconstrained.dfy. Case 3 has
// no REJECT lemma against the weak spec because it was never a gap: the
// weak spec's own `infusionRateMlPerHr >= 0.0 || dose == 0.0` clause
// already pins dose to exactly 0 whenever the rate is negative, with no
// help from ExpectedDose needed.

include "dosage.dfy"

// --- Case 1: normal in-range (rawDose = 5.0 * 2.0 = 10.0, within [0,100]) ---

lemma STP_Accept_NormalCase(dose: real)
  requires dose == ExpectedDose(2.0, 5.0, 100.0)
  requires 0.0 <= dose <= 100.0
  requires 5.0 >= 0.0 || dose == 0.0
  ensures dose == 10.0
{}

lemma STP_Reject_NormalCase_WrongValueExcluded(dose: real)
  requires dose == ExpectedDose(2.0, 5.0, 100.0)
  requires 0.0 <= dose <= 100.0
  requires 5.0 >= 0.0 || dose == 0.0
  requires dose == 0.0 // wrong: the real answer is 10.0, not 0.0
  ensures false
{}

// --- Case 2: ceiling-clamped (rawDose = 10.0 * 50.0 = 500.0 > max = 100.0) ---

lemma STP_Accept_CeilingClampedCase(dose: real)
  requires dose == ExpectedDose(50.0, 10.0, 100.0)
  requires 0.0 <= dose <= 100.0
  requires 10.0 >= 0.0 || dose == 0.0
  ensures dose == 100.0
{}

lemma STP_Reject_CeilingClampedCase_WrongValueExcluded(dose: real)
  requires dose == ExpectedDose(50.0, 10.0, 100.0)
  requires 0.0 <= dose <= 100.0
  requires 10.0 >= 0.0 || dose == 0.0
  requires dose == 50.0 // wrong but still in-bounds: the true answer is
                        // 100.0 (the ceiling), not an arbitrary in-range
                        // value - deliberately NOT the raw unclamped
                        // product (500.0), which the weak spec's own
                        // 0<=dose<=max bound already excludes trivially
                        // and so would not test the actual gap (verified
                        // empirically - see
                        // dosage_stp_suite_against_underconstrained.dfy)
  ensures false
{}

// --- Case 3: reverse flow (rate = -5.0 < 0, so dose must be exactly 0) ---

lemma STP_Accept_ReverseFlowCase(dose: real)
  requires dose == ExpectedDose(2.0, -5.0, 100.0)
  requires 0.0 <= dose <= 100.0
  requires -5.0 >= 0.0 || dose == 0.0
  ensures dose == 0.0
{}
