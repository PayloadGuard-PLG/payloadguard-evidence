// dosage_assume_escape.dfy - Component F (Tier 3) honesty exhibit, case 3.
//
// The frozen CONTRACT SURFACE here is IDENTICAL to dosage.dfy: the same
// ExpectedDose function (byte-for-byte), the same CalculateHourlyDose
// signature, the same two requires and the same three ensures. What differs
// is only the method BODY (which the frozen contract does NOT freeze - it is
// the implementation, where proof scaffolding legitimately lives): the
// implementation is WRONG (it never clamps), and an `assume false;` forces
// Dafny to discharge all three postconditions vacuously.
//
// Dafny's VERIFIER ACCEPTS this file: it reports "2 verified, 0 errors" (see
// raw_dafny_output_assume_escape.txt) - `assume false` discharges every
// postcondition vacuously. Dafny does, by default, also emit a soundness
// WARNING on the assume and exit non-zero; but `dafny verify --allow-warnings`
// (a single, common flag) suppresses that warning to a clean exit-0
// "2 verified, 0 errors", indistinguishable from an honest pass at the
// capture level. So the warning is not a robust guard. The frozen-contract
// checker (evidence/frozen_contract.py) REJECTS this file either way - not on
// the contract surface, which is pristine, but on the forbidden `assume`
// construct a drafter must never introduce. This is the case the
// contract-surface diff alone cannot see, and the reason the checker also
// scans for soundness escapes. Preserved as an exhibit, same discipline as
// dosage_underconstrained.dfy / dosage_naive_widening.py.

function ExpectedDose(
  concentrationMgPerMl: real,
  infusionRateMlPerHr: real,
  maxSafeDoseMgPerHr: real
): real
  requires concentrationMgPerMl > 0.0
  requires maxSafeDoseMgPerHr > 0.0
{
  var rawDose := infusionRateMlPerHr * concentrationMgPerMl;
  if rawDose < 0.0 then 0.0
  else if rawDose > maxSafeDoseMgPerHr then maxSafeDoseMgPerHr
  else rawDose
}

method CalculateHourlyDose(
  concentrationMgPerMl: real,
  infusionRateMlPerHr: real,
  maxSafeDoseMgPerHr: real
) returns (dose: real)
  requires concentrationMgPerMl > 0.0
  requires maxSafeDoseMgPerHr > 0.0
  ensures dose == ExpectedDose(concentrationMgPerMl, infusionRateMlPerHr, maxSafeDoseMgPerHr)
  ensures 0.0 <= dose <= maxSafeDoseMgPerHr        // REQ-GIP-1-4-12, kernel_scope
  ensures infusionRateMlPerHr > 0.0 || dose == 0.0  // REQ-GIP-1-8-1
{
  // WRONG: no clamp - would violate all three postconditions above.
  dose := infusionRateMlPerHr * concentrationMgPerMl;
  assume false; // soundness escape: forces Dafny to accept the wrong result
}
