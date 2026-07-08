# Gate 1c — Internal consistency and completeness audit

Status: **performed 2026-07-08.** Hand-traces every `REQ-RENAL-*` and the
NHS SPS worked example through the Gate 1b skeleton (`PHASE1_PLAN.md`,
`gate_c1_sketch.md`), using the 16-row test-vector table as raw material.
Per Gate 1c's own stated purpose — catch conceptual gaps at the cheapest
possible point, before any Dafny code exists — **this audit found two
real gaps, not zero.** Consistent with this repo's discipline, they're
named here rather than smoothed over so Gate 1 can be marked closed.
**Conclusion: Gate 1 is not yet fully closeable.** See "Exit criteria
assessment" at the end.

## Total coverage check

Each of the four sketched functions is domain-total over its declared
precondition, confirmed both by inspection of its `ensures` clauses and
by the real Dafny 4.11.0 verification runs already recorded in
`gate_c1_sketch.md`:

- `RoundHalfUp(x: real)`, `requires x >= 0.0`: every non-negative real
  maps to exactly one integer (the `ensures` bounds it to a half-open
  unit interval around the input). No gap.
- `GStage(roundedEgfr: int)`, `requires roundedEgfr >= 0`: the six
  `ensures` clauses (`>=90`, `60..89`, `45..59`, `30..44`, `15..29`,
  `<15`) partition all non-negative integers with no overlap and no
  gap — confirmed by Dafny accepting all six as simultaneously provable
  for the same input.
- `SelectFormula(...)`: the two `ensures` clauses are a condition and its
  exact negation — total and exhaustive over all 2×2×∞×∞×2 = every
  reachable combination of the five inputs, confirmed by Dafny (a single
  `if`/`else` on the same boolean expression the `ensures` clauses use).
- `ComposedCeiling(existingCeiling, renalCeiling: real)`, both
  `requires > 0.0`: total `min`-style function, no gap.

**Composed boundary check, run for real (not just argued):** wrote
`GStage(RoundHalfUp(x))` compositions as Dafny lemmas for all ten
boundary-tie/just-under pairs from the Gate 1c test-vector table (rows
2–6) plus the NHS SPS eGFR value (53.0), and verified them against real
Dafny 4.11.0: **24 verified, 0 errors.** Every boundary lands exactly
where REQ-RENAL-1a predicts (89.5→G1, 89.499999→G2, and so on through
14.5/14.499999→G4/G5). Boundary-inclusivity is now proven for the
composition, not just for each function individually.

## New finding 1: no function computes the actual CrCl/eGFR numeric value

`SelectFormula` decides *which* formula applies; `RoundHalfUp` and
`GStage` operate on an eGFR/CrCl value that arrives already computed.
**No Dafny function has been sketched anywhere in this POC's planning
that actually computes Cockcroft-Gault CrCl or CKD-EPI eGFR from raw
inputs (age, weight, sex, creatinine).** This was never an explicit
scope decision — it fell out silently from decomposing the skeleton
into staging/selection/composition functions, and Gate 1c is exactly
where a silent gap like this should be caught, not Phase 2.

Two ways to resolve it, not decided here:

