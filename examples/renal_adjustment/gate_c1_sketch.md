# Gate C1 sketch: signatures and test vectors, before any implementation

Status: **all four functions checked against the real Dafny 4.11.0
toolchain (2026-07-08) and verify cleanly** — `RoundHalfUp`, `GStage`,
`SelectFormula`, `ComposedCeiling`, each 1 verified / 0 errors in a
scratch file, `ensures` clauses holding for real, not asserted. None of
this is yet part of a committed `.dfy` file in `examples/renal_adjustment/`
— the scratch check is a de-risking step, not a build step, and no
mutation testing, STP suite, or Gate C3 lint has run against any of
them. Per Steven's instruction, test vectors were defined before any
body was written, mirroring the discipline the Gate C5 LVR extension
used (hand-derived prediction recorded before the real run). This does
not start Phase 2 — Gate 1c's hand-trace write-up is still open (see
`PHASE1_PLAN.md`), and these signatures are exactly what Gate 1c needs
to be checked against, not a way around it.

Four logical operations, decomposed rather than inlined into one or two
methods (per the Gate C1 options discussion) — each becomes its own
`function`, callable from one top-level `method`, the same shape that
let Gate C5's AOR/LVR extensions target `dosage.dfy`'s companion
function directly. The fourth, `ComposedCeiling`, was added after
checking `dosage.dfy`'s actual signature directly (it takes a single
`maxSafeDoseMgPerHr: real`, not a pair of bounds to intersect — REQ-
RENAL-5's "more conservative bound wins" claim has to be a composition
step upstream of it, not something provable inside `dosage.dfy` itself).

## 1. `RoundHalfUp` — REQ-RENAL-1a

```
function RoundHalfUp(x: real): int
  requires x >= 0.0
  ensures (RoundHalfUp(x) as real) - 0.5 <= x < (RoundHalfUp(x) as real) + 0.5
  ensures x - x.Floor as real == 0.5 ==> RoundHalfUp(x) == x.Floor + 1  // ties round up
```

**Test vectors (defined now, checked once a body exists):**

| Input | Expected output | Why |
|---|---|---|
| 89.5 | 90 | tie, rounds up |
| 89.49999 | 89 | just under the tie |
| 59.5 | 60 | tie, rounds up |
| 59.49999 | 59 | just under |
| 44.5 | 45 | tie, rounds up |
| 44.49999 | 44 | just under |
| 29.5 | 30 | tie, rounds up |
| 29.49999 | 29 | just under |
| 14.5 | 15 | tie, rounds up |
| 14.49999 | 14 | just under |
| 53.0 | 53 | NHS SPS worked example (eGFR 53) |
| 0.0 | 0 | lower boundary, not yet a rejection case |

### `RoundHalfUp` implementation strategy (Gate C1 options, recommendation 2, mapped out)

The signature above states *what* `RoundHalfUp` must satisfy; this maps
out *how* it gets implemented and verified, so Gate C1's build has a
concrete plan rather than starting from a blank function body.

**Candidate body:**

```
function RoundHalfUp(x: real): int
  requires x >= 0.0
  ensures (RoundHalfUp(x) as real) - 0.5 <= x < (RoundHalfUp(x) as real) + 0.5
{
  (x + 0.5).Floor
}
```

**Why this shape, not an alternative:**

