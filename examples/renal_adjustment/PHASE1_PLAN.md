# Renal Function Dose Adjustment — Phase 1 (Specification & Foundation)

Status: **Gate 1 closed, under two named, documented fallback
assumptions — Phase 2 started 2026-07-08.** Gate 1a and 1b closed; Gate
1c performed (`examples/renal_adjustment/GATE_1C_AUDIT.md`) and found
two real gaps, one resolved by redesign (`AssessRenalFunction`'s
type-level fix for the `GStage`-misapplication finding), one closed by
an explicit provisional default rather than a permanent decision:

1. **CrCl/eGFR value computation (Finding 1): defaulted to
   caller-supplied for both formulas in Phase 2 v1.** Not a design
   change — `AssessRenalFunction` already takes `renalFunctionValue:
   real` as a parameter regardless of who computes it. The verified
   Cockcroft-Gault formula (`sources/ckd-epi-2021-and-cockcroft-gault-verification.md`)
   is ready to add as a pure extension (a new function feeding the same
   parameter) whenever Steven decides to build it — this default does
   not foreclose that, it just doesn't block starting on it.
2. **Classification-flag provenance (`REQ-RENAL-8`): reclassified as a
   Phase 3 integration concern, not a Phase 2 proof blocker.**
   `SelectFormula`'s flags are already caller-supplied parameters — the
   open question (clinician form vs. EHR lookup vs. static list) is
   about who populates them operationally, which the proof itself
   doesn't need resolved. Named here so it isn't silently dropped, not
   silently promoted to a blocker it was never structurally being.

Five core proof functions (`RoundHalfUp`, `GStage`, `SelectFormula`,
`ComposedCeiling`, `AssessRenalFunction`) verify cleanly against the
real, installed Dafny 4.11.0 toolchain, including the composed boundary
behavior (`GStage(RoundHalfUp(x))`, 24/24 verified) and
`AssessRenalFunction`'s type-level proof that a Cockcroft-Gault CrCl
value can never reach `GStage` (11/11 verified). Phase 2 (the Gate
C1/C6/C4/C3/C5 build pipeline, per
`/root/.claude/plans/stateless-weaving-firefly.md`'s infrastructure
plan) is now underway — see `examples/renal_adjustment/renal_adjustment.dfy`
and its capture.

**Gate C1 built** (`renal_adjustment.dfy`, `run_verify_renal.py`,
real capture: `5 verified, 0 errors`). **Gate C6 built** (NL-dialogue
confirmation, moved earlier per its own recommendation) — see
`examples/renal_adjustment/nl_confirmation_renal_adjustment_dfy.md`,
pending Steven's sign-off. Building it surfaced two real bugs in shared
tooling, caught rather than papered over: `evidence/dafny_nl_summary.py`
and `evidence/dafny_spec_lint.py::_find_method_header` only matched
Dafny's `method` keyword, never `function` — `renal_adjustment.dfy` is
the first spec in this repo consisting entirely of functions, and the
gap only surfaced when Gate C6 was actually pointed at it (fixed, small
widened regex, two regression tests). Separately, `_REQ_ID_RE`'s
character class silently truncated `REQ-RENAL-1a` to `REQ-RENAL-1` (no
lowercase letters in its pattern) — a real citation-accuracy bug, not
hypothetical, since `dosage.dfy`'s REQ-IDs never had a lowercase suffix
to expose it (fixed, regression-tested). 142 tests passing (up from
138).

## Objective

A complete, internally consistent, clinically-grounded formal
specification for renal-function dose adjustment — PayloadGuard-Evidence's
second independent proof-of-concept, demonstrating the Gate C1–C6 pipeline
generalizes from arithmetic clamping (`dosage.dfy`) to lookup-table and
conditional-branching logic. UK-jurisdiction from the outset
(MHRA/NICE/KDIGO/UK Kidney Association), not a port of US convention.
Maps onto IEC 62304 Clause 5: this document covers development planning +
requirements analysis + architectural/detailed design (5.1–5.4); Phase 2
covers unit implementation and verification (5.5); Phase 3 covers release
(5.8) plus Clause 7 risk management and SOUP/tool documentation.

## Gate 1a — Clinical source audit & requirements extraction

Requirements table, each row citing an exact, versioned source — mirroring
`sources/req-gip-1-4-12-alarm-scope-decision.md`'s discipline. Corrected
against the primary sources actually fetched/extracted this session (see
`sources/kdigo-2024-gfr-staging.md`; MHRA and NICE NG203 were verified
directly by WebFetch earlier in this work and are cited as such below).

