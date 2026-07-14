# Hazard Register — Renal-Function Dose Adjustment (GFR Staging and Formula Selection, POC)

**Document ID:** HZ-RENAL-001
**Part of the risk management file** per ISO 14971:2019 clause 4.5 —
this is the risk *analysis* content (clause 5.4 hazard identification)
`RISK_MANAGEMENT_PLAN.md`'s Section 8 named as not yet existing.
Second hazard register in this repo, and a genuinely different
construction from the first (`dosage_calculator/HAZARD_REGISTER.md`):
this device has no published, numbered hazard-analysis source to
transcribe from. Instead, every hazard entry below is derived from two
real, already-existing sources — the nine named `REQ-RENAL-*`
requirement IDs (REQ-RENAL-1 through 8, plus sub-requirement
REQ-RENAL-1a; KDIGO/MHRA-sourced, `metadata.a.yaml`) and
`GATE_1C_AUDIT.md`'s own hand-trace findings, which already identify
concrete failure modes (a hazard analysis in substance, if not in the
GIP table's format).

**Status:** DRAFT | Version: 0.1 | Last reviewed: 2026-07-14

**What this register does, and does not, complete.** Same discipline as
the `dosage_calculator` register: hazard identification (clause 5.4)
and the qualitative half of clause 5.5 are real here — grounded in
`metadata.a.yaml`'s sourced requirement text and `GATE_1C_AUDIT.md`'s
own named findings, not invented. Severity, probability, and
acceptability evaluation remain explicit `GAP`s, pending the clinical
SME and manufacturer policy `RISK_MANAGEMENT_PLAN.md` Sections 2 and 4
still don't have.

---

## 1. Scope of this register

**8 hazard entries** (`HAZ-RENAL-1` through `HAZ-RENAL-8`) covering
**9 `REQ-RENAL-*` requirement IDs** — `HAZ-RENAL-1` covers both
REQ-RENAL-1 and its sub-requirement REQ-RENAL-1a together, since 1a is
a refinement of 1's own rounding behavior, not an independent hazard;
every other hazard entry maps 1:1 to its requirement number. This
device's own numbering already partitions its hazard-relevant surface,
so this register follows it directly rather
than inventing a separate scheme. Each entry states whether the
requirement is currently mitigated by a real Dafny proof or remains
prose-only, per `traceability_matrix.a.md`'s own `PROVEN`/`GAP` split
— stated honestly, not smoothed over. Section 3 below names what's
genuinely outside this device's scope entirely (not just "not yet
built").

---

## 2. Hazard entries

### HAZ-RENAL-1 — Wrong GFR-category assignment or category-type confusion

| Field | Value |
|---|---|
| Source | REQ-RENAL-1/1a, `metadata.a.yaml`. KDIGO boundaries (`sources/kdigo-2024-gfr-staging.md`, confirmed verbatim in Gate C6 sign-off: G1 ≥90, G2 60–89, G3a 45–59, G3b 30–44, G4 15–29, G5 <15 mL/min/1.73m²) plus `GATE_1C_AUDIT.md`'s "New finding 2" |
| Hazardous situation | Two distinct failure modes, both real and named, not hypothetical: (a) an eGFR value rounds/stages to the wrong KDIGO category at or near a boundary; (b) — the more serious one, actually found by this repo's own Gate 1c audit — a Cockcroft-Gault CrCl value (not BSA-normalized, not KDIGO-staged in clinical practice) gets run through `GStage` as if it were an eGFR value, producing a category-error label. Audit's own concrete example: the NHS SPS patient's CrCl (37 mL/min) would misreport as "G3a" if miscategorized this way, versus the correct, clinically distinct eGFR value (53) which genuinely is G3a — a ~30% numeric divergence that the label alone wouldn't reveal |
| Risk control measure | (a) `RoundHalfUp` composed with `GStage`, all ten boundary-tie/just-under cases plus the NHS SPS value verified as Dafny lemmas: **24 verified, 0 errors** (`GATE_1C_AUDIT.md`'s "Composed boundary check"). (b) `AssessRenalFunction`'s tagged-union return type (`EGFRAssessment(stage) \| CrClAssessment(roundedCrClMlPerMin)`) makes the miscategorization a **type-level impossibility**, not a convention a caller has to remember — pinned by its own four `ensures` clauses (`renal_adjustment.dfy:172-175`, tagged `REQ-RENAL-1, REQ-RENAL-2`), verified as part of the committed spec's real capture: **`raw_dafny_output_renal.txt`, 7 verified, 0 errors**. Correction: an earlier draft of this entry cited two named lemmas (`EgfrPathNeverProducesCrClAssessment`, `CrClPathNeverProducesEGFRAssessment`) and "11 verified, 0 errors" — those exist only in `gate_c1_sketch.md`, the historical 2026-07-08 planning sketch, not in the final committed spec or its real capture. Caught in PR #47 review; fixed to cite what's actually committed and reproducible |
| Known, named residual | REQ-RENAL-1a's round-half-up tie-break is itself an uncited design decision — KDIGO states no tie-break rule (confirmed directly, `sources/kdigo-2024-gfr-staging.md` line 137, per the Gate C6 sign-off). Not a defect, but worth a clinical SME's confirmation that half-up (vs. half-even) is the intended convention, not just an engineering default |
| Potential harm (qualitative, not scored) | Per `metadata.a.yaml`'s own `classification_rationale`: "failure could contribute to a non-serious renal dose-adjustment error given clinician oversight" — reused verbatim rather than inventing new harm language |
| Severity | `GAP` |
| Probability | `GAP` |
| Risk evaluation (acceptable?) | `GAP` |

### HAZ-RENAL-2 — Wrong formula selected, or selected formula's value computed incorrectly

| Field | Value |
|---|---|
| Source | REQ-RENAL-2, `metadata.a.yaml`. MHRA's five formula-selection conditions (`sources/mhra-renal-formula-selection-2019.md`, confirmed verbatim in Gate C6 sign-off: DOACs, nephrotoxic drugs, age ≥75, BMI extremes `<18` or `>40` strict inequality, narrow-therapeutic-index drugs) plus `GATE_1C_AUDIT.md`'s "New finding 1" |
| Hazardous situation | Two layers, kept distinct rather than conflated: (a) the wrong formula (eGFR vs. Cockcroft-Gault) is selected for a patient who meets one of the five MHRA conditions; (b) the *correct* formula is selected, but its underlying numeric value (CrCl or eGFR) is itself computed incorrectly upstream — a real, named gap this repo's own Gate 1c audit found (no function existed at all to compute the value from raw patient data; both formulas' outputs were being treated as already-computed, caller-supplied inputs) |
| Risk control measure | (a) `SelectFormula`'s two `ensures` clauses are a condition and its exact logical negation — Dafny-confirmed total and exhaustive over all reachable input combinations (`GATE_1C_AUDIT.md`'s "Total coverage check"). All five MHRA conditions, including the strict `<18`/`>40` BMI inequality, confirmed to match verbatim MHRA wording (Gate C6 sign-off). (b) **Closed for Cockcroft-Gault only**: `CockcroftGaultCrClMlPerMin` is committed and proven (`renal_adjustment.dfy`, `7 verified, 0 errors`; STP suite `52 verified, 0 errors`) — using the unrounded exact fraction, not the "1.23/1.04" constants an earlier draft of this audit incorrectly attributed to MHRA (MHRA only names Cockcroft-Gault as the required method; the constants are standard unit-conversion arithmetic, corrected 2026-07-10) |
| Known, named residual | **CKD-EPI eGFR's value computation remains caller-supplied — a genuine, empirically-confirmed Dafny/Z3 expressiveness limit, not a choice.** Two real probes committed: `dafny_pow_expressiveness_probe.dfy` (a direct attempt to express CKD-EPI's `min(Scr/κ,1)^α` shape — result: `Error: unresolved identifier: Pow`, Dafny has no real-exponentiation primitive at all) and `dafny_pow_axiom_trap_probe.dfy` (the obvious workaround, an unproven `{:axiom}` — result: `2 verified, 0 errors` *including* a lemma claiming `Pow` always returns exactly `0.0`, proving the axiom-based approach would verify nothing real). Confirmed by Steven's own framing: "if we physically cannot [tie eGFR to Dafny/Z3] at the moment, then the choice is made for us." This is the renal-adjustment analogue of `dosage_calculator`'s `system_scope` gap — a real, bounded, and named limit, not an oversight |
| Potential harm (qualitative, not scored) | Same framing as HAZ-RENAL-1 — a wrong formula choice, or a wrong value from a correctly-chosen formula, both risk an inappropriately high dose ceiling reaching a downstream calculation |
| Severity | `GAP` |
| Probability | `GAP` |
| Risk evaluation (acceptable?) | `GAP` |

