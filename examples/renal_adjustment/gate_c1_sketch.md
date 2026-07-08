# Gate C1 sketch: signatures and test vectors, before any implementation

Status: **sketch only.** No Dafny toolchain has touched this — these are
contract shapes (signature + `requires`/`ensures` intent), not verified
code. Per Steven's instruction, test vectors are defined here *before*
any function body is written, mirroring the discipline the Gate C5 LVR
extension used (hand-derived prediction recorded before the real run).
This does not start Phase 2 — Gate 1c (internal consistency audit) is
still open, and these signatures are exactly what Gate 1c needs to be
checked against, not a way around it.

Three logical operations, decomposed rather than inlined into one
method (per the Gate C1 options discussion) — each becomes its own
`function`, callable from one top-level `method`, the same shape that
let Gate C5's AOR/LVR extensions target `dosage.dfy`'s companion
function directly.

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

**Proof strategy — the actual verification risk, named up front rather
than assumed clean:** the `ensures` clause is a direct algebraic
consequence of the `Floor` body (`(x+0.5).Floor` satisfies
`(x+0.5).Floor <= x + 0.5 < (x+0.5).Floor + 1` by `Floor`'s own
definition, which rearranges to the stated `ensures`) — Z3 should
discharge this without hinting, similar in difficulty to `dosage.dfy`'s
own arithmetic postconditions. The one thing to actually check once
Dafny is invoked (not assumed): whether Dafny's `real` literal `0.5` and
`.Floor` interact with the SMT real-arithmetic theory cleanly, or
whether Z3 needs a `assert` lemma step bridging `Floor`'s built-in axiom
to the stated `ensures` — this is the kind of thing Gate C3's
vacuous-precondition/weak-postcondition checks exist to catch if the
proof goes through vacuously instead of for the right reason.

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

**Named precision gap, not yet resolved — flagging rather than
guessing an operator:** the BMI boundary's exact inclusivity (`< 18.0`
vs `<= 18.0`, `> 40.0` vs `>= 40.0` at BMI exactly 18.0/40.0) has not
been independently verified against the MHRA source's literal wording
the way the GFR/eGFR rounding boundary was. The signature above assumes
strict inequality (`< 18.0`, `> 40.0`, i.e. exactly 18.0 and exactly
40.0 are *not* "extremes") as the more conservative reading, but this
is an assumption, not a citation — needs the same source-verification
treatment KDIGO's Table 11 got before Gate 1c can close on it.

## What happens next

These signatures and test vectors are Gate 1c's actual raw material —
Gate 1c is the hand-trace of `REQ-RENAL-*` and the NHS SPS example
through exactly this skeleton (already partially done in the "NHS SPS
worked example" rows above). Once Steven confirms the BMI-boundary
citation and answers the three still-open Phase 1 questions
(`PHASE1_PLAN.md`), Gate 1c can close and Phase 2 (writing the real,
verified `renal_adjustment.dfy` body against this same signature shape)
can begin.
