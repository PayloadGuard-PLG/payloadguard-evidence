# Renal Function Dose Adjustment — Audit-Trail Record

Second, independent proof-of-concept for the PayloadGuard evidence
layer: staging renal function (GFR/CrCl), selecting which formula
governs a given patient, and adjusting a drug dose ceiling accordingly —
verified with the same Gate C1–C6 Dafny/Z3 pipeline built for
`dosage_calculator/`, on a UK-jurisdiction clinical example (MHRA,
KDIGO, NICE) chosen specifically to stress lookup-table and
conditional-branching logic, not just arithmetic clamping.

This file is the fixed audit-trail record — source citations,
interpretive-call caveats, and dated amendments. For **current, living
status** (what's built vs. open, the concrete next step), see
`PHASE1_PLAN.md` and the repository root's `HANDOFF.md`; this file
doesn't duplicate that and isn't kept in lockstep with it turn by turn.

## Source documents

| Document | Role |
|---|---|
| MHRA Drug Safety Update, vol. 13, issue 3 (Oct 2019), "Prescribing medicines in renal impairment" | Formula-selection rule (REQ-RENAL-2) and its BMI boundary; AKI reassessment caveat (REQ-RENAL-6). Verified by direct fetch, `sources/mhra-renal-formula-selection-2019.md`. |
| KDIGO 2024 Clinical Practice Guideline for CKD, *Kidney International* (2024) 105(Suppl 4S) | GFR staging categories (REQ-RENAL-1), rounding convention (REQ-RENAL-1a), Cockcroft-Gault reliability limitations (REQ-RENAL-3), BSA de-normalization practice point (REQ-RENAL-7). Archived verbatim as `sources/KDIGO-2024-CKD-Guideline.pdf`; extract and citations in `sources/kdigo-2024-gfr-staging.md`. |
| NICE NG203, "Chronic kidney disease: assessment and management" | eGFR equation choice (CKD-EPI, no version mandated) and pre-test preparation; cited to correct a fabricated citation, see Amendment below. Verified by direct fetch. |
| Cockcroft DW, Gault MH (1976), *Nephron* 16(1):31-41, PMID 1244564 | Original CrCl formula, independently verified against a peer-reviewed secondary source (full text not machine-extractable from 1976 PubMed record). `sources/ckd-epi-2021-and-cockcroft-gault-verification.md`. |
| Inker LA et al. (2021), *NEJM* 385(19):1737-1749, PMID 34554658 | 2021 CKD-EPI creatinine and creatinine-cystatin-C eGFR equations (race-free). Verified against the National Kidney Foundation's own published equations. `sources/ckd-epi-2021-and-cockcroft-gault-verification.md`. |

## Requirement-to-source mapping

| ID | Requirement | Built? |
|---|---|---|
| `REQ-RENAL-1` | GFR category assignment (G1–G5), eGFRcr default | `GStage` — proven |
| `REQ-RENAL-1a` | Round-to-nearest-whole-number before staging | `RoundHalfUp` — proven |
| `REQ-RENAL-2` | Formula selection (eGFR vs. Cockcroft-Gault), five trigger conditions | `SelectFormula` — proven |
| `REQ-RENAL-3` | Cockcroft-Gault unreliable under obesity/oedema — flag, don't silently compute | Prose only — not yet a Dafny signature |
| `REQ-RENAL-4` | Fail-safe on missing/invalid renal-function data | Prose only — not yet a Dafny signature |
| `REQ-RENAL-5` | Bound composition against `dosage.dfy`'s existing ceiling | `ComposedCeiling` — proven |
| `REQ-RENAL-6` | AKI reassessment flag (absorbs REQ-RENAL-3's original "unstable renal function" half — see Amendment below) | Prose only — not yet a Dafny signature |
| `REQ-RENAL-7` | BSA-nonindexed eGFR for narrow-therapeutic-index drugs at extremes of body weight | Prose only — not yet a Dafny signature |
| `REQ-RENAL-8` | Drug-classification flags are caller-supplied, not computed | `SelectFormula`'s parameters — proven correct given the flags; flag provenance itself is out of scope, see Open Questions |
| *(unnumbered, Gate 1c Finding 1)* | CrCl/eGFR numeric value computation from raw patient data | Cockcroft-Gault: `CockcroftGaultCrClMlPerMin` — proven. CKD-EPI eGFR: caller-supplied, see Open Questions. |

Full requirement text and per-row source page citations:
`PHASE1_PLAN.md`'s requirements table.

## Interpretive-call caveats

1. **`RoundHalfUp`'s tie-break direction (round-half-*up*) is a named
   design decision, not a KDIGO rule.** KDIGO requires rounding to the
   nearest whole number but states no tie-breaking method; industry
   guidance (Miller et al., *Clin Chem* 2022;68(4):511-520, PMID
   34918062) explicitly defers this to each laboratory's own software.
   Originally miswritten as "KDIGO's own convention" — caught and
   corrected 2026-07-09, see the amendment below. The rounding *body*
   never changed, only the sourcing claim about it.
2. **`GStage` must never be called on a Cockcroft-Gault CrCl value.**
   CrCl isn't BSA-normalized and isn't clinically staged G1–G5 the way
   eGFR is — a category error, not just a units mismatch. Enforced at
   the type level (`AssessRenalFunction`'s tagged-union return type),
   not left as a calling convention a future caller has to remember.
3. **The Cockcroft-Gault CrCl formula uses the unrounded exact
   unit-conversion fraction (88.4/72), not the commonly-quoted rounded
   1.23 (male) / 1.04 (female) multiplier.** Earlier notes in this
   project called those "MHRA's constants" — a direct re-fetch of the
   MHRA source page found MHRA states no formula or numeric constant at
   all. The 1.23/1.04 figures are ordinary clinical-chemistry unit
   conversion, not an MHRA-specific number; see the amendment below and
   `sources/mhra-renal-formula-selection-2019.md`'s own 2026-07-09
   amendment.
4. **Per-drug numeric dose-reduction factors are an explicit non-goal**
   of this gate — BNF/SPC/Renal Drug Handbook disagree at the
   individual-drug level. The proof establishes correct, bounded
   *application* of a supplied factor, mirroring how `dosage.dfy`
   treats `maxSafeDoseMgPerHr` as a parameter, not a baked-in constant.
5. **Paediatric renal dosing is out of scope** — no free UK paediatric
   renal-dosing standard exists at the level of the adult sources used
   here.

## Amendment 2026-07-08 — Gate 1c Finding 2 resolved by redesign

Independent review found `GStage`'s eGFR-only applicability (caveat 2,
above) was an unstated assumption, not an enforced one. Resolved by
introducing `AssessRenalFunction` as the sole entry point permitted to
call `GStage`, with a tagged-union return type (`EGFRAssessment` vs.
`CrClAssessment`) making the category error a type-level impossibility.
Verified against real Dafny 4.11.0: 11/11, 0 errors at the time. Full
trace, including the NHS SPS worked example (80yo male, 60kg, creatinine
120 µmol/L; eGFR 53 vs. CrCl 37, a ~30% divergence) that motivated the
finding: `GATE_1C_AUDIT.md`.

## Amendment 2026-07-09 — RoundHalfUp's tie-break sourcing corrected

Direct challenge on Gate C6's sign-off review surfaced a
self-inconsistent overclaim (caveat 1, above): the round-half-up
tie-break had been presented as "KDIGO's own convention" in the same
paragraph that also stated KDIGO specifies no tie-breaking method at
all. Corrected in `sources/kdigo-2024-gfr-staging.md`, `gate_c1_sketch.md`,
and `renal_adjustment.dfy`'s header comment — no code change,
`RoundHalfUp`'s body was never wrong, only its sourcing claim. Full
detail: `KNOWN_LIMITATIONS.md`'s 2026-07-09 correction entry.

## Amendment 2026-07-09 — Gate C4 found and fixed two real under-constrained postconditions

Spec-Testing Proofs (IronSpec methodology) predicted, then confirmed for
real, that `ComposedCeiling` and `AssessRenalFunction`'s original
postconditions bounded their results without pinning them exactly — a
function returning a constant would have satisfied the original
`ensures` clauses just as well as the real implementation. REJECT lemmas
assuming a wrong candidate value genuinely **failed to verify**
(`renal_adjustment_stp_suite_against_underconstrained.dfy`, `0 verified,
4 errors`) against the preserved pre-fix spec
(`renal_adjustment_underconstrained.dfy`, kept verbatim as an honesty
exhibit). Fixed with pinning `ensures` clauses mirroring `ExpectedDose`'s
role in `dosage.dfy`. Re-verified clean; full STP suite passed at 44
lemmas at that point. Full detail: `gate_c4_stp_plan.md`,
`nl_confirmation_renal_adjustment_dfy.md`'s amendment section.

## Amendment 2026-07-09 — Gate 1c Finding 1 closed for Cockcroft-Gault; CKD-EPI eGFR confirmed not a scope choice

Steven's scope decision: build whatever the toolchain can actually
prove, defer whatever it can't — "if we have to tie to specific software
then if we physically cannot at the moment, then the choice is made for
us." `CockcroftGaultCrClMlPerMin` (small linear arithmetic, self-pinning
`ensures`) and `AssessRenalFunctionFromInputs` (end-to-end
orchestration: selects the formula, computes CrCl on the Cockcroft-Gault
branch, still takes a caller-supplied value on the eGFR branch) added to
`renal_adjustment.dfy` — `7 verified, 0 errors` (up from 5), STP-covered
with real ACCEPT/REJECT lemmas (`52 verified, 0 errors`, up from 44).
**CKD-EPI eGFR remains caller-supplied, confirmed as a genuine Dafny/Z3
expressiveness gap** (real-valued fractional exponents on a variable
base — `Scr^-1.200`, `Scr^-0.302`, etc.), not a preference; a proposed
lookup-table workaround was evaluated and found to relocate, not
eliminate, the trust boundary.

Implementing this first required re-fetching the MHRA and NICE NG203
source pages directly (due for a "still resolve to the same content"
re-check) — both confirmed unchanged since 2026-07-08, surfacing caveat
3 above along the way: MHRA's page states no Cockcroft-Gault formula or
constants, contrary to how earlier notes had characterized it. Full
detail: `GATE_1C_AUDIT.md`'s 2026-07-09 addendum,
`sources/mhra-renal-formula-selection-2019.md`'s amendment,
`KNOWN_LIMITATIONS.md`.

A second, unrelated real gap surfaced building this: `evidence/dafny_nl_summary.py`
correctly refused to summarize `AssessRenalFunctionFromInputs` on first
attempt because its `ensures` clauses were the first multi-line ones
ever written in this repo's Dafny specs. Fixed by reformatting to this
file's existing single-line convention (my own formatting slip, not a
genuine spec need), not by extending the tool. Named as a permanent
tooling constraint in `KNOWN_LIMITATIONS.md`.

