# Gate C4 plan: Spec-Testing Proofs for `renal_adjustment.dfy`

Status: **plan only, not built.** Per this repo's standing discipline
("scope out X" produces a written plan first, built on explicit
follow-up instruction), this document scopes Gate C4 before writing
`renal_adjustment_stp_suite.dfy`. Nothing in `renal_adjustment.dfy`
itself has changed.

## What an STP actually tests, and why it matters here specifically

An STP (IronSpec methodology, per `dosage_stp_suite.dfy`'s header)
proves that a manually chosen `(input, output)` pair is ACCEPTED or
REJECTED by the **specification itself** — the `requires`/`ensures`
clauses as a logical predicate — independent of whether the function's
own body is ever consulted. `dosage.dfy`'s own Gate C4 history is the
reason this matters: the original spec's postconditions (bounds +
reverse-flow-zero) verified cleanly against the real implementation, but
a REJECT lemma trying to prove a *wrong* candidate dose value impossible
**failed** — the postconditions bounded `dose`, they never pinned it to
the exact clamped value, so a broken implementation could have satisfied
the same spec undetected. Fixed by adding an `ExpectedDose` pinning
clause. This is exactly the class of defect Gate C4 exists to catch
mechanically, and it's a real, precedented risk for this second POC too,
not a hypothetical one being invoked for form's sake.

## Two predicted gaps, hand-derived before building (hypothesis, not a promise — per the LVR extension's precedent)

Read through all five functions' `ensures` clauses specifically asking
"does this pin the exact output, or only bound/shape it?" before writing
a single STP lemma. Two real, predictable gaps stood out:

### Predicted gap 1: `ComposedCeiling` is almost certainly under-constrained

```dafny
ensures ComposedCeiling(existingCeiling, renalCeiling) <= existingCeiling
ensures ComposedCeiling(existingCeiling, renalCeiling) <= renalCeiling
```

These two `<=` bounds do **not** force the result to equal
`min(existingCeiling, renalCeiling)`. A hypothetical alternative
implementation that always returns, say, `0.0` (or any value `<=` both
inputs) would satisfy both `ensures` clauses just as well as the real
`if renalCeiling < existingCeiling then renalCeiling else existingCeiling`
body does. **Prediction: a REJECT lemma attempting to prove
`ComposedCeiling(10.0, 6.0) != 0.0` impossible will fail to verify** —
the spec doesn't exclude it. This is the same shape of bug as
`dosage.dfy`'s original gap, on the one function in this spec that most
resembles `CalculateHourlyDose`'s bound-only postcondition style.

**Predicted fix, not yet applied:** add a pinning clause, e.g.
`ensures ComposedCeiling(existingCeiling, renalCeiling) == existingCeiling || ComposedCeiling(existingCeiling, renalCeiling) == renalCeiling`
— combined with the two existing `<=` bounds, this forces the result to
be exactly `min(existingCeiling, renalCeiling)`, the same pattern
`dosage.dfy` used (`ExpectedDose`-style exact-value pinning, not a
separate helper function needed here since the two disjuncts plus the
bounds are sufficient).

### Predicted gap 2: `AssessRenalFunction` pins the variant, not the value

```dafny
ensures formula == EGFRFormula ==> AssessRenalFunction(formula, renalFunctionValue).EGFRAssessment?
ensures formula == CockcroftGaultFormula ==> AssessRenalFunction(formula, renalFunctionValue).CrClAssessment?
```

These only constrain *which constructor* the result uses (`.EGFRAssessment?`
vs. `.CrClAssessment?`) — Gate 1c Finding 2's actual target, and they do
that correctly. But neither clause constrains the *value inside* the
constructor. **Prediction: a REJECT lemma attempting to prove
`AssessRenalFunction(EGFRFormula, 53.0) != EGFRAssessment(G1)` (a wrong
stage) impossible will fail to verify** — an alternative implementation
that always returns `EGFRAssessment(G1)` regardless of input would
satisfy both `ensures` clauses.

**Predicted fix, not yet applied:** add pinning clauses referencing the
function's own composition, mirroring `ExpectedDose`'s role in
`dosage.dfy`:
`ensures formula == EGFRFormula ==> AssessRenalFunction(formula, renalFunctionValue) == EGFRAssessment(GStage(RoundHalfUp(renalFunctionValue)))`
(and the symmetric clause for the CrCl branch).

### The other three functions look genuinely tight — also a prediction, not yet confirmed

