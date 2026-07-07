// Phase C, Gate C4: the "before" half of the STP proof. Same REJECT
// lemmas as dosage_stp_suite.dfy's Case 1 and Case 2, but included
// against the PRESERVED ORIGINAL weak spec (dosage_underconstrained.dfy)
// instead of the fixed one. Both lemmas below are expected to FAIL to
// verify - confirmed for real
// (run_verify_dafny_stp_suite_against_underconstrained.py) - because the
// weak spec's ensures clauses only bound `dose`, never pinned it to the
// actual clamped product, so a wrong candidate value cannot be excluded.
//
// No Case 3 (reverse-flow) lemma here: that branch was never a gap, even
// in the weak spec - `infusionRateMlPerHr >= 0.0 || dose == 0.0` already
// forces dose to exactly 0 whenever the rate is negative.
//
// This file's real, committed capture is a genuinely FAILING one -
// exit_code != 0, same discipline as dosage_broken.dfy: a deliberately
// negative result, verbatim, not smoothed over, proving the STP
// methodology actually distinguishes a tight spec from a loose one
// rather than passing regardless.

include "dosage_underconstrained.dfy"

lemma STP_Reject_NormalCase_WrongValueExcluded(dose: real)
  requires 0.0 <= dose <= 100.0
  requires 5.0 >= 0.0 || dose == 0.0
  requires dose == 0.0 // wrong: the real answer is 10.0, not 0.0 - but
                       // this weak spec cannot prove that
  ensures false
{}

lemma STP_Reject_CeilingClampedCase_WrongValueExcluded(dose: real)
  requires 0.0 <= dose <= 100.0
  requires 10.0 >= 0.0 || dose == 0.0
  requires dose == 50.0 // wrong but still in-bounds: the true answer is
                        // 100.0 (the ceiling). Deliberately NOT the raw
                        // unclamped product (500.0), which the weak
                        // spec's own 0<=dose<=max bound already excludes
                        // trivially - that would not test the actual gap
                        // (confirmed empirically: 500.0 alone made this
                        // lemma verify even against the weak spec, for
                        // the wrong reason - caught and corrected before
                        // committing)
  ensures false
{}