### HAZ-RENAL-3 — Cockcroft-Gault used without flagging unreliability under obesity/oedema

| Field | Value |
|---|---|
| Source | REQ-RENAL-3, `metadata.a.yaml`: "Cockcroft-Gault is unreliable when weight is distorted by obesity or oedema (it is a weight-based formula) — should flag rather than silently compute." KDIGO-sourced |
| Hazardous situation | A patient with clinically significant oedema or obesity has their CrCl computed via the standard weight-based Cockcroft-Gault formula with no distinguishing flag — the numeric output looks identical to a reliable calculation, with nothing in this kernel's own output signalling the difference |
| Risk control measure | **None — not yet formalized as a Dafny signature.** `traceability_matrix.a.md`'s own row: `intended_method: PROVEN`, `realized: GAP`. Stated plainly, matching this repo's own "prose only" framing for this requirement, not implied to already have mechanical coverage |
| Known, named residual | This is a genuine open item, not a deferred nice-to-have — of the four prose-only requirements, this one has the most direct numeric-accuracy consequence (an unreliable weight-based estimate silently treated as reliable) |
| Potential harm (qualitative, not scored) | Same framing as HAZ-RENAL-1/2 |
| Severity | `GAP` |
| Probability | `GAP` |
| Risk evaluation (acceptable?) | `GAP` |