- **`RoundHalfUp`**: `ensures (result as real) - 0.5 <= x < (result as real) + 0.5`. The half-open intervals `[n-0.5, n+0.5)` for consecutive integers `n` are disjoint and tile the reals with no gap — by inspection, this should already pin a *unique* integer per `x`. Predicted STP: a uniqueness lemma (if `n1` and `n2` both satisfy the postcondition for the same `x`, then `n1 == n2`) should verify cleanly.
- **`GStage`**: six `ensures` clauses, mutually exclusive range guards, jointly covering all `roundedEgfr >= 0` with no gap. Predicted STP: a totality lemma (every `roundedEgfr >= 0` satisfies at least one guard) and a uniqueness lemma should both verify cleanly — each guard forces exact equality when it applies, and the guards don't overlap.
- **`SelectFormula`**: two `ensures` clauses that are exact logical negations of each other — trivially exhaustive and mutually exclusive. Predicted STP: low novelty, but a completeness lemma is cheap to write and worth having for parity with the other functions.

## Per-function STP lemma plan, using the 16-row test-vector table

The table already committed in `PHASE1_PLAN.md` supplies the concrete
`(input, output)` pairs; each row becomes one ACCEPT lemma. REJECT/
uniqueness/totality lemmas (above) are new, not derived from the table.

| Function | ACCEPT lemmas (from the 16-row table) | REJECT / structural lemmas |
|---|---|---|
| `RoundHalfUp` | Rows 2–6 (10 boundary values) + row 1's two values (53.0, 36.9) | Uniqueness (predicted: verifies) |
| `GStage` | Rows 2–6 (composed with `RoundHalfUp`, already proven in Gate 1c's scratch check — formalize into the committed suite) | Totality + uniqueness (predicted: verifies) |
| `SelectFormula` | Rows 7–12 (six branch cases) | Exhaustiveness/mutual-exclusivity (predicted: verifies) |
| `ComposedCeiling` | Rows 15–16 (both directions) | **REJECT: wrong-value-not-excluded (predicted: FAILS — real gap expected)** |
| `AssessRenalFunction` | Row 1 (NHS SPS, both paths) + the two type-safety lemmas already in Gate 1c's audit | **REJECT: wrong-stage-not-excluded (predicted: FAILS — real gap expected)** |

Rows 13 (REQ-RENAL-3) and 14 (REQ-RENAL-4) have no function to test yet
— named gap, not silently skipped; those two rows stay unused until
REQ-RENAL-3/4 are formalized as signatures (still prose-only, per
`renal_adjustment.dfy`'s own header comment).

## What building this actually involves

1. Write `renal_adjustment_stp_suite.dfy` (`include`s `renal_adjustment.dfy`),
   with the ACCEPT/REJECT/structural lemmas above.
2. Run it for real against Dafny 4.11.0 — **expect two REJECT lemmas to
   fail**, per the predictions above. If they fail as predicted, that
   confirms the analysis and identifies exactly where
   `renal_adjustment.dfy` needs pinning clauses added (mirroring
   `dosage.dfy`'s own fix), not a surprise finding requiring new
   investigation.
3. Fix `ComposedCeiling` and `AssessRenalFunction` with the pinning
   clauses sketched above; re-verify `renal_adjustment.dfy` itself
   (`dafny verify`, expect still `5 verified, 0 errors` — pinning
   clauses should be provable from the existing bodies without
   changing them, same as `ExpectedDose` didn't need `dosage.dfy`'s
   clamping logic to change).
4. Re-run the STP suite — expect all lemmas (ACCEPT and REJECT) to pass
   cleanly this time.
5. Preserve the original, under-constrained versions as honesty
   exhibits if the predictions confirm (mirroring
   `dosage_underconstrained.dfy` / `dosage_stp_suite_against_underconstrained.dfy`'s
   pattern) — a real, committed record that Gate C4 caught something,
   not smoothed over.
6. `run_verify_dafny_stp_suite_renal.py` capture runner, mirroring
   `run_verify_dafny_stp_suite.py` exactly.
7. Update `nl_confirmation_renal_adjustment_dfy.md` if
   `ComposedCeiling`/`AssessRenalFunction`'s `ensures` clauses change —
   Gate C6's sign-off would need re-presenting for the changed
   postconditions, same discipline as `dosage.dfy`'s Gate C5 amendment
   after its own postcondition tightening.

If either prediction turns out wrong (a REJECT lemma that was expected
to fail actually verifies, or vice versa), that gets reported honestly,
not silently reconciled — same standard the LVR extension's own
hand-derived prediction was held to.