## Amendment 2026-07-09 — Gate C3 (spec lint) built: all seven functions pass vector 1, five have expected vector 2 warnings

Applied `evidence/dafny_spec_lint.py`'s existing vectors 1-2 to every
function. **Vector 1 (vacuous preconditions):** all seven `sat` — no
function's `requires` clauses are vacuous. Found and fixed a real gap
applying this: `check_precondition_satisfiability` used to build a Z3
symbol for every declared parameter regardless of use, so
`AssessRenalFunction(formula: Formula, renalFunctionValue: real)`
refused outright on its `Formula`-typed parameter even though the one
`requires` clause never mentions it. Fixed to only model referenced
parameters — a referenced unsupported-type parameter still refuses,
unchanged. **Vector 2 (weak postconditions, heuristic):** unlike
`dosage.dfy` (zero warnings — its ensures clauses never use `==>`),
five of seven functions here genuinely use one-way implications for
exhaustive branch dispatch (16 warnings total) — expected, not a
regression: every one of these clauses is independently STP-covered by
Gate C4's ACCEPT/REJECT lemmas, a stronger, proof-based check than this
heuristic lint provides alone. Full detail and exact counts:
`tests/test_renal_adjustment_spec_lint.py`.

## Amendment 2026-07-09 — Gate C5 (mutation testing) built: 450 mutants, 51 explained survivors, one named engine gap