### HAZ-RENAL-4 — Missing or invalid renal-function data silently defaults to unadjusted (full) dose

| Field | Value |
|---|---|
| Source | REQ-RENAL-4, `metadata.a.yaml`: "Fail-safe on missing/invalid renal-function data: never default to unadjusted/full dose. Design invariant, same category as `dosage.dfy`'s own fail-safe defaults" |
| Hazardous situation | Missing, malformed, or otherwise invalid renal-function input reaches the dose-adjustment path and — absent an explicit fail-safe — the system defaults to the *unadjusted* full dose rather than refusing, flagging, or defaulting to the more conservative direction. This is the single most safety-critical named-but-unbuilt gap in this register: a fail-*open* behavior on bad data is a materially worse failure mode than any of the numeric-accuracy hazards above, since it bypasses renal adjustment entirely rather than mis-computing it |
| Risk control measure | **None — not yet formalized as a Dafny signature.** Same `GAP` status as HAZ-RENAL-3, `traceability_matrix.a.md` |
| Known, named residual | Flagged here as the highest-priority candidate for formalization among REQ-RENAL-3/4/6/7, precisely because "silently uses the full, unadjusted dose" is a fail-open pattern, not a fail-safe one — worth the user's/Risk Manager's attention ahead of the other three prose-only rows, though the actual priority ranking is a risk-acceptability judgment call this register does not make (Section 4 of `RISK_MANAGEMENT_PLAN.md`) |
| Potential harm (qualitative, not scored) | Same framing as above, though the underlying mechanism (fail-open vs. mis-computation) is materially different — noted, not scored |
| Severity | `GAP` |
| Probability | `GAP` |
| Risk evaluation (acceptable?) | `GAP` |

### HAZ-RENAL-5 — Composed dose ceiling not conservative (wrong bound wins)

