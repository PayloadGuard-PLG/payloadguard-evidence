# Hazard Register — Generic Infusion Pump: Dose-Limit Safety Kernel (POC)

**Document ID:** HZ-GIP-001
**Part of the risk management file** per ISO 14971:2019 clause 4.5 —
this is the risk *analysis* content (clause 5.4 hazard identification)
`RISK_MANAGEMENT_PLAN.md`'s Section 8 named as not yet existing. It is
the first such register built in this repo, for the one worked example
whose primary source is itself a formal hazard analysis
(`sources/gip-v1.0-hazard-analysis.md`, the GIP v1.0 project,
Arney/Jetley/Jones/Lee/Ray/Sokolsky/Zhang, 2009), unlike the other two
examples' clinical-guideline sources.

**Status:** DRAFT | Version: 0.2 | Last reviewed: 2026-07-14

**What this register does, and does not, complete.** ISO 14971:2019
clause 5.4 (identification of hazards and hazardous situations) and
part of clause 5.5 (the qualitative consequence description) are real
here — every hazard row below is a real GIP v1.0 hazard, cited by its
own `HID`, cross-referenced against this kernel's actual scope, not
invented. **Updated 2026-07-14:** Steven is now the named Clinical SME
(`RISK_MANAGEMENT_PLAN.md` Section 2). **Updated 2026-07-15
(`RISK_MANAGEMENT_FINDINGS.md` Finding 3/R3 resolved, Option 3):**
severity is now defined by consequence alone, not evidence strength —
the 2026-07-14 severity values below were invalidated by that finding,
not merely superseded, since they measured proof strength rather than
real-world consequence. Every hazard's `Severity` is now an explicit
`GAP` pending Steven's clinical scoring; `Probability` reverts to
`RISK_MANAGEMENT_PLAN.md` §4.2's standing worst-case default policy
for every hazard **except `HAZ-GIP-1.2b`**, whose probability stays
`GAP` by deliberate design (Finding 5, unaffected by R3 either way —
see that row below); `Risk evaluation` is `GAP` for every hazard,
cascading from `Severity`. `RISK_MANAGEMENT_PLAN.md` §4.1 now also
carries an explicit "evidence artifact" citation per hazard — the real
proof/bound/test that grounds each hazard's probability side, kept
separate from the (still-open) severity question rather than folded
into it.

---

## 1. Scope of this register

Covers only the hazards `dosage.py::calculate_hourly_dose` /
`dosage.dfy::CalculateHourlyDose` actually participate in mitigating,
per this kernel's own `intended_use`: computing a safe hourly infusion
dose, clamped to a configured maximum, from patient/drug parameters.
This is a narrow slice of GIP v1.0's full ~85-hazard table (Section
2.4, all eight categories) — the kernel does not sense flow, detect
occlusion, manage batteries, run POST checks, or handle any hardware/
electrical/environmental hazard. Listing only the in-scope subset here
is a scope decision, not an oversight — Section 3 below names what's
explicitly excluded and why, so this register cannot be misread as
covering the full pump.

---

## 2. Hazard entries

### HAZ-GIP-1.2 — Overinfusion (dose limit exceeded via bolus requests) — kernel-scope delivery pathway

**Narrowed 2026-07-15** (`RISK_MANAGEMENT_FINDINGS.md` Finding 4): this
row previously named "Overinfusion" while its own `Known, named
residual` and `Severity` fields already described a different, still-
open situation (clinician awareness, not delivered dose). Split, not
renamed — this row now covers only the pathway `calculate_hourly_dose`
actually proves closed; the real open residual moved to
`HAZ-GIP-1.2b` below.

