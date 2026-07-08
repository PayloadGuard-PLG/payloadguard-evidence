// Phase 2, Gate C4: the "before" half of the STP proof for
// renal_adjustment.dfy, mirroring
// dosage_stp_suite_against_underconstrained.dfy's exact discipline.
//
// Same four REJECT lemmas as renal_adjustment_stp_suite.dfy's
// ComposedCeiling and AssessRenalFunction sections, but included against
// the PRESERVED ORIGINAL under-constrained spec
// (renal_adjustment_underconstrained.dfy) instead of the fixed one. All
// four lemmas below are expected to FAIL to verify - confirmed for real
// (run_verify_dafny_stp_suite_against_underconstrained_renal.py) -
// because the original ensures clauses only bounded the results, never
// pinned them to the actual computed value, so a wrong candidate value
// cannot be excluded.
//
// This file's real, committed capture is a genuinely FAILING one -
// exit_code != 0, same discipline as dosage_broken.dfy and
// dosage_stp_suite_against_underconstrained.dfy: a deliberately negative
// result, verbatim, not smoothed over, proving the STP methodology
// actually distinguishes a real gap from a non-issue rather than always
// reporting success.

include "renal_adjustment_underconstrained.dfy"

lemma STP_Reject_ComposedCeiling_RenalMoreConservative_WrongValueExcluded(c: real)
  requires c <= 10.0
  requires c <= 6.0
  requires c == 0.0 // wrong: the true answer is 6.0
  ensures false
{}

lemma STP_Reject_ComposedCeiling_ExistingMoreConservative_WrongValueExcluded(c: real)
  requires c <= 6.0
  requires c <= 10.0
  requires c == 0.0 // wrong: the true answer is 6.0
  ensures false
{}

lemma STP_Reject_AssessRenalFunction_EgfrPath_WrongStageExcluded(r: RenalAssessment)
  requires EGFRFormula == EGFRFormula ==> r.EGFRAssessment?
  requires EGFRFormula == CockcroftGaultFormula ==> r.CrClAssessment?
  requires r == EGFRAssessment(G1) // wrong: NHS SPS eGFR 53.0 stages to
                                    // G3a, not G1
  ensures false
{}

lemma STP_Reject_AssessRenalFunction_CrClPath_WrongValueExcluded(r: RenalAssessment)
  requires CockcroftGaultFormula == EGFRFormula ==> r.EGFRAssessment?
  requires CockcroftGaultFormula == CockcroftGaultFormula ==> r.CrClAssessment?
  requires r == CrClAssessment(1) // wrong: NHS SPS Cockcroft-Gault CrCl
                                   // 36.9 rounds to 37, not 1
  ensures false
{}