| Field | Value |
|---|---|
| Source | REQ-RENAL-5, `metadata.a.yaml`: "Bound composition against `dosage.dfy`'s existing ceiling: the more conservative of the two bounds provably wins, pinned to exactly one of the two inputs, not just bounded above by both" |
| Hazardous situation | Given an existing (non-renal) dose ceiling and a renally-derived ceiling, the composed result fails to equal the lower/more conservative of the two — e.g. bounded above by both inputs without actually being pinned to either, leaving room for a value stricter than intended or looser than either bound alone |
| Risk control measure | `ComposedCeiling`'s pinning clause (`result == existingCeiling \|\| result == renalCeiling`, combined with its two `<=` bounds) forces the minimum by cases — proven, `renal_adjustment_stp_suite.dfy` / `raw_dafny_output_stp_suite_renal.txt`. **A real gap was found and fixed here, not merely designed correctly the first time**: Gate C4's STP suite (2026-07-09) found the *original* spec's two `<=` bounds and `AssessRenalFunction`'s two variant-only clauses did not actually pin the exact result — a REJECT lemma assuming a wrong candidate value **failed to verify** against the original, underconstrained spec (preserved as `renal_adjustment_underconstrained.dfy`, the failing capture is `raw_dafny_output_stp_suite_against_underconstrained_renal.txt`, `0 verified, 4 errors`). Fixed by adding the pinning clauses; re-verified clean, full STP suite (44 lemmas, ACCEPT and REJECT) now passes |
| Known, named residual | None currently identified — this is the one requirement in this register whose original spec gap was caught and closed by the pipeline itself (Gate C4), not left open |
| Potential harm (qualitative, not scored) | An incorrectly composed ceiling could either under-protect (looser than intended) or over-restrict (stricter than clinically appropriate) — both directions named, not assumed to be equally likely or equally severe |
| Severity | `GAP` |
| Probability | `GAP` |
| Risk evaluation (acceptable?) | `GAP` |

### HAZ-RENAL-6 — Rapidly changing renal function (AKI) treated as a stable, authoritative single value

| Field | Value |
|---|---|
| Source | REQ-RENAL-6, `metadata.a.yaml`: "Reassessment flag on rapidly changing renal function (AKI) — a single value must not be treated as authoritative in that situation." MHRA-sourced |
| Hazardous situation | A patient in acute kidney injury (rapidly changing renal function) has a single renal-function value fed into this kernel and treated with the same confidence as a stable patient's value — the kernel has no mechanism to flag staleness or rate-of-change |
| Risk control measure | **None — not yet formalized as a Dafny signature.** `traceability_matrix.a.md`: `intended_method: PROVEN`, `realized: GAP` |
| Known, named residual | Formalizing this would likely require a different input shape entirely (a value plus a timestamp/trend, not a bare number) — a real design question for whenever this is built, not a small addition to the current signature |
| Potential harm (qualitative, not scored) | Same framing as HAZ-RENAL-3/4 |
| Severity | `GAP` |
| Probability | `GAP` |
| Risk evaluation (acceptable?) | `GAP` |

### HAZ-RENAL-7 — Non-BSA-normalized eGFR needed but not used, at extremes of body weight for narrow-therapeutic-index drugs

| Field | Value |
|---|---|
| Source | REQ-RENAL-7, `metadata.a.yaml`: "For narrow-therapeutic-index drugs on the eGFR branch, BSA-nonindexed eGFR (mL/min, not mL/min/1.73m²) may be needed at extremes of body weight. Named, sourced (KDIGO Practice Point 4.2.4)" |
| Hazardous situation | A narrow-therapeutic-index drug is dosed using the standard BSA-normalized eGFR for a patient at a weight extreme, where KDIGO's own guidance says the normalized value can be clinically misleading relative to the non-normalized figure |
| Risk control measure | **None — not yet formalized as a Dafny signature.** `traceability_matrix.a.md`: `intended_method: PROVEN`, `realized: GAP` |
| Known, named residual | The narrowest-scoped of the four prose-only requirements (only applies to narrow-therapeutic-index drugs at weight extremes) — worth confirming with a clinical SME whether this is lower relative priority than HAZ-RENAL-3/4/6, not assumed here |
| Potential harm (qualitative, not scored) | Same framing as HAZ-RENAL-3/4/6 |
| Severity | `GAP` |
| Probability | `GAP` |
| Risk evaluation (acceptable?) | `GAP` |

### HAZ-RENAL-8 — Drug-classification flags supplied incorrectly or by an unspecified process