| Field | Value |
|---|---|
| GIP v1.0 source | HID 1.2, `sources/gip-v1.0-hazard-analysis.md` §2.4.1. Verbatim: Hazard "Overinfusion", Type "All", Cause "Dose limit exceeded due to too many bolus requests", GIP's own stated mitigation "Flow sensor", GIP Safety Req "1.4, 3.4.6" |
| Cross-reference | This device's existing STRIDE threat entry `THR-GIP-1-2` (`metadata.a.yaml`) cites the same GIP hazard under a different discipline (security threat modeling, not clinical hazard analysis) — see `RISK_MANAGEMENT_PLAN.md` Section 1 for why these are kept distinct, not merged. See also `HAZ-GIP-1.2b` for the split-out residual. |
| Hazardous situation at this kernel's scope (narrowed) | A bolus request, when converted to an hourly dose by `calculate_hourly_dose`, would produce a raw dose exceeding `max_safe_dose_mg_per_hr` **before clamping** — the pathway this kernel's output is proven to close, not the clinician-awareness question |
| Risk control measure | REQ-GIP-1-4-12, `kernel_scope`: the kernel detects the over-limit condition and returns it via a clamped output value, so the *delivered* dose never exceeds `max_safe_dose_mg_per_hr`. Formally verified — Dafny `CalculateHourlyDose` (`raw_dafny_output.txt`), CrossHair bounded search, concrete test `kernel_detects_bolus_limit_exceeded` (all three per `traceability_matrix.a.md`) |
| Known, named residual (narrowed) | None at kernel scope for the delivered-dose question itself — the clamp is proven for every input this kernel accepts. The `system_scope` question (whether a clinician is ever alerted that a clamp fired) is a different hazard mechanism, moved to `HAZ-GIP-1.2b` |
| Potential harm (qualitative, not scored) | Per `metadata.a.yaml`'s own `classification_rationale`: "failure could contribute to a non-serious over- or under-dose given clinician oversight" — reused verbatim rather than inventing new harm language; applies to the delivered-dose pathway this row now covers |
| Severity | **GAP — pending Steven's consequence-based scoring** (`RISK_MANAGEMENT_PLAN.md` §4.1, R3 resolved 2026-07-15, Option 3). The prior `DRAFT: S2` value was justified by the clinician-awareness residual, which moved to `HAZ-GIP-1.2b`, and was invalid regardless — it measured evidence strength, not consequence. Not a regression: no valid severity value existed for this row before either |
| Probability | **P5 — worst-case default**, per `RISK_MANAGEMENT_PLAN.md` §4.2's standing policy (no field data exists). Unaffected by R3 — the strong Dafny/CrossHair/concrete-test evidence for this pathway (Risk control measure, above) is now correctly read as backing this field, not `Severity`, though whether it should ever justify a lower band than the conservative default remains a separate, unresolved question (§4.2) |
| Risk evaluation (acceptable?) | **GAP — cannot be evaluated** until Severity is scored above; `RISK_MANAGEMENT_PLAN.md` §4.3's matrix has nothing to look up otherwise |

### HAZ-GIP-1.3 — Overinfusion (bolus volume/concentration too high) — kernel-scope delivery pathway

**Narrowed 2026-07-15**, same restructuring and same reason as
`HAZ-GIP-1.2` above: this row previously named "Overinfusion" while its
own residual/severity fields already described the split-out
clinician-awareness situation now covered by `HAZ-GIP-1.2b`. This is a
narrowing, not a retirement — the row, its GIP `HID 1.3` traceability
anchor, and its distinct cause text all remain.

| Field | Value |
|---|---|
| GIP v1.0 source | HID 1.3, same table. Verbatim: Hazard "Overinfusion", Type "All", Cause "(Programmed) Bolus volume/concentration too high", mitigation "Drug library", Safety Req "1.4, 3.4.6" |
| Cross-reference | `THR-GIP-1-3` (`metadata.a.yaml`). See also `HAZ-GIP-1.2b` for the split-out residual |
| Hazardous situation at this kernel's scope (narrowed) | A high `concentration_mg_per_ml` or `infusion_rate_ml_per_hr` input drives the raw computed hourly dose above `max_safe_dose_mg_per_hr` **before clamping** — **the kernel does not distinguish this cause from HAZ-GIP-1.2's** (both collapse to the same detected over-limit condition; `calculate_hourly_dose` has no notion of "too many bolus requests" vs. "one bolus too large," only the resulting dose value). Stated explicitly rather than silently implying two independently-covered pathways |
| Risk control measure | Same as HAZ-GIP-1.2 — REQ-GIP-1-4-12, same evidence: the kernel detects the over-limit condition and clamps, so the *delivered* dose never exceeds `max_safe_dose_mg_per_hr` |
| Known, named residual (narrowed) | None at kernel scope for the delivered-dose question itself, same as HAZ-GIP-1.2. The `system_scope` clinician-awareness question moved to `HAZ-GIP-1.2b` |
| Potential harm (qualitative, not scored) | Same as HAZ-GIP-1.2 |
| Severity | **GAP — pending Steven's consequence-based scoring**, same reasoning as HAZ-GIP-1.2 above (R3 resolved 2026-07-15, Option 3) |
| Probability | **P5 — worst-case default**, same reasoning as HAZ-GIP-1.2 above |
| Risk evaluation (acceptable?) | **GAP — cannot be evaluated**, same reasoning as HAZ-GIP-1.2 above |