- Dafny's `real.Floor` is a built-in, total function on reals (`real ->
  int`, always rounds toward negative infinity) — already used
  implicitly wherever `dosage.dfy` does real-to-int-adjacent reasoning,
  so it is a known-verifiable primitive in this repo's Dafny version
  (4.11.0), not a new risk.
- `(x + 0.5).Floor` is the standard round-half-up construction: for any
  non-negative `x`, adding `0.5` then flooring rounds every value in
  `[n - 0.5, n + 0.5)` to `n`, and pushes an exact tie (`x = n - 0.5`)
  up to `n` rather than down — which is exactly KDIGO's own convention
  (see `sources/kdigo-2024-gfr-staging.md`), not an arbitrary choice
  between round-half-up and round-half-even. Round-half-even (banker's
  rounding) was considered and rejected: KDIGO's cited text says
  "rounded to the nearest whole number" with no even/odd tie-breaking
  rule stated, and clinical dose-staging conventions (and the NHS SPS
  worked example) consistently read as round-half-up in practice.
- **Alternative rejected:** inlining `x + 0.5` then truncating at each
  of the five boundary comparisons inside `GStage` directly, instead of
  factoring out `RoundHalfUp`. Rejected for the reason already given
  when this option was first raised — it multiplies the proof and
  mutation-testing surface fivefold for a single, unchanging operation,
  and risks the boundaries drifting out of sync under a future edit.

**Proof strategy — checked against the real toolchain, not just
hand-reasoned.** The candidate body above was written to a scratch file
and run through the actual installed Dafny 4.11.0 (`dafny verify`,
2026-07-08): **1 verified, 0 errors.** Z3 discharged the `ensures`
clause directly from `Floor`'s built-in axiom with no hinting needed —
the bridging `assert` step flagged as a risk above turned out to be
unnecessary in practice. This was a scratch-file check
(`/tmp/.../scratchpad/round_half_up_check.dfy`), not a committed build
artifact — Gate C3's vacuous-precondition/weak-postcondition checks
still need to run for real once this is part of a committed spec, since
a scratch check confirms the proof goes through, not that it goes
through *for the right reason* (that's exactly what Gate C3 and the STP
suite are for).

**Test-vector-to-STP mapping.** Every row in the table above becomes one
Gate C4-equivalent STP lemma once Phase 2 starts (e.g. `lemma
RoundHalfUp_89_5_rounds_up() ensures RoundHalfUp(89.5) == 90`), and the
five tie rows collectively become the mutation-testing (Gate C5
equivalent) target for LVR on the `0.5` literal — swapping it to `0.4`
or `0.6` should flip exactly the tie-boundary test vectors and nothing
else, which is the kind of exact, predicted mutant-kill pattern Gate C5
has consistently produced on `dosage.dfy`.

## 2. `GStage` — REQ-RENAL-1

```
datatype GStageCategory = G1 | G2 | G3a | G3b | G4 | G5

function GStage(roundedEgfr: int): GStageCategory
  requires roundedEgfr >= 0
  ensures roundedEgfr >= 90 ==> GStage(roundedEgfr) == G1
  ensures 60 <= roundedEgfr <= 89 ==> GStage(roundedEgfr) == G2
  ensures 45 <= roundedEgfr <= 59 ==> GStage(roundedEgfr) == G3a
  ensures 30 <= roundedEgfr <= 44 ==> GStage(roundedEgfr) == G3b
  ensures 15 <= roundedEgfr <= 29 ==> GStage(roundedEgfr) == G4
  ensures roundedEgfr < 15 ==> GStage(roundedEgfr) == G5
```

Note: `GStage` takes an already-*rounded* integer — it composes with
`RoundHalfUp`'s output, it does not re-derive the boundary shift itself.
Keeping the two functions separate means the STP suite (Gate C4
equivalent) can prove the composition `GStage(RoundHalfUp(x))` pins
89.5/59.5/44.5/29.5/14.5 correctly without `GStage` itself needing to
know about rounding.

**Candidate body, verified against real Dafny 4.11.0, 2026-07-08: 1
verified, 0 errors** (straightforward cascading `if`, descending
threshold order — Z3 discharged all six `ensures` clauses without
hinting):

```dafny
{
  if roundedEgfr >= 90 then G1
  else if roundedEgfr >= 60 then G2
  else if roundedEgfr >= 45 then G3a
  else if roundedEgfr >= 30 then G3b
  else if roundedEgfr >= 15 then G4
  else G5
}
```

**Test vectors:**

| Rounded eGFR | Expected stage |
|---|---|
| 90 | G1 |
| 89 | G2 |
| 60 | G2 |
| 59 | G3a |
| 45 | G3a |
| 44 | G3b |
| 30 | G3b |
| 29 | G4 |
| 15 | G4 |
| 14 | G5 |
| 53 | G3a (NHS SPS worked example) |

## 3. `SelectFormula` — REQ-RENAL-2

```
datatype Formula = EGFRFormula | CockcroftGaultFormula

function SelectFormula(
  isDirectActingOralAnticoagulant: bool,
  isOnNephrotoxicDrug: bool,
  ageYears: int,
  bmi: real,
  isNarrowTherapeuticIndexDrug: bool
): Formula
  requires ageYears >= 0
  requires bmi > 0.0
  ensures (isDirectActingOralAnticoagulant || isOnNephrotoxicDrug || ageYears >= 75
           || bmi < 18.0 || bmi > 40.0 || isNarrowTherapeuticIndexDrug)
          ==> SelectFormula(isDirectActingOralAnticoagulant, isOnNephrotoxicDrug,
                             ageYears, bmi, isNarrowTherapeuticIndexDrug) == CockcroftGaultFormula
  ensures !(isDirectActingOralAnticoagulant || isOnNephrotoxicDrug || ageYears >= 75
            || bmi < 18.0 || bmi > 40.0 || isNarrowTherapeuticIndexDrug)
          ==> SelectFormula(isDirectActingOralAnticoagulant, isOnNephrotoxicDrug,
                             ageYears, bmi, isNarrowTherapeuticIndexDrug) == EGFRFormula