| Field | Value |
|---|---|
| Source | REQ-RENAL-8, `metadata.a.yaml`: `SelectFormula`'s boolean drug-classification inputs (DOAC / nephrotoxic / narrow-therapeutic-index) are caller-supplied, a deliberate, permanent trust boundary — MHRA's own drug lists are illustrative, not closed or exhaustive |
| Hazardous situation | The caller supplies a wrong, stale, or incomplete classification flag for a given drug — `SelectFormula`'s own correctness (HAZ-RENAL-2) is irrelevant if the flags feeding it are wrong, since the function is proven correct *given* its inputs, not proven to validate them |
| Risk control measure | **The trust boundary itself is settled and permanent, not something this register or a future proof will close** — hardcoding MHRA's illustrative drug lists into a "proven" artifact would embed a false-completeness claim. What remains genuinely open is *who* populates the flags operationally (clinician form / EHR lookup / static versioned list) — a real-world process decision, actively being gathered as of 2026-07-11, deliberately parked as an explicit `GAP` rather than guessed at |
| Known, named residual | Even once the operational process is decided, it resolves to a `DECLARED` process fact, not a Dafny proof target — contrast REQ-RENAL-3/4/6/7 above, which are aiming at eventual formalization. This hazard's risk control is fundamentally procedural/organizational, not mechanical |
| Potential harm (qualitative, not scored) | A wrong classification flag could route a patient through the wrong formula-selection branch entirely, compounding with HAZ-RENAL-2 rather than being an independent failure mode |
| Severity | `GAP` |
| Probability | `GAP` |
| Risk evaluation (acceptable?) | `GAP` |

---

## 3. Explicitly out of scope (named, not omitted)

Unlike `dosage_calculator`'s hazard table (a full-pump analysis this
kernel addresses a narrow slice of), `renal_adjustment`'s `REQ-RENAL-*`
list already covers most of what this device's own sources name as
hazard-relevant. What's genuinely outside this device's scope entirely
— not deferred, not a `GAP` row, just never this device's job:

- **Per-drug numeric dosing tables downstream of the composed
  ceiling** — this kernel produces a *ceiling*, not a final per-drug
  dose; which specific mg figure a given drug's dosing table yields
  under that ceiling is `dosage_calculator`'s domain (or a real
  per-drug table this repo hasn't built), not `renal_adjustment`'s.
- **Input measurement quality** — creatinine assay error, weight
  measurement error, and similar data-quality hazards upstream of this
  kernel's inputs are not addressed; `AssessRenalFunctionFromInputs`
  takes raw inputs as given, the same trust boundary as REQ-RENAL-8's
  classification flags but for numeric inputs instead of booleans.
- **Non-renal contraindications** — drug interactions, hepatic
  function, or other non-renal contraindications are entirely outside
  this device's stated `intended_use` ("stage renal function, select
  formula, compose bound") — see `drug_interaction_checker` for the
  device that addresses drug-drug interaction hazards specifically.
- **Pregnancy- and paediatric-specific renal formulas** — KDIGO 2024
  and the MHRA formula-selection source this device draws from are
  adult-focused; no paediatric or pregnancy-specific staging/formula
  guidance was sourced or is modelled here.

---

## 4. Change log

| Date | Change | Reason |
|---|---|---|
| 2026-07-14 | Initial draft: 8 hazard entries (one per `REQ-RENAL-*`, including 1a), explicitly-out-of-scope section | Second hazard register in this repo, extending the approach from `dosage_calculator`. Built from a genuinely different source shape — no published numbered hazard table exists for this device, so hazard identification draws on `metadata.a.yaml`'s sourced requirement text and `GATE_1C_AUDIT.md`'s own hand-trace findings (which already name concrete failure modes) instead |

---

*Hazard identification (Section 2's `Source`, `Hazardous situation`,
and `Risk control measure` fields) is drawn directly from this repo's
own committed evidence (`metadata.a.yaml`, `GATE_1C_AUDIT.md`,
`traceability_matrix.a.md`, `nl_confirmation_renal_adjustment_dfy.md`,
`raw_dafny_output_*.txt` captures) — not fabricated. Severity,
probability, and risk-acceptability evaluation are explicit `GAP`s,
same discipline as `RISK_MANAGEMENT_PLAN.md` and the
`dosage_calculator` register: this register identifies hazards; it
does not yet estimate or evaluate risk, per ISO 14971:2019 clauses
5.5, 6, and 8, which require the clinical SME and manufacturer policy
`RISK_MANAGEMENT_PLAN.md` Sections 2 and 4 still name as unassigned.*
