// Probe: can Dafny/Z3 express CKD-EPI's fractional-exponent term at all?
// Shape: min(Scr/kappa, 1)^alpha  where alpha is a real, non-integer constant.
function CkdEpiPowerTerm(scr: real, kappa: real, alpha: real): real
  requires scr > 0.0
  requires kappa > 0.0
{
  var ratio := if scr / kappa < 1.0 then scr / kappa else 1.0;
  Pow(ratio, alpha)
}
