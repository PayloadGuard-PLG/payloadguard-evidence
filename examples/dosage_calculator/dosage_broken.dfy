// Deliberately broken Dafny variant (Sample B equivalent for Gate C1):
// the clamp is removed, so both postconditions are violated whenever
// rawDose exceeds maxSafeDoseMgPerHr or is negative. Exists only to prove
// the capture mechanism actually detects a real failure, not just that it
// can print a success message. Mirrors dosage_broken.py's role for the
// CrossHair captures (Sample B).

method CalculateHourlyDose(
  concentrationMgPerMl: real,
  infusionRateMlPerHr: real,
  maxSafeDoseMgPerHr: real
) returns (dose: real)
  requires concentrationMgPerMl > 0.0
  requires maxSafeDoseMgPerHr > 0.0
  ensures 0.0 <= dose <= maxSafeDoseMgPerHr
  ensures infusionRateMlPerHr >= 0.0 || dose == 0.0
{
  dose := infusionRateMlPerHr * concentrationMgPerMl;
}
