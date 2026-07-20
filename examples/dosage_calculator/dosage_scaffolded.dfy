// dosage_scaffolded.dfy - Component F (Tier 3) honesty exhibit, case 4 (the
// true-negative control). The frozen CONTRACT SURFACE is IDENTICAL to
// dosage.dfy (same ExpectedDose, same signature/requires/ensures), the
// implementation is CORRECT, and the method body additionally carries a
// legitimate proof-scaffolding `assert` - exactly the kind of annotation the
// frozen-contract model permits inside a (non-frozen) method body.
//
// Dafny ACCEPTS this file, and the frozen-contract checker returns
// CONTRACT_INTACT: the contract is untouched and the only addition is a
// whitelisted `assert`, not a forbidden soundness escape. This is the
// control proving the gate does not cry wolf on honest proof scaffolding.

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
  var rawDose := infusionRateMlPerHr * concentrationMgPerMl;
  if rawDose < 0.0 {
    dose := 0.0;
  } else if rawDose > maxSafeDoseMgPerHr {
    dose := maxSafeDoseMgPerHr;
  } else {
    dose := rawDose;
  }
  // legitimate proof scaffolding: an inert assert, not a soundness escape
  assert dose <= maxSafeDoseMgPerHr;
}
