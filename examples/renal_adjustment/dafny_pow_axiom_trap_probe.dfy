// Second probe: the workaround someone might reach for -- declare Pow as
// an axiom instead of a computed function. Confirms WHY this isn't a real
// fix: Dafny reports "verified" for an axiom trivially (no body to prove
// anything about), which is a DECLARED claim wearing PROVEN's clothing --
// exactly what Gate C2 (assert_no_realized_proven) exists to catch
// downstream, but this shows the trap exists even earlier, at the spec
// level, before any matrix is ever built.
function {:axiom} Pow(base: real, exp: real): real

function CkdEpiPowerTerm(scr: real, kappa: real, alpha: real): real
  requires scr > 0.0
  requires kappa > 0.0
{
  var ratio := if scr / kappa < 1.0 then scr / kappa else 1.0;
  Pow(ratio, alpha)
}

// The trap: this "verifies" too, but proves NOTHING about the actual
// numeric behavior of Pow -- an axiom this permissive is equally
// consistent with Pow always returning 0.0, an absurd, wrong claim.
lemma {:axiom} AxiomProvesNothingUseful(scr: real, kappa: real, alpha: real)
  requires scr > 0.0 && kappa > 0.0
  ensures CkdEpiPowerTerm(scr, kappa, alpha) == 0.0
