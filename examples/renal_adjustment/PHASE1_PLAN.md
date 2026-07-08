# Renal Function Dose Adjustment — Phase 1 (Specification & Foundation)

Status: **Gate 1a in progress, corrected against primary sources.** Not yet
closed — see "Still open" at the end. No Dafny code exists yet; Phase 2
(the Gate C1/C6/C4/C3/C5 build pipeline, per
`/root/.claude/plans/stateless-weaving-firefly.md`'s infrastructure plan)
is blocked on this document closing.

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
| REQ-RENAL-2 | Formula selection: eGFR is the default for most drugs/most adult patients of average build and height. Cockcroft-Gault CrCl is required instead for: direct-acting oral anticoagulants (apixaban, dabigatran, edoxaban, rivaroxaban); patients on nephrotoxic drugs (e.g. vancomycin, amphotericin B); patients aged ≥75; patients at extremes of muscle mass (BMI <18 or >40 — exact thresholds, not a fuzzy judgment call); medicines renally excreted with a narrow therapeutic index (e.g. digoxin, sotalol). | MHRA Drug Safety Update, vol. 13, issue 3 (Oct 2019), verified by direct fetch. |
| REQ-RENAL-3 | Cockcroft-Gault is unreliable when weight is distorted by obesity or oedema (it is a weight-based formula) — flag rather than silently compute. | KDIGO 2024 (Cockcroft-Gault limitations discussion, same section as Table 11); see `sources/kdigo-2024-gfr-staging.md`. Corrected citation — the original scoping draft attributed this to MHRA, but a direct MHRA fetch did not corroborate the obesity/oedema caveat; KDIGO does. |
| REQ-RENAL-4 | Fail-safe on missing/invalid renal-function data: never default to unadjusted/full dose. | Design invariant (not a single citable clinical source; same category as `dosage.dfy`'s own fail-safe defaults). |
| REQ-RENAL-5 | Monotonicity and bound composition against `dosage.dfy`'s existing clamp: the more conservative of the two bounds always wins (intersection, not override). | Design invariant, this artifact's own interaction contract. |
| REQ-RENAL-6 | Reassessment flag on rapidly changing renal function (AKI) — a single value must not be treated as authoritative in that situation. Absorbs the "unstable renal function" language originally proposed as part of REQ-RENAL-3, since both describe the same underlying steady-state assumption failing; that half was never independently corroborated by any source fetched (MHRA's actual stated caveat is specifically about rapid change / AKI reassessment, which is this requirement, not a separately-sourced general "unstable" flag). | MHRA Drug Safety Update, vol. 13, issue 3 (Oct 2019); merge decision recorded here rather than left as an unresolved gap in `sources/kdigo-2024-gfr-staging.md`. |
| REQ-RENAL-7 | For narrow-therapeutic-index drugs specifically (already one of REQ-RENAL-2's five conditions), when the eGFR branch is selected, BSA-nonindexed eGFR (ml/min, not ml/min/1.73m²) may be needed at extremes of body weight — indexed eGFR can over/under-estimate actual drug clearance in very small or large individuals. | KDIGO 2024, p. S164, Practice Point 4.2.4; see `sources/kdigo-2024-gfr-staging.md`. New requirement, not in the original scoping draft. |

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
  reference ranges entirely (explicit out-of-scope, not an implicit gap;
  confirmation from Steven still pending, see Open Questions).
- Weight and sex present whenever Cockcroft-Gault is selected (both
  required by the formula itself).
- The MHRA/NICE/KDIGO override conditions (extremes of muscle mass,
  obesity/oedema per REQ-RENAL-3, AKI per REQ-RENAL-6) are explicit flag
  paths, not silently absorbed into the calculation.

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
- Correct, total mapping from rounded eGFR/CrCl to KDIGO G-stage, proven
  exactly at each boundary (89.5/90, 59.5/60, 44.5/45, 29.5/30, 14.5/15
  — corrected boundary set per REQ-RENAL-1a, not the naive integers).
- Monotonicity: assigned dose is non-increasing as renal function
  worsens.
- Output bounds: renal-adjusted dose never exceeds the unadjusted dose,
  and lies within whatever licensed dose range is supplied as
  configuration.

**Fail-safe and missing-data postconditions:**
- Missing/invalid renal-function input fails safe (withhold, flag for
  clinician review) as a proven postcondition, not a tested-by-example
  behaviour (REQ-RENAL-4).
- AKI / rapidly-changing renal function raises a reassessment flag
  (REQ-RENAL-6).

**Interaction contract with `dosage.dfy` (REQ-RENAL-5).** The final
output must be provably within both the renal-adjustment bound and
`dosage.dfy`'s existing clamp simultaneously — the intersection, i.e. the
more conservative constraint always wins.

## Gate 1c — Internal consistency and completeness audit

Not yet performed — blocked on Gate 1b's skeleton being reviewed against
`dosage.dfy`'s actual header/precondition structure (per the Verification
section below), and on the open questions closing. When run, this gate
will hand-trace every `REQ-RENAL-*` through the Gate 1b skeleton and
hand-trace the NHS SPS worked example (80-year-old man, 60 kg, creatinine
120 micromol/L → CrCl 37 mL/min vs. eGFR 53 mL/min/1.73m²) as a first
sanity check, before any Dafny code exists.

## Still open (named, not guessed)

1. **Paediatric scope** — assumed out-of-scope for v1 (adult-only,
   REQ-RENAL-1b precondition), pending Steven's confirmation.
2. **Combined creatinine-cystatin C eGFR** — KDIGO 2024 prefers this
   where cystatin C is available (REQ-RENAL-1). Named as a second,
   unbuilt branch for v1, not silently excluded, pending Steven's
   decision on whether to scope it in now or defer it.
3. **Seed test cases beyond the NHS SPS example** — pending Steven's
   input on which other worked examples to pin before Gate 1c closes.
4. **Gate 1c itself** has not yet been run (see above) — this is the
   remaining work needed to formally close Gate 1.

## Documentation set updated so far

- `sources/KDIGO-2024-CKD-Guideline.pdf`, `sources/kdigo-2024-gfr-staging.md`,
  `sources/README.md` — committed.
- This file (`examples/renal_adjustment/PHASE1_PLAN.md`) — this commit.
- Still to do: `payloadguard-evidence-roadmap-phaseB-to-C.md` (new section,
  condensed), `KNOWN_LIMITATIONS.md` (pointer row for per-drug-factors
  non-goal and paediatric/cystatin-C exclusions), `DEVLOG.md` (dated entry).

## Verification

- This document has not yet been checked against `dosage.dfy`'s actual
  precondition structure to confirm the interaction contract (bound
  intersection, REQ-RENAL-5) is expressed in terms that match the
  existing code rather than just prose — still to do before Gate 1b is
  finalized.
- Before Phase 2 begins: re-confirm the MHRA and NICE source URLs still
  resolve and cite the same content.
- `python -m pytest tests/ -q` — 138 passed, unaffected (no code changed
  by this document).