Ran the full ROR/LOR/AOR/LVR/COI suite independently against all seven
functions (`examples/renal_adjustment/run_mutation_suite_renal.py`) —
450 mutants, real-verified against Dafny 4.11.0: 250 killed, 137
filtered before verification, 51 survived, 10 unclassifiable, 2 blocked.
Four real gaps in the shared `evidence/dafny_mutate.py` engine surfaced
applying it to this spec's different shape (no top-level `method`, seven
independent proof targets, int-typed boundary literals, a datatype
discriminator) — full detail in the runner script's module docstring:

- **Fixed:** the lexical tokenizer had no `DOT` or `QUESTION` token, so
  `RoundHalfUp`'s `.Floor` and `AssessRenalFunction`'s
  `.EGFRAssessment?`/`.CrClAssessment?` raised "unsupported syntax" —
  both added, the same class of extension as the existing COMMA/SEMI
  tolerance.
- **Fixed:** LVR always formatted a mutated literal as a decimal
  (`90.01`), breaking Dafny's static typing on this spec's many
  int-typed boundary literals (`roundedEgfr >= 90`, `ageYears < 140`)
  — `dosage.dfy`'s literals were all already real-typed, so this never
  surfaced before. A literal's own lexical form now determines whether
  its mutant stays an int (+/-1) or a real (+/-0.01).