| ID | Requirement | Source |
|---|---|---|
| REQ-RENAL-1 | GFR category assignment: G1 ≥90, G2 60–89, G3a 45–59, G3b 30–44, G4 15–29, G5 <15 mL/min/1.73m², creatinine-based eGFR (eGFRcr) as default; combined creatinine-cystatin C eGFR (eGFRcr-cys) preferred where cystatin C is available (named, not built — see Open Questions). | KDIGO 2024, p. S126 (Table, "Current CKD Nomenclature"); see `sources/kdigo-2024-gfr-staging.md`. |
| REQ-RENAL-1a | eGFR is reported rounded to the nearest whole number before staging — the effective continuous G-stage boundaries for a real-valued input are 89.5/59.5/44.5/29.5/14.5 (round-half-up), not the naive 90.0/60.0/45.0/30.0/15.0. | KDIGO 2024, p. S164, Table 11 ("Implementation standards..."); see `sources/kdigo-2024-gfr-staging.md`. New finding, not in the original scoping draft. |
| REQ-RENAL-2 | Formula selection: eGFR is the default for most drugs/most adult patients of average build and height. Cockcroft-Gault CrCl is required instead for: direct-acting oral anticoagulants (apixaban, dabigatran, edoxaban, rivaroxaban); patients on nephrotoxic drugs (e.g. vancomycin, amphotericin B); patients aged ≥75; patients at extremes of muscle mass (**BMI <18 kg/m² or >40 kg/m², strict inequality — verbatim MHRA wording, verified directly against the primary MHRA page**, not a fuzzy judgment call); medicines renally excreted with a narrow therapeutic index (e.g. digoxin, sotalol). | MHRA Drug Safety Update, vol. 13, issue 3 (Oct 2019), verified by direct fetch; see `sources/mhra-renal-formula-selection-2019.md`. |
| REQ-RENAL-3 | Cockcroft-Gault is unreliable when weight is distorted by obesity or oedema (it is a weight-based formula) — flag rather than silently compute. | KDIGO 2024 (Cockcroft-Gault limitations discussion, same section as Table 11); see `sources/kdigo-2024-gfr-staging.md`. Corrected citation — the original scoping draft attributed this to MHRA, but a direct MHRA fetch did not corroborate the obesity/oedema caveat; KDIGO does. |
| REQ-RENAL-4 | Fail-safe on missing/invalid renal-function data: never default to unadjusted/full dose. | Design invariant (not a single citable clinical source; same category as `dosage.dfy`'s own fail-safe defaults). |
| REQ-RENAL-5 | Monotonicity and bound composition against `dosage.dfy`'s existing clamp, via a new, explicitly built and proven function, `ComposedCeiling` (see Gate 1b) — the more conservative of the two bounds provably wins. **Settled as a built, proven function, not left as prose or a caller convention.** | Design invariant; `ComposedCeiling` checked directly against `dosage.dfy`'s actual `CalculateHourlyDose` signature (single `maxSafeDoseMgPerHr: real` parameter — no internal bound pair to intersect, so composition has to happen upstream of it) and verified against real Dafny 4.11.0, 2026-07-08: 1 verified, 0 errors. |
| REQ-RENAL-6 | Reassessment flag on rapidly changing renal function (AKI) — a single value must not be treated as authoritative in that situation. Absorbs the "unstable renal function" language originally proposed as part of REQ-RENAL-3, since both describe the same underlying steady-state assumption failing; that half was never independently corroborated by any source fetched (MHRA's actual stated caveat is specifically about rapid change / AKI reassessment, which is this requirement, not a separately-sourced general "unstable" flag). | MHRA Drug Safety Update, vol. 13, issue 3 (Oct 2019); merge decision recorded here rather than left as an unresolved gap in `sources/kdigo-2024-gfr-staging.md`. |
| REQ-RENAL-7 | For narrow-therapeutic-index drugs specifically (already one of REQ-RENAL-2's five conditions), when the eGFR branch is selected, BSA-nonindexed eGFR (ml/min, not ml/min/1.73m²) may be needed at extremes of body weight — indexed eGFR can over/under-estimate actual drug clearance in very small or large individuals. | KDIGO 2024, p. S164, Practice Point 4.2.4; see `sources/kdigo-2024-gfr-staging.md`. New requirement, not in the original scoping draft. |
| REQ-RENAL-8 | `SelectFormula`'s boolean drug-classification inputs (`isDirectActingOralAnticoagulant`, `isOnNephrotoxicDrug`, `isNarrowTherapeuticIndexDrug`) are **caller-supplied, not computed inside `renal_adjustment.dfy`.** The proof establishes correct OR-logic branching given the flags — including the case where more than one flag is true simultaneously, which earns an explicit test vector rather than an assumption — not the correctness of the classification itself. Same trust-boundary pattern as the per-drug-factors non-goal, below. Reason: MHRA's own drug lists are illustrative ("such as vancomycin and amphotericin B"), not closed or exhaustive; hardcoding them into the spec would embed a false-completeness claim inside a formally "proven" artifact. | Design/trust-boundary decision, settled 2026-07-08. **Renumbered from a proposed `REQ-RENAL-7` in the uploaded research-findings document to `REQ-RENAL-8`** — `REQ-RENAL-7` was already committed above (BSA de-normalization, KDIGO Practice Point 4.2.4) before that document arrived; flagged and resolved here rather than silently overwritten. This settles *that* the flags are caller-supplied but explicitly does not settle *who* sets them or by what process — see "Still open," below. |

**Explicit non-goal.** Per-drug numeric dose-reduction factors are not
sourced or proven in this gate — BNF/SPC/Renal Drug Handbook disagree at
the individual-drug level. Scoped as a versioned, human-signed-off
configuration input (a Gate C6-style artifact), with the proof
establishing correct, monotonic, bounded *application* of whatever factor
is supplied, mirroring how `dosage.dfy` treats `maxSafeDoseMgPerHr` as a
parameter, not a baked-in constant. The MHRA source's own fallback chain
(BNF monograph first, SmPC where the BNF gives no CrCl-based advice) is
part of what a future configuration-input schema needs to record.

## Gate 1b — Formal specification skeleton (structure, not code)

**Preconditions:**
- Serum creatinine within a physiologically plausible band; reject
  non-positive or absurd values.
- Adult patient only for v1 — paediatric renal dosing uses different
  reference ranges entirely. **Settled: excluded from v1**, explicit
  adult-only precondition. No free UK paediatric renal-dosing standard
  exists at the level of the adult sources used here; building it now
  would mean guessing at reference ranges.
- Weight and sex present whenever Cockcroft-Gault is selected (both
  required by the formula itself).
- The MHRA/NICE/KDIGO override conditions (extremes of muscle mass,
  obesity/oedema per REQ-RENAL-3, AKI per REQ-RENAL-6) are explicit flag
  paths, not silently absorbed into the calculation.
- BMI strictly less than 18.0 or strictly greater than 40.0 triggers the
  "extremes of muscle mass" formula-selection condition (REQ-RENAL-2) —
  `< 18.0`/`> 40.0`, not `<=`/`>=`, per the verbatim MHRA wording.

**Precondition style, matched to the existing spec rather than invented
fresh.** `dosage.dfy`'s actual, verified `CalculateHourlyDose` signature
constrains only what the proof needs constrained, strict inequality
throughout (`requires concentrationMgPerMl > 0.0`, `requires
maxSafeDoseMgPerHr > 0.0`), leaving inputs like `infusionRateMlPerHr`
deliberately unconstrained where the proof doesn't require it (negative
"reverse flow" is let through, on purpose, to satisfy REQ-GIP-1-8-1).
`renal_adjustment.dfy`'s preconditions should follow the same
discipline: strict `>`/`<` throughout, nothing constrained beyond what a
specific `REQ-RENAL-*` actually requires.

**Combined creatinine-cystatin C eGFR (part of REQ-RENAL-1): settled as
named, not built.** A closed-form 2021 CKD-EPI creatinine-cystatin-C
equation exists and is fully provable (Inker et al., "New Creatinine-
and Cystatin C-Based Equations to Estimate GFR without Race," *N Engl J
Med* 2021;385(19):1737–1749, PMID 34554658 — verified directly against
PubMed, title/journal/volume/pages/DOI all match), so this is not a
feasibility gap. But cystatin C isn't routinely measured in UK practice,
making the branch near-permanently unreachable with real data for this
POC. Documented as a future extension, same pattern as the Gate C5 LVR
extension naming EQ-literal mutation as a gap before building it.

**Rounding-then-staging decision (REQ-RENAL-1a), decided here:**
`renal_adjustment.dfy` will accept a real-valued eGFR/CrCl and **prove the
rounding step explicitly as its own operation before staging** — not
accept a pre-rounded integer as an unproven precondition. This is the
more faithful, more provable model, and it is exactly the kind of
boundary-precision question Gate C4's STPs exist to pin down (an STP
lemma will prove, e.g., "eGFR = 89.5 rounds to 90 and stages to G1,
eGFR = 89.49999 rounds to 89 and stages to G2"). Recorded as a closed
decision, not left open into Phase 2.

**Formula-selection logic — the core novel proof target.** Prove
Cockcroft-Gault is selected whenever any REQ-RENAL-2 condition holds, and
eGFR otherwise; prove the two paths are never silently conflated. Highest
proof value of anything in this spec: it's the conditional-branching
structure `dosage.dfy` doesn't have, and getting it wrong has a
documented, quantified consequence (NHS SPS worked example: CrCl 37
mL/min vs. eGFR 53 mL/min/1.73m², ~30% relative difference, same patient).

**Staging and lookup postconditions:**
- Correct, total mapping from rounded eGFR to KDIGO G-stage, proven
  exactly at each boundary (89.5/90, 59.5/60, 44.5/45, 29.5/30, 14.5/15
  — corrected boundary set per REQ-RENAL-1a, not the naive integers).
- Monotonicity: assigned dose is non-increasing as renal function
  worsens.
- Output bounds: renal-adjusted dose never exceeds the unadjusted dose,
  and lies within whatever licensed dose range is supplied as
  configuration.

**Two separate downstream paths, settled by design (Gate 1c Finding 2,
resolved).** `GStage`'s KDIGO-derived boundaries are eGFR-specific and
must never be applied to a Cockcroft-Gault CrCl value — found by
hand-tracing the NHS SPS example in Gate 1c (see
`GATE_1C_AUDIT.md`'s addendum). Resolved by a dispatcher function,
`AssessRenalFunction(formula: Formula, renalFunctionValue: real):
RenalAssessment`, whose return type is a tagged union
(`EGFRAssessment(stage: GStageCategory) | CrClAssessment(roundedCrClMlPerMin:
int)`) — `GStage` can only be reached inside the `EGFRFormula` branch, so
a raw CrCl number can never be mislabeled with a KDIGO G-stage, and an
eGFR value can never skip staging. This is a type-level guarantee, not a
calling convention: verified against real Dafny 4.11.0, 11/11 verified,
0 errors, including two explicit lemmas proving each direction of the
impossibility. Full signature and test vectors in `gate_c1_sketch.md`
section 5.

**Fail-safe and missing-data postconditions:**
- Missing/invalid renal-function input fails safe (withhold, flag for
  clinician review) as a proven postcondition, not a tested-by-example
  behaviour (REQ-RENAL-4).
- AKI / rapidly-changing renal function raises a reassessment flag
  (REQ-RENAL-6).

**Interaction contract with `dosage.dfy` (REQ-RENAL-5) — settled as a
built, proven function, not documentation.** `CalculateHourlyDose` takes
a single `maxSafeDoseMgPerHr: real` parameter — there's no pair of bounds
inside it to intersect, checked directly against the real file at
`examples/dosage_calculator/dosage.dfy`. "The more conservative bound
wins" therefore has to be a composition step upstream of it, not a claim
about `dosage.dfy`'s own proof surface. Named explicitly as a new
function rather than left as an unproven caller convention:

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

Its result is what gets passed in as `CalculateHourlyDose`'s
`maxSafeDoseMgPerHr` argument. **Verified against real Dafny 4.11.0,
2026-07-08: 1 verified, 0 errors** — both `ensures` clauses hold, not
just asserted. This is the one proof in the whole second POC that
actually demonstrates cross-module extensibility rather than asserting
it. Phase 2 now builds **two** proof units (`renal_adjustment.dfy` and
`ComposedCeiling`), not one — `ComposedCeiling` should get its own Gate
C1 capture, Gate C4 STP pair (both directions: renal ceiling wins,
existing ceiling wins), and Gate C6 NL confirmation, not be folded
silently into `renal_adjustment.dfy`'s own gates.

## Gate 1c — Internal consistency and completeness audit

**Ordering note, settled:** REQ-RENAL-8 (flag ownership) had to resolve
before the seed test-vector table below could be finalized. With
classification flags caller-supplied rather than drug-name-derived, the
test vectors exercise `SelectFormula`'s branching logic directly (set a
flag, check the branch) — they don't need real drug names or a
classification dataset. Had REQ-RENAL-8 gone the other way (spec-owned
drug lists), the table would have needed actual drug identifiers, which
was never sourced and would have blocked this gate.

**Seed test-vector table (16 rows) — the actual raw material for the
hand-trace audit, not a replacement for it:**

| # | Case | Exercises |
|---|---|---|
| 1 | NHS SPS worked example (80yo, 60kg, creatinine 120 µmol/L) | eGFR-vs-CrCl divergence (~30%), real numbers |
| 2 | eGFR = 90 exactly, and 89.499999 | G1/G2 boundary post-rounding (89.5 shift, REQ-RENAL-1a) |
| 3 | eGFR = 60 exactly, and 59.499999 | G2/G3a boundary post-rounding |
| 4 | eGFR = 45 exactly, and 44.499999 | G3a/G3b boundary post-rounding |
| 5 | eGFR = 30 exactly, and 29.499999 | G3b/G4 boundary post-rounding |
| 6 | eGFR = 15 exactly, and 14.499999 | G4/G5 boundary post-rounding |
| 7 | `isDirectActingOralAnticoagulant = true`, others false | Formula selection, REQ-RENAL-2 |
| 8 | `age = 75` exactly, and 74 | Formula selection age threshold, inclusivity |
| 9 | `bmi = 18.0`/`17.999`, and `bmi = 40.0`/`40.001` | Formula selection BMI threshold, strict inequality per verified MHRA citation |
| 10 | `isOnNephrotoxicDrug = true`, others false | Formula selection, REQ-RENAL-2 |
| 11 | `isNarrowTherapeuticIndexDrug = true`, others false | Formula selection, REQ-RENAL-2 |
| 12 | Two or more flags true simultaneously | REQ-RENAL-8 combinatorial OR-logic, not assumed trivial |
| 13 | Unstable-weight/oedema flag true | REQ-RENAL-3 reliability override — flagged, not silently computed |
| 14 | Renal-function input missing/invalid | REQ-RENAL-4 fail-safe, never defaults to full dose |
| 15 | `ComposedCeiling`: renal ceiling more conservative than existing | REQ-RENAL-5, renal bound wins |
| 16 | `ComposedCeiling`: existing dosage ceiling more conservative than renal | REQ-RENAL-5, existing bound wins |

Rows 2–6 use `89.499999` etc. rather than the previously-drafted
`89.999` — corrected to match REQ-RENAL-1a's actual rounding shift
(the boundary is 89.5, not 89.999/90).

**Performed 2026-07-08 — see `examples/renal_adjustment/GATE_1C_AUDIT.md`
for the full hand-trace.** Total coverage confirmed for all four sketched
functions; the composed boundary behavior (`GStage(RoundHalfUp(x))`) was
verified for real against Dafny across all ten boundary rows above plus
the NHS SPS eGFR value (24/24 verified, 0 errors); the NHS SPS example
was hand-traced end to end, including the raw Cockcroft-Gault arithmetic
(36.9, rounds to 37 — matches the published figure exactly). **The audit
found two real gaps, not zero:** (1) no function computes the actual
Cockcroft-Gault CrCl or CKD-EPI eGFR numeric value from raw inputs — the
skeleton only stages/selects/composes an already-computed value; (2)
`GStage`'s KDIGO-derived boundaries are specific to eGFR and must not be
applied to a Cockcroft-Gault CrCl value (a category error — CrCl isn't
BSA-normalized and isn't clinically staged via G1–G5). **Finding 2 is
now resolved** by the `AssessRenalFunction` dispatcher (see Gate 1b
above and `gate_c1_sketch.md` section 5), which makes the category error
a type-level impossibility rather than a convention to remember —
verified against real Dafny, 11/11, 0 errors. Finding 1 remains open, by
explicit choice (Steven's direction: defer it, resolve Finding 2 first).

## Closed under named fallback assumptions (not silently, not permanently)

~~1. Classification-flag provenance (opened by REQ-RENAL-8).~~
**Reclassified 2026-07-08 as a Phase 3 concern, not a Phase 1/2
blocker.** `SelectFormula`'s flags were always caller-supplied
parameters — the open question is *who* populates them operationally
(clinician form, EHR lookup, static versioned list), which is an
external-integration decision the proof itself doesn't need resolved.
Still a real, unscoped item — not dropped, just correctly placed in
Phase 3 rather than treated as blocking Phase 2's proof work, which it
never structurally was.

~~2. CrCl/eGFR value computation scope (Gate 1c finding 1).~~
**Defaulted 2026-07-08 to caller-supplied for both formulas in Phase 2
v1** — a provisional default, not a permanent decision, per Steven's
explicit direction ("assumption I'll find the data"). Backed by
verified data either way it eventually goes:
`sources/ckd-epi-2021-and-cockcroft-gault-verification.md` confirms
both 2021 CKD-EPI equations exactly (independently checked against the
National Kidney Foundation's own published equations) and the original
1976 Cockcroft-Gault formula/MHRA constant arithmetic; it also corrects
a fabricated NICE NG203 citation from the supplied research document
(claimed recommendation numbers/text that don't exist in the real
guideline — UK lab practice is actually heterogeneous and in
transition, per an independent 2024 UK study, Roy et al., *Nephron*,
PMID 39342928, not settled on one equation).

Cockcroft-Gault has no fractional-exponent term and is a small,
linear-arithmetic formula well within Dafny/Z3's proven capability
(same category as `RoundHalfUp`/`GStage`/`ComposedCeiling`) — ready to
add as a pure extension (a new function feeding `AssessRenalFunction`'s
existing `renalFunctionValue: real` parameter) whenever Steven decides
to build it; this default doesn't foreclose that. CKD-EPI's real-valued
fractional exponents on a variable base (`Scr^-1.200`, `Scr^-0.302`,
etc.) are a genuine Dafny/Z3 expressiveness gap, not a performance
issue — a proposed lookup-table workaround was evaluated and found to
relocate, not eliminate, the trust boundary (the LUT itself would need
independent verification against the formula), so CKD-EPI stays
caller-supplied for longer than Cockcroft-Gault regardless of when this
default gets revisited.

~~3. `GStage`'s eGFR-only applicability (Gate 1c finding 2).~~ **Resolved
2026-07-08** — `AssessRenalFunction`'s tagged-union return type makes
this a type-level impossibility. See Gate 1b above.

**Gate 1 is closed, under the two documented fallback assumptions
above.** Nothing was silently resolved: both remaining items are named,
dated, and reversible — Phase 2 does not depend on either being decided
permanently, only on the fallback being an honest, stated default.
Phase 2 started 2026-07-08 — see `renal_adjustment.dfy`.

## Documentation set updated so far

- `sources/KDIGO-2024-CKD-Guideline.pdf`, `sources/kdigo-2024-gfr-staging.md`,
  `sources/mhra-renal-formula-selection-2019.md`, `sources/README.md` —
  committed.
- This file (`examples/renal_adjustment/PHASE1_PLAN.md`),
  `examples/renal_adjustment/gate_c1_sketch.md`, and
  `examples/renal_adjustment/GATE_1C_AUDIT.md` — committed.
- Still to do: `payloadguard-evidence-roadmap-phaseB-to-C.md` and
  `KNOWN_LIMITATIONS.md` (both need updating for Gate 1c's two findings),
  `DEVLOG.md` (dated entry).

## Verification

- **Done:** `dosage.dfy` pulled from `examples/dosage_calculator/dosage.dfy`
  at HEAD and checked directly — the `ComposedCeiling` finding above is
  against the literal signature, not a description of it.
- **Done:** both `RoundHalfUp` and `ComposedCeiling` checked against the
  real, installed Dafny 4.11.0 toolchain in this environment (not just
  hand-reasoned) — both verify cleanly, 0 errors. Neither is yet part of
  a committed `.dfy` file in `examples/renal_adjustment/` — this was a
  scratch-file check, not a build step, and Phase 2 hasn't formally
  started.
- **Done:** the MHRA BMI-boundary citation (REQ-RENAL-2) verified directly
  against the primary MHRA page (not a secondary source); the
  ClinicalTrials.gov NCT02942810/NCT02039817 corroboration and the Inker
  et al. 2021 PMID 34554658 citation were independently checked against
  ClinicalTrials.gov and PubMed directly, not taken on trust.
- Before Phase 2 begins: re-confirm the MHRA and NICE source URLs still
  resolve and cite the same content.
- Before `ComposedCeiling` is built for real inside a committed file:
  re-pull `dosage.dfy` once more immediately prior, in case other work
  has touched its signature since this check.
- `python -m pytest tests/ -q` — 138 passed, unaffected (no code changed
  by this document).