- **(a) In scope for Phase 2:** write and prove a `ComputeCockcroftGault`
  function from the exact formula already cited in Gate 1a (`(140-age) ×
  weight × constant / creatinine`, `constant = 1.23` male / `1.04`
  female — a single, provable rational-arithmetic expression, no
  meaningfully greater proof risk than `dosage.dfy`'s own arithmetic).
  The CKD-EPI 2021 eGFR equation is a much larger undertaking (piecewise,
  sex- and creatinine-threshold-dependent, involves real exponentiation
  Dafny doesn't natively support without careful modeling) and would
  need its own scoping pass if pursued.
- **(b) Caller-supplied, same trust boundary as REQ-RENAL-8's
  classification flags:** the proof establishes correct rounding,
  staging, formula selection, and bound composition given an already-
  computed value, not the correctness of the computation itself. This
  mirrors the per-drug-factors non-goal and REQ-RENAL-8 exactly, and
  would be the lower-risk, faster-to-close option for this POC's stated
  purpose (proving the Gate C1–C6 pipeline generalizes to conditional
  branching, not proving every clinical formula in the domain).

**Recommendation, not a decision:** (b) for CKD-EPI eGFR (too large a
proof undertaking to justify for what this POC needs to demonstrate),
(a) for Cockcroft-Gault specifically (small, already fully specified,
genuinely cheap to add, and it's the one MHRA gives an exact formula
for). This is Steven's call, named here rather than assumed.

## New finding 2: `GStage` is eGFR-specific; applying it to Cockcroft-Gault CrCl would be a category error

`GStage`'s six `ensures` clauses were derived directly from KDIGO's G1–G5
table (`sources/kdigo-2024-gfr-staging.md`), which stages **eGFR**
specifically — a BSA-normalized value (ml/min/1.73m²). Cockcroft-Gault
CrCl is **not** BSA-normalized (ml/min, raw) and is not staged via
KDIGO's G1–G5 categories in clinical practice; per-drug dosing tables
keyed to CrCl use raw numeric thresholds (e.g. "if CrCl < 30 mL/min,
reduce dose"), not the G-stage nomenclature.

Concretely: for the NHS SPS worked example, `SelectFormula` correctly
picks `CockcroftGaultFormula` (age 80 ≥ 75). If the resulting CrCl value
(36.9, rounds to 37) were then run through `GStage`, it would report
"G3a" — but that's an eGFR-scale label being applied to a CrCl-scale
number. The two values aren't clinically equivalent even when close in
magnitude (this exact patient: CrCl 37 vs. eGFR 53, the ~30% divergence
that's the whole reason `REQ-RENAL-2`'s formula-selection branch exists
in the first place). **`GStage` should only ever be called on an eGFR
value, never on a Cockcroft-Gault CrCl value** — this needs to be an
explicit branch in the eventual top-level method (eGFR path: compute →
round → `GStage` → dose-lookup keyed by G-stage; CrCl path: compute →
round → dose-lookup keyed by a separate numeric-threshold table), not a
single unconditional `GStage` call downstream of `SelectFormula`.

This is a real design decision for Gate 1b's method-level structure that
wasn't visible until this audit actually traced a concrete example
through the skeleton — exactly the kind of gap a hand-trace is supposed
to catch. Not resolved here; named for Phase 2's method design.

## REQ-by-REQ trace

| ID | Enforced by | Status |
|---|---|---|
| REQ-RENAL-1 | `GStage` (eGFR path only — see Finding 2) | Staging logic proven total and boundary-correct; **the eGFR-only scope of `GStage` needs to be an explicit branch, not assumed** |
| REQ-RENAL-1a | `RoundHalfUp`, composed with `GStage` | Proven for real (24/24 lemmas verified) |
| REQ-RENAL-2 | `SelectFormula` | Proven total and exhaustive |
| REQ-RENAL-3 | Not yet a function — precondition/flag path named in Gate 1b prose only | Not yet formalized as a signature; same status as before this audit |
| REQ-RENAL-4 | Not yet a function — fail-safe postcondition named in Gate 1b prose only | Not yet formalized as a signature; same status as before this audit |
| REQ-RENAL-5 | `ComposedCeiling` | Proven for real |
| REQ-RENAL-6 | Not yet a function — reassessment flag named in Gate 1b prose only | Not yet formalized as a signature; same status as before this audit |
| REQ-RENAL-7 | Not yet a function — BSA de-normalization named in Gate 1a prose only | Not yet formalized as a signature; same status as before this audit |
| REQ-RENAL-8 | `SelectFormula`'s inputs (caller-supplied) | Settled trust boundary; provenance itself still unscoped (see `PHASE1_PLAN.md`) |
| *(unnumbered)* | Actual CrCl/eGFR value computation | **New gap, Finding 1 above — not covered by any sketched function** |

Four of eight numbered requirements (REQ-RENAL-3, 4, 6, 7) have never
had a Dafny signature sketched at all — they exist only as prose in
Gate 1a/1b. This was already implicitly true before this audit but is
worth stating plainly here rather than letting the four verified
functions create an impression of more coverage than actually exists.

## NHS SPS worked example — full hand-trace

Patient: 80-year-old man, 60 kg, serum creatinine 120 µmol/L.

1. `SelectFormula(false, false, 80, bmi_unspecified, false)` → age
   condition (`80 >= 75`) alone triggers `CockcroftGaultFormula`,
   regardless of the unspecified BMI/other flags (any true value
   independently forces the same result — OR-logic, proven).
2. Cockcroft-Gault CrCl (hand-computed, no Dafny function exists for
   this yet — Finding 1): `(140 - 80) × 60 × 1.23 / 120 = 36.9`.
   Matches the NHS SPS source's published **37 mL/min** once rounded.
3. `RoundHalfUp(36.9) = 37` — confirmed by direct computation
   (`36.9 + 0.5 = 37.4`, floor `37`), consistent with the verified
   function's `ensures` clause.
4. **`GStage` is not applicable here** — CrCl was selected, not eGFR
   (Finding 2). The example's eGFR value (53, CKD-EPI, externally given
   — no eGFR-computation function exists either, Finding 1) is the one
   that would go through `RoundHalfUp`/`GStage`: `RoundHalfUp(53.0) = 53`,
   `GStage(53) = G3a` — proven for real (lemma
   `NhsSps_53_is_G3a`, part of the 24/24 verified composed check above).
5. The ~30% CrCl-vs-eGFR divergence (37 vs. 53) is exactly the
   documented consequence `REQ-RENAL-2`'s formula-selection branch
   exists to catch — hand-tracing it end to end confirms the branch
   produces the clinically correct choice (Cockcroft-Gault, driven by
   age) rather than defaulting to eGFR and silently under-dosing.

## Open judgment calls (named, not guessed)

1. **Classification-flag provenance (REQ-RENAL-8)** — unchanged from
   `PHASE1_PLAN.md`: who sets the caller-supplied flags, by what
   process.
2. **CrCl/eGFR value computation scope (new, Finding 1)** — in scope for
   Phase 2 (at least for Cockcroft-Gault) or caller-supplied like the
   classification flags. Recommendation offered above, not decided.
3. **`GStage`'s eGFR-only applicability (new, Finding 2)** — needs to be
   an explicit two-path branch in the eventual top-level method, not
   assumed obvious from the function signature alone.

## Exit criteria assessment

Per `PHASE1_PLAN.md`'s Gate 1 exit criteria ("all three sub-gates
complete... specification skeleton has no undefined input regions...
audit document names every open judgment call rather than resolving
them implicitly"): **Gate 1c is now performed, but Gate 1 is not yet
fully closeable** — this audit found the skeleton *does* have an
undefined input region (Finding 1: no CrCl/eGFR computation path) and
an unstated branching assumption (Finding 2: `GStage`'s eGFR-only
scope). Both are named, not resolved, per this repo's discipline. Phase
2 remains blocked until Steven decides Finding 1's scope question and
the method-design consequence of Finding 2 is incorporated into Gate
1b's skeleton.