- **Named, not fixed — RoundHalfUp and CockcroftGaultCrClMlPerMin's LVR
  clause literals:** both have a literal embedded in arithmetic
  (`... - 0.5 <= x`; `140`/`88.4`/`72.0` deep inside a pinning
  equality's RHS) rather than directly adjacent to a comparison
  operator — the LVR locator's documented Tier-1 scope boundary. Real
  new design work, not a bounded fix (the narrowing/widening direction
  of an arithmetic-embedded literal depends on the enclosing operator);
  Gate C4's STP suite already independently proves both functions'
  exact values, so this is a coverage overlap loss, not a proof gap.
  Recorded as `blocked_lvr_clause_literal` (2 mutants).
- **Named, not fixed — SelectFormula's flat `||` chain:** mutating any
  one `||` to `&&` in its six-term, unparenthesized ensures antecedent
  produces Dafny's own genuine "Ambiguous use of && and ||" parser
  rejection. Unlike ROR's analogous, already-fixed chain-direction
  problem, this needs real new engineering (grouping same-paren-depth
  `&&`/`||` runs) that wasn't built here. Recorded as `unclassifiable`
  (10 mutants, all SelectFormula/LOR).

**All 51 survivors are explained, not an undifferentiated pile** — three
named categories, each locked in by `tests/test_renal_mutation_report.py`:

1. **33 survivors** — ROR/LVR mutations narrowing a one-way `==>`
   clause's antecedent (e.g. `roundedEgfr >= 90` → `roundedEgfr == 90`).
   A narrower antecedent's true-set is always a subset of the original's,
   so these can *never* be killed regardless of whether the spec is
   tight — a structural blind spot of this technique against
   guard-style clauses, not a proof gap. Gate C4's STP suite is the tool
   that actually pins these boundaries (dedicated lemmas at every
   G-stage transition).
2. **17 survivors** — `requires`-clause weakenings that Dafny can still
   satisfy because the specific `ensures` clauses currently proven don't
   depend on them (e.g. `ComposedCeiling`'s `<=`/pinning postconditions
   hold for any real `existingCeiling`/`renalCeiling` pair, not just
   positive ones). Not a defect: `> 0.0` still correctly documents a
   real domain fact (dose ceilings and BMI are physically positive) —
   it just isn't proof-necessary for what's currently established.
3. **1 survivor** — `RoundHalfUp`'s self-referential ensures clause
   survives an AOR `-` → `*` substitution for a coincidental numeric
   reason specific to that one substitution; its exact integer output is
   independently pinned by Gate C4's STP suite regardless.

## Fixture and capture formats

Mirrors `dosage_calculator/`'s discipline: every capture below is the
verbatim output of a real, installed Dafny 4.11.0 / Z3 run — none is
hand-typed.

- **`renal_adjustment.dfy`** — the committed spec, currently seven
  functions (`RoundHalfUp`, `GStage`, `SelectFormula`, `ComposedCeiling`,
  `AssessRenalFunction`, `CockcroftGaultCrClMlPerMin`,
  `AssessRenalFunctionFromInputs`). Captured by `run_verify_renal.py` →
  `raw_dafny_output_renal.txt` / `run_manifest_dafny_renal.json`.
- **`renal_adjustment_underconstrained.dfy`** — Gate C4 honesty exhibit:
  the pre-fix spec, preserved verbatim, never updated after the fix.
- **`renal_adjustment_stp_suite.dfy`** / **`renal_adjustment_stp_suite_against_underconstrained.dfy`**
  — Spec-Testing Proofs. The first passes against the fixed spec; the
  second (same REJECT lemmas, included against the preserved original)
  genuinely fails — both captured for real, not asserted. Runners:
  `run_verify_dafny_stp_suite_renal.py`,
  `run_verify_dafny_stp_suite_against_underconstrained_renal.py`.
- **`nl_confirmation_renal_adjustment_dfy.md`** — Gate C6: plain-English
  summaries generated by `evidence/dafny_nl_summary.py`, presented for
  Steven's sign-off. **Still pending confirmation** as of this writing —
  covers five amendments' worth of change (two Gate C4 fixes, two Gate
  1c Finding 1 additions, plus the original spec) under one outstanding
  decision.
