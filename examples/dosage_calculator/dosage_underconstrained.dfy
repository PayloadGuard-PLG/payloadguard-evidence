// Preserved review artifact — Gate C4 (Phase C) honesty exhibit, same
// rationale as dosage_naive_widening.py: this is Gate C1's ORIGINAL
// CalculateHourlyDose spec, byte-for-byte, kept exactly as it was first
// verified and committed, before Gate C4's Spec-Testing Proofs (STPs)
// found it under-constrained.
//
// THE GAP, confirmed mechanically, not by inspection alone: these two
// ensures clauses bound `dose` to [0, maxSafeDoseMgPerHr] and force it to
// 0 on reverse flow, but never relate `dose` to the actual product
// `infusionRateMlPerHr * concentrationMgPerMl` in the normal and
// ceiling-clamped cases. A method that always returned, say, 0.0 for
// every non-negative-rate input would satisfy this exact spec just as
// well as the real clamping implementation does — Dafny's own clean pass
// on this method proves boundedness and reverse-flow-zeroing, nothing
// about correctness of the computed dose otherwise. See
// dosage_stp_suite_against_underconstrained.dfy for the mechanized
// proof: two Spec-Testing Proof lemmas that try to exclude a wrong
// candidate dose value for the normal and ceiling-clamped cases, and
// FAIL to verify against this spec (confirmed for real, not asserted) -
// the same two lemmas succeed against the fixed dosage.dfy, which adds
// an ExpectedDose function and a pinning ensures clause. The
// reverse-flow case has no such gap even here: `infusionRateMlPerHr >=
// 0.0 || dose == 0.0` already forces dose to exactly 0 whenever the rate
// is negative, with no help from a pinning function needed.
//
// This file is verified standalone for real
// (run_verify_dafny_underconstrained.py) and still passes cleanly - the
// bug is a spec weakness, not a verification failure, which is exactly
// why STPs are a distinct check from "does it verify."

method CalculateHourlyDose(
  concentrationMgPerMl: real,
  infusionRateMlPerHr: real,
  maxSafeDoseMgPerHr: real
) returns (dose: real)
  requires concentrationMgPerMl > 0.0
  requires maxSafeDoseMgPerHr > 0.0
  ensures 0.0 <= dose <= maxSafeDoseMgPerHr        // REQ-GIP-1-4-12, kernel_scope
  ensures infusionRateMlPerHr >= 0.0 || dose == 0.0 // REQ-GIP-1-8-1
{
  var rawDose := infusionRateMlPerHr * concentrationMgPerMl;
  if rawDose < 0.0 {
    dose := 0.0;
  } else if rawDose > maxSafeDoseMgPerHr {
    dose := maxSafeDoseMgPerHr;
  } else {
    dose := rawDose;
  }
}