```

**Test vectors:**

| Anticoag | Nephrotoxic | Age | BMI | NTI drug | Expected |
|---|---|---|---|---|---|
| true | false | 40 | 24.0 | false | CockcroftGault (anticoag alone forces it) |
| false | true | 40 | 24.0 | false | CockcroftGault (nephrotoxic alone) |
| false | false | 75 | 24.0 | false | CockcroftGault (age boundary, inclusive) |
| false | false | 74 | 24.0 | false | EGFR (just under age boundary) |
| false | false | 40 | 17.9 | false | CockcroftGault (BMI just under 18) |
| false | false | 40 | 40.1 | false | CockcroftGault (BMI just over 40) |
| false | false | 40 | 24.0 | true | CockcroftGault (NTI drug alone) |
| false | false | 40 | 24.0 | false | EGFR (no condition holds) |
| false | false | 80 | 24.0(implied) | false | CockcroftGault — NHS SPS worked example, age 80 |

**Precision gap resolved, 2026-07-08:** the BMI boundary's exact
inclusivity has now been verified directly against the MHRA source's
literal wording (not assumed) — `sources/mhra-renal-formula-selection-2019.md`
records the verbatim quote: "patients at extremes of muscle mass (BMI
<18 kg/m2 or >40 kg/m2)." Strict inequality confirmed: exactly 18.0 or
40.0 is not itself "extreme." The signature above's `< 18.0`/`> 40.0` is
now a cited fact, not an assumption.

**Candidate body, verified against real Dafny 4.11.0, 2026-07-08: 1
verified, 0 errors** (a single OR-guarded `if`, matching the `ensures`
clauses' own condition exactly — no separate proof needed for the
combinatorial case, since the OR is checked as one guard, not five
independent branches):

```dafny
{
  if isDirectActingOralAnticoagulant || isOnNephrotoxicDrug || ageYears >= 75
     || bmi < 18.0 || bmi > 40.0 || isNarrowTherapeuticIndexDrug
  then CockcroftGaultFormula
  else EGFRFormula
}
```

## 4. `ComposedCeiling` — REQ-RENAL-5

```dafny
function ComposedCeiling(existingCeiling: real, renalCeiling: real): real
  requires existingCeiling > 0.0
  requires renalCeiling > 0.0
  ensures ComposedCeiling(existingCeiling, renalCeiling) <= existingCeiling
  ensures ComposedCeiling(existingCeiling, renalCeiling) <= renalCeiling
{
  if renalCeiling < existingCeiling then renalCeiling else existingCeiling
}
```

Not decomposed further — this is already minimal (a `min` over two
positive reals). Named as its own function, not inlined into
`renal_adjustment.dfy`'s top-level method, because it's the composition
bridge to `dosage.dfy`, not a `renal_adjustment.dfy`-internal concern;
Phase 2 should give it its own Gate C1 capture and Gate C4 STP pair.

**Verified against real Dafny 4.11.0, 2026-07-08: 1 verified, 0
errors.** Both `ensures` clauses hold — the "more conservative bound
wins" claim (REQ-RENAL-5) is proven for this function directly, not
asserted in prose.

**Test vectors:**

| existingCeiling | renalCeiling | Expected result | Why |
|---|---|---|---|
| 10.0 | 6.0 | 6.0 | renal ceiling more conservative, wins |
| 6.0 | 10.0 | 6.0 | existing ceiling more conservative, wins |
| 8.0 | 8.0 | 8.0 | equal — either branch, same result |

## What happens next

These signatures and test vectors are Gate 1c's actual raw material —
Gate 1c is the hand-trace of `REQ-RENAL-*` and the NHS SPS example
through exactly this skeleton (already partially done in the "NHS SPS
worked example" rows above, and now backed by the 16-row table in
`PHASE1_PLAN.md`). All four functions now verify individually against
the real Dafny toolchain; none of them have been composed together in
one file, none have run through Gate C3's lint checks or a real Gate C5
mutation suite, and none are yet part of a committed `.dfy` file. The
next concrete step is writing up Gate 1c's actual hand-trace document
(tracing each `REQ-RENAL-*` through this now-verified skeleton) and
scoping classification-flag provenance (see `PHASE1_PLAN.md`'s "Still
open" section), before Phase 2 (a real, committed `renal_adjustment.dfy`
composing all four functions) begins.