- **`run_mutation_suite_renal.py`** / **`mutation_report_renal.json`/`.md`**
  / **`run_manifest_mutation_renal.json`** — Gate C5: capture runner and
  the real, committed outcome of every one of the 450 mutants above.
- **`gate_c1_sketch.md`**, **`gate_c4_stp_plan.md`**, **`GATE_1C_AUDIT.md`**
  — working documents: signature sketches individually verified before
  composition, hand-derived STP predictions checked before building,
  and the internal-consistency audit that found Findings 1 and 2.

## Open questions

Not resolved here — named, not guessed at, per this repo's discipline:

1. **`REQ-RENAL-8` classification-flag provenance.** Who sets
   `SelectFormula`'s caller-supplied boolean flags
   (`isDirectActingOralAnticoagulant`, etc.), by what process (clinician
   form, EHR lookup, static versioned list). Reclassified as a Phase 3
   integration concern, not a Phase 2 proof blocker — the proof itself
   doesn't need it resolved.
2. **CKD-EPI eGFR computation** remains caller-supplied, not because
   it's unscoped but because it's currently unprovable in this
   toolchain — see the 2026-07-09 amendment above. Revisit only if
   Dafny/Z3 gains real-valued fractional-exponent support, or if a
   verified lookup-table approach is built with its own independent
   verification against the formula (not assumed correct by
   construction).
3. **Gate C5's two named engine gaps** (SelectFormula's `||`-chain
   ambiguity; the two arithmetic-embedded LVR literals) are real,
   documented tooling limitations, not spec defects — see the Gate C5
   amendment above. Worth real engineering only if a future spec change
   makes them load-bearing in a way Gate C4's STPs don't already cover.
4. **Gate C6's sign-off is still pending** — the accumulated NL-summary
   document now covers seven amendments' worth of change under one
   outstanding decision. The concrete next step for this example.