### HAZ-GIP-1.2b — Overinfusion clamp fires with no proven clinician notification

**New 2026-07-15** (`RISK_MANAGEMENT_FINDINGS.md` Finding 4): the real,
still-open residual split out of `HAZ-GIP-1.2`/`HAZ-GIP-1.3` above —
this kernel proves a bad request gets clamped, not that anyone is ever
told it happened.

| Field | Value |
|---|---|
| GIP v1.0 source | Same underlying hazards as HID 1.2/1.3 (`sources/gip-v1.0-hazard-analysis.md` §2.4.1) — this row is not a new GIP-sourced hazard, it is the `system_scope` half of HID 1.2/1.3's own mitigation that this kernel's proof does not reach |
| Cross-reference | `HAZ-GIP-1.2`, `HAZ-GIP-1.3` (the narrowed, proof-closed rows this splits from). `HAZ-DOSE-003` has a related masking mechanism (an overflow-driven clamp is indistinguishable from a legitimate at-ceiling request) — cross-referenced, deliberately **not** folded into this row; whether they should be merged is Steven's register-organization call, not decided here |
| Hazardous situation at this kernel's scope | REQ-GIP-1-4-12's `system_scope` component — the full pump generating an audible/visual alarm *signal* once the kernel reports an over-limit clamp — is explicitly deferred to integration testing per `RISK_MANAGEMENT_PLAN.md` Section 1. This kernel's detection and clamping is proven; nothing in this repo proves a clinician is ever alerted that it fired |
| Risk control measure | **None at kernel scope.** No Dafny, CrossHair, or concrete-test artifact in `examples/dosage_calculator/` addresses alarm signaling — it requires an integrated pump system (hardware, firmware, alarm hardware, UI layer) this POC was never scoped to build, per `RISK_MANAGEMENT_PLAN.md`'s "Path to sign-off" section |
| Known, named residual | The complete residual *is* this row — no partial evidence exists to describe as "known but incomplete"; this is a full evidence gap, not a weak proof |
| Potential harm (qualitative, not scored) | A clinician who is never alerted that an over-limit request was clamped may not investigate the underlying cause (miscalculated order, programming error, etc.), potentially leading to a repeated or escalating dosing error — qualitative only, not scored |
| Severity | **GAP — not scored.** Finding 3/R3 is now resolved (Option 3, consequence-only model, 2026-07-15) — what remains blocking this field is purely the genuine clinical-judgment input this repo's assistant cannot supply, same as every other hazard in this register |
| Probability | **GAP — deliberately not defaulted to P5.** `RISK_MANAGEMENT_FINDINGS.md` Finding 5 (separate from, and not resolved by, Finding 3/R3): this is arguably exactly TR 24971 §5.5.3's target case (a "software failure"-class hazard with zero evidence of any kind, not merely an unmeasured one), for which the standard's own guidance is to evaluate on severity alone rather than assume worst-case probability and run the full matrix. Whether §5.5.3 applies here, versus the plan's current P5-plus-matrix policy, versus a two-track approach, is Finding 5's open Option A/B/C question — presuming P5 here would prejudge that question |
| Risk evaluation (acceptable?) | **GAP — cannot be evaluated** until both Severity (above, Steven's clinical scoring) and Finding 5 (evaluation procedure for this specific hazard class) are resolved. This row is the concrete reason Finding 5 matters in practice — not an abstract choice |

### HAZ-GIP-1.14 — Improper flow (bleed back / reflux within device)

| Field | Value |
|---|---|
| GIP v1.0 source | HID 1.14, §2.4.1. Verbatim: Hazard "Improper flow", Type "FRN", Cause "Bleed back; reflux within device", mitigation "Flow sensor", Safety Req "1.8". `FRN` = FDA Product Code for "Infusion Pump" (21 CFR 880.5725) — within the GIP taxonomy, general-purpose volumetric infusion pumps, distinct from the `All` tag used elsewhere — resolved 2026-07-05, `sources/README.md` and `README.md`'s own "`FRN` pump-type tag: RESOLVED" section. Confidence caveat carried forward, not dropped: well-supported but not yet independently re-verified against the raw §2.4.1 text |
| Cross-reference | `THR-GIP-1-14` (`metadata.a.yaml`) |
| Hazardous situation at this kernel's scope | Modelled as a fault input per GIP Safety Requirement 1.8.1 ("Continuous reverse delivery shall not be possible during normal use or a single-fault condition," IEC 601-2-24): a negative `infusion_rate_ml_per_hr` (hardware reverse-flow fault) |
| Risk control measure | REQ-GIP-1-8-1: any negative rate yields exactly zero delivered dose — proven for both the ordinary and float-overflow-magnitude negative-rate cases (`ordinary_negative_rate_clamps_to_zero`, `overflow_negative_rate_clamps_to_zero`), plus CrossHair and Dafny `CalculateHourlyDose`. The docstring itself notes the negative check deliberately runs *before* the finiteness check, so an overflowing negative product clamps to zero rather than being misread as a positive overflow — `dosage_naive_widening.py` preserves the wrong-order variant this guards against, as a named negative example, not a hypothetical |
| Known, named residual | None currently identified beyond the general `system_scope` alarm-signal gap — REQ-GIP-1-8-1 has no separate system-scope split in `metadata.a.yaml`, unlike REQ-GIP-1-4-12; worth confirming, not assuming, if this register is extended |
| Potential harm (qualitative, not scored) | Reverse delivery of drug is a materially different failure mode from over/under-dose — GIP's own Type tag ("FRN," resolved to general-purpose volumetric pumps, see above) suggests it may not apply to every pump subtype this kernel could underlie; harm severity is left to clinical judgment, same as the others, not assumed comparable to HAZ-GIP-1.2/1.3 |
| Severity | **GAP — pending Steven's consequence-based scoring** (R3 resolved 2026-07-15, Option 3). This row's proof — the strongest evidence artifact in this register — no longer justifies `S1` by itself: Finding 3 found that reasoning invalid (a proof of unreachability is a probability claim, not a severity one). What would happen to a patient if reverse delivery *did* reach them, independent of how strongly this kernel proves it doesn't, is the real, still-open question |
| Probability | **P5 — worst-case default**, per §4.2's standing policy, though this hazard has the strongest probability-side evidence in the register: Dafny-**proven** exactly zero delivered dose on any negative-rate fault, both ordinary and overflow-magnitude. Whether evidence this strong should ever override the conservative default remains a separate, unresolved question (§4.2) |
| Risk evaluation (acceptable?) | **GAP — cannot be evaluated** until Severity is scored above. No longer `Acceptable`: that value was computed from the same invalid evidence-strength severity reasoning R3 replaced, not a real consequence-based evaluation |

### HAZ-DOSE-003 — Non-finite or out-of-range calculation result

| Field | Value |
|---|---|
| GIP v1.0 source | **None.** `metadata.a.yaml`'s own `REQ-DOSE-003` text says so directly: "DECLARED - not sourced from GIP v1.0, which does not address floating-point overflow at the implementation level." Included here for completeness of this kernel's real risk-control coverage, not because a primary hazard source names it — flagged as the one row in this register without a GIP `HID`, not silently presented as equivalent to the other three |
| Hazardous situation at this kernel's scope | An extreme input combination (e.g. `concentration_mg_per_ml` near `1e308`, per the overflow probe fixtures) causes `raw_dose` to overflow to a non-finite intermediate value. **Correction (caught in PR #46 review): the non-finite value does not propagate out of the function.** `calculate_hourly_dose` (`dosage.py:34-38`) checks `not math.isfinite(raw_dose)` and clamps to `max_safe_dose_mg_per_hr` in that case — the same branch, and the same output, as an ordinary in-range over-limit dose. The real hazardous situation is narrower: an overflowing/erroneous input is silently indistinguishable, at this kernel's output alone, from a legitimate request for exactly the maximum safe dose — no distinct signal marks "input was extreme/malformed" versus "input legitimately hit the ceiling" |
| Risk control measure | CrossHair bounded search + concrete test `normal_in_range_exact_value` — **no Dafny proof exists for this row**, stated plainly rather than implied at the same strength as the other three (`traceability_matrix.a.md`'s own `intended_method: BOUNDED_CHECKED`, not `PROVEN`). The finiteness clamp itself is real, exercised code (`dosage.py:37`), just not formally proven |
| Known, named residual | Weaker evidence strength than the GIP-sourced hazards above — a bounded symbolic search is not a proof that the finiteness clamp holds for every input, only that no counterexample was found within the recorded bounds. Separately: this kernel gives no distinguishing signal between an overflow-driven clamp and an ordinary at-ceiling dose (see above) — whether that conflation itself needs a distinct alarm/log path is a real open design question, not resolved here |
| Potential harm (qualitative, not scored) | Not a runaway/unbounded dose reaching delivery (the clamp prevents that) — the residual concern is a *masking* one: an erroneous or extreme input is silently treated as an ordinary maximum-dose request, with no error signal distinguishing the two, which could obscure a real upstream data problem rather than surface it |
| Severity | **GAP — pending Steven's consequence-based scoring** (R3 resolved 2026-07-15, Option 3). The prior `DRAFT: S2` value reasoned from this row's weaker (`BOUNDED_CHECKED`, not `PROVEN`) evidence strength — invalid under the same finding as every other row, regardless of which way the evidence-strength comparison to `HAZ-GIP-1.2`/`1.3` cut |
| Probability | **P5 — worst-case default**, per §4.2's standing policy — especially conservative here given this row's probability-side evidence is permanently capped at `BOUNDED_CHECKED` (see `RISK_MANAGEMENT_PLAN.md`'s "Path to sign-off" section for why that ceiling is structural, not a gap waiting to be closed) |
| Risk evaluation (acceptable?) | **GAP — cannot be evaluated** until Severity is scored above |

---

## 3. Explicitly out of scope (named, not omitted)

The GIP v1.0 hazard table (§2.4, all eight categories: Operational,
Environmental, Electrical, Hardware, Software, Mechanical, Biological/
Chemical, Use) enumerates roughly 85 hazards. This kernel addresses
exactly the five rows above (**corrected 2026-07-15**: said "four" until
this fix — stale since `HAZ-GIP-1.2b` split out, Finding 4; caught
while resolving Finding 3/R3, not separately reported). Representative
examples of what is **not**
addressed here, and why — not an exhaustive list, but enough to show
the exclusion is a real scope boundary, not a gap in this register's
diligence:

- **HID 1.1** (Overinfusion, programmed flow rate too high) — mitigated
  per GIP by the "Drug library," a prescribing/formulary control this
  kernel has no part of; `calculate_hourly_dose` takes the programmed
  rate as a trusted input, it does not validate it against a drug
  library.
- **HID 1.5–1.13, 1.16–1.28** (under-infusion, air-in-line, occlusion,
  reservoir state, priming, keypad state, etc.) — all require physical
  sensing (flow sensor, pressure sensor) this kernel has no access to;
  it is a pure numeric calculation over caller-supplied parameters.
- **Categories 2–8** (Environmental, Electrical, Hardware, Software,
  Mechanical, Biological/Chemical, Use hazards) — none of these are
  addressed by a dose-calculation function; they belong to the full
  device's hardware, firmware, and human-factors design, entirely
  outside `examples/dosage_calculator/`'s scope as stated in
  `RISK_MANAGEMENT_PLAN.md` Section 1.

---

## 4. Change log

| Date | Change | Reason |
|---|---|---|
| 2026-07-14 | Initial draft: 4 hazard entries (3 GIP-sourced, 1 DECLARED), scope section, out-of-scope section | First real hazard-register artifact in this repo, chosen as the easiest starting point because this device's primary source is itself a formal hazard analysis already partially cited in `metadata.a.yaml`'s STRIDE threat model — unlike the other two worked examples, which have no equivalent source |
| 2026-07-14 (later) | Draft severity/probability/evaluation proposal added to all 4 hazards; Steven assigned as Clinical SME | Direct instruction: "assign a clinical SME and start the severity/probability tables." Real finding: none of the 4 hazards reaches S3/S4 given what's actually proven (3 land at S2, 1 — the fully-proven reverse-delivery mitigation — lands at S1); 3 of 4 evaluate provisionally `Unacceptable` under the mandated worst-case probability default. All values marked DRAFT, pending Steven's confirmation, not self-declared as final |
| 2026-07-15 | `HAZ-GIP-1.2`/`HAZ-GIP-1.3` narrowed to the kernel-proven-closed delivery pathway; new `HAZ-GIP-1.2b` row split out for the real, still-open clinician-notification residual | Audit finding (`RISK_MANAGEMENT_FINDINGS.md` Finding 4, verified against `dosage.py`/`dosage.dfy` directly): the original rows named "Overinfusion" — a pathway this kernel proves closed — while their own residual/severity fields already described a different, open situation. Split, not renamed. `HAZ-GIP-1.2`/`1.3`'s Severity/Probability/Risk-evaluation values are marked stale, pending re-derivation, rather than silently carried over or newly re-scored — that re-scoring is Finding 3/R3's open question. `HAZ-GIP-1.2b`'s Probability is deliberately left `GAP`, not defaulted to P5, per Finding 5's newly-surfaced open question of whether TR 24971 §5.5.3 (severity-alone evaluation) applies to this specific inestimable-probability hazard. Both are register restructuring, not new judgment calls — the severity model, evaluation procedure, and actual scored values remain Steven's decisions |
| 2026-07-15 (later) | **Correction**: restored a standalone, narrowed `HAZ-GIP-1.3` entry | The first pass of the above restructuring collapsed `HAZ-GIP-1.2` and `HAZ-GIP-1.3` into a single narrowed `HAZ-GIP-1.2` row, silently dropping `HAZ-GIP-1.3`'s own GIP `HID 1.3` traceability anchor while `HAZ-GIP-1.2b` and several other documents still referenced it — a real correctness bug, caught by an automated PR review (Qodo) on PR #50, not self-caught. Fixed by restoring `HAZ-GIP-1.3` as its own narrowed row, parallel in structure to `HAZ-GIP-1.2`, per the review's own suggested Option 1 |
| 2026-07-15 (yet later) | Finding 3/R3 resolved: every hazard's `Severity` and `Risk evaluation` updated to explicit `GAP`; `Probability` reverted to the §4.2 default policy for every hazard except `HAZ-GIP-1.2b` (Finding 5, unaffected either way) | Direct instruction: "work through R3's severity model." Steven chose Option 3 (hybrid, `AskUserQuestion`) after Option 2 was eliminated on textual grounds (TR 24971 §5.5.4). The prior `DRAFT: S1`/`S2` values (including `HAZ-GIP-1.14`'s `Acceptable` evaluation) were withdrawn, not revised — they measured evidence strength, not real-world consequence, so no valid severity value existed for any hazard before this fix either. `RISK_MANAGEMENT_PLAN.md` §4.1 now carries the consequence-only band definitions and an explicit evidence-artifact citation per hazard |
| 2026-07-15 (later still) | **Correction**: fixed an overgeneralized "every hazard reverts to P5" claim (this file's intro, this change log's row above, `DEVLOG.md`) that didn't carve out `HAZ-GIP-1.2b`'s deliberate exception; split the §4.1 evidence-artifact table's merged `HAZ-GIP-1.2`/`HAZ-GIP-1.3` row into two; fixed a second, separate "four hazards"/"four rows" staleness instance in this file's own Section 3 (missed by the same-day R3 fix, which only caught the two instances in `RISK_MANAGEMENT_PLAN.md`) | Three real findings from an automated PR review (Qodo) on PR #53, not self-caught — confirmed directly against the files before fixing, same discipline as every other review response this session |

---

*Hazard identification (Section 2's `GIP v1.0 source`, `Cross-reference`,
`Hazardous situation`, and `Risk control measure` fields) is drawn
directly from `sources/gip-v1.0-hazard-analysis.md` and this repo's own
committed evidence (`metadata.a.yaml`, `traceability_matrix.a.md`,
`dosage.py`'s own docstring). Updated 2026-07-15: the severity **model**
(clause 5.5) is now real and consequence-only, per
`RISK_MANAGEMENT_FINDINGS.md` Finding 3/R3's resolution — every
hazard's severity **value** is an explicit `GAP` above, pending
Steven's clinical scoring, not a "draft proposal" in the sense the
2026-07-14 values were. That distinction matters: the old values were
actively invalid (measuring proof strength, not consequence), not
merely unconfirmed. None of the `GAP` values above carries authority
until Steven, the named Clinical SME (`RISK_MANAGEMENT_PLAN.md`
Section 2), scores them.*
