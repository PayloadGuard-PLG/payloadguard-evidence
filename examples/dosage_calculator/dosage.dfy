// Dafny translation of dosage.py's clamping kernel — Gate C1 (Phase C).
//
// SCOPE, NAMED EXPLICITLY: this spec covers REQ-GIP-1-4-12 (kernel_scope:
// dose never exceeds the safe ceiling) and REQ-GIP-1-8-1 (reverse
// delivery yields exactly zero) ONLY.
//
// REQ-DOSE-003 (finite, in-range result under floating-point overflow) is
// NOT covered here, and cannot be: Dafny's `real` type is exact,
// arbitrary-precision mathematical real arithmetic with no overflow, no
// infinity, no NaN. Confirmed empirically (2026-07-06), not assumed:
// `y := x / 0.0` on `real` is flagged as a verification ERROR
// ("possible division by zero") in this installed Dafny (4.11.0) — real
// division by zero is disallowed, not a silent IEEE inf. A Dafny "proof"
// of finiteness would therefore be true of a model that cannot even
// represent the phenomenon REQ-DOSE-003 is about (IEEE-754 overflow to
// +-inf on `raw_dose = infusion_rate_ml_per_hr * concentration_mg_per_ml`
// when both are large). Claiming PROVEN for REQ-DOSE-003 via this spec
// would be exactly the false-zero-shaped mistake this repo's Sample C /
// overflow_probe.py honesty exhibits exist to prevent. CrossHair's
// BOUNDED_CHECKED evidence remains the only meaningful evidence for
// REQ-DOSE-003; nothing here changes that.
//
// weight_kg is intentionally omitted: in dosage.py it is an unused
// precondition-only guard (reserved for a future weight-based ceiling),
// never referenced by either postcondition — dropping it changes nothing
// about what is or isn't proved.
//
// Gate C4 finding and fix (2026-07-07): the ORIGINAL two ensures clauses
// below (bounds + reverse-flow-zero) verified cleanly but never pinned
// `dose` to the actual clamped product of rate and concentration — a
// method that always returned 0.0 for any non-negative rate would have
// satisfied that spec too. Confirmed mechanically, not by inspection: a
// Spec-Testing Proof (IronSpec methodology) trying to prove a wrong
// candidate dose value impossible FAILED to verify against the original
// spec, and SUCCEEDS against this fixed one. The original is preserved
// verbatim as dosage_underconstrained.dfy (an honesty exhibit, same
// rationale as dosage_naive_widening.py); the STP suites proving both
// directions are dosage_stp_suite.dfy (passes against this fixed spec)
// and dosage_stp_suite_against_underconstrained.dfy (fails against the
// preserved original). ExpectedDose below is the fix: a function
// computing the exact clamped value, referenced by a new ensures clause
// that pins `dose` to it exactly — the two original ensures clauses stay,
// unchanged, for direct per-requirement traceability (REQ-GIP-1-4-12,
// REQ-GIP-1-8-1), now implied by (not contradicting) the pinning clause.
//
// Gate C5 finding and fix (2026-07-07): mutation testing found the
// REQ-GIP-1-8-1 clause's `>=` was not independently load-bearing at
// infusionRateMlPerHr == 0.0 exactly — real multiplication by exactly
// 0.0 already forces dose == 0.0 there via the second disjunct, so
// `>=`, `!=`, and `>` all verified identically at that boundary
// (mutation-testing survivors, examples/dosage_calculator/mutation_report.md).
// Tightened to `>` on Steven's explicit decision, re-verified clean, and
// re-run through the mutation suite to confirm the survivor is now
// killed. See examples/dosage_calculator/nl_confirmation_dosage_dfy.md's
// amendment for the post-change re-confirmation.

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
}
