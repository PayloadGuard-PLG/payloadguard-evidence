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
(`RISK_MANAGEMENT_PLAN.md` Section 2), and each hazard row below now
carries a **draft severity/probability/evaluation proposal**, reasoned
from this register's own real evidence per `RISK_MANAGEMENT_PLAN.md`
Sections 4–5 — explicitly a draft, not a confirmed SME determination.
Every `Severity`/`Probability`/`Risk evaluation` field says so
directly rather than presenting proposed values as settled.

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
| Severity | **STALE, pending re-derivation — not re-scored here.** The prior `DRAFT: S2` value was justified by the clinician-awareness residual, which has moved to `HAZ-GIP-1.2b`. Re-scoring this narrowed, proof-closed pathway is a Finding 3/R3 question (severity model still open — see `RISK_MANAGEMENT_FINDINGS.md`), not resolved by this restructuring |
| Probability | **STALE, pending re-derivation** — same reason as Severity above |
| Risk evaluation (acceptable?) | **STALE, pending re-derivation** — cannot be evaluated honestly until Severity/Probability are re-derived under whichever model Finding 3/R3 settles on |

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
| Severity | **GAP — not scored.** Blocked on the same open Finding 3/R3 question as `HAZ-GIP-1.2` above (which severity model applies), plus genuine clinical-judgment input this repo's assistant cannot supply |
| Probability | **GAP — deliberately not defaulted to P5.** `RISK_MANAGEMENT_FINDINGS.md` Finding 5: this is arguably exactly TR 24971 §5.5.3's target case (a "software failure"-class hazard with zero evidence of any kind, not merely an unmeasured one), for which the standard's own guidance is to evaluate on severity alone rather than assume worst-case probability and run the full matrix. Whether §5.5.3 applies here, versus the plan's current P5-plus-matrix policy, versus a two-track approach, is Finding 5's open Option A/B/C question — presuming P5 here would prejudge that question, not just restructure the register |
| Risk evaluation (acceptable?) | **GAP — cannot be evaluated** until both Finding 3/R3 (severity model) and Finding 5 (evaluation procedure for this specific hazard class) are decided. This row is the concrete reason those two open questions matter in practice — not an abstract choice |

### HAZ-GIP-1.14 — Improper flow (bleed back / reflux within device)

| Field | Value |
|---|---|
| GIP v1.0 source | HID 1.14, §2.4.1. Verbatim: Hazard "Improper flow", Type "FRN", Cause "Bleed back; reflux within device", mitigation "Flow sensor", Safety Req "1.8". `FRN` = FDA Product Code for "Infusion Pump" (21 CFR 880.5725) — within the GIP taxonomy, general-purpose volumetric infusion pumps, distinct from the `All` tag used elsewhere — resolved 2026-07-05, `sources/README.md` and `README.md`'s own "`FRN` pump-type tag: RESOLVED" section. Confidence caveat carried forward, not dropped: well-supported but not yet independently re-verified against the raw §2.4.1 text |
| Cross-reference | `THR-GIP-1-14` (`metadata.a.yaml`) |
| Hazardous situation at this kernel's scope | Modelled as a fault input per GIP Safety Requirement 1.8.1 ("Continuous reverse delivery shall not be possible during normal use or a single-fault condition," IEC 601-2-24): a negative `infusion_rate_ml_per_hr` (hardware reverse-flow fault) |
| Risk control measure | REQ-GIP-1-8-1: any negative rate yields exactly zero delivered dose — proven for both the ordinary and float-overflow-magnitude negative-rate cases (`ordinary_negative_rate_clamps_to_zero`, `overflow_negative_rate_clamps_to_zero`), plus CrossHair and Dafny `CalculateHourlyDose`. The docstring itself notes the negative check deliberately runs *before* the finiteness check, so an overflowing negative product clamps to zero rather than being misread as a positive overflow — `dosage_naive_widening.py` preserves the wrong-order variant this guards against, as a named negative example, not a hypothetical |
| Known, named residual | None currently identified beyond the general `system_scope` alarm-signal gap — REQ-GIP-1-8-1 has no separate system-scope split in `metadata.a.yaml`, unlike REQ-GIP-1-4-12; worth confirming, not assuming, if this register is extended |
| Potential harm (qualitative, not scored) | Reverse delivery of drug is a materially different failure mode from over/under-dose — GIP's own Type tag ("FRN," resolved to general-purpose volumetric pumps, see above) suggests it may not apply to every pump subtype this kernel could underlie; harm severity is left to clinical judgment, same as the others, not assumed comparable to HAZ-GIP-1.2/1.3 |
| Severity | **DRAFT: S1 — Negligible.** The only hazard in this register whose mitigation is complete and Dafny-**proven**, not bounded-checked: exactly zero delivered dose on any negative-rate fault, both ordinary and overflow-magnitude. Proposed, not confirmed |
| Probability | **DRAFT: P5 (worst-case default, not a frequency estimate)**, applied for consistency even though S1's evaluation doesn't depend on it |
| Risk evaluation (acceptable?) | **DRAFT: Acceptable** at any probability, per §4.3's matrix — the one hazard in this register that clears the draft bar today |

### HAZ-DOSE-003 — Non-finite or out-of-range calculation result

| Field | Value |
|---|---|
| GIP v1.0 source | **None.** `metadata.a.yaml`'s own `REQ-DOSE-003` text says so directly: "DECLARED - not sourced from GIP v1.0, which does not address floating-point overflow at the implementation level." Included here for completeness of this kernel's real risk-control coverage, not because a primary hazard source names it — flagged as the one row in this register without a GIP `HID`, not silently presented as equivalent to the other three |
| Hazardous situation at this kernel's scope | An extreme input combination (e.g. `concentration_mg_per_ml` near `1e308`, per the overflow probe fixtures) causes `raw_dose` to overflow to a non-finite intermediate value. **Correction (caught in PR #46 review): the non-finite value does not propagate out of the function.** `calculate_hourly_dose` (`dosage.py:34-38`) checks `not math.isfinite(raw_dose)` and clamps to `max_safe_dose_mg_per_hr` in that case — the same branch, and the same output, as an ordinary in-range over-limit dose. The real hazardous situation is narrower: an overflowing/erroneous input is silently indistinguishable, at this kernel's output alone, from a legitimate request for exactly the maximum safe dose — no distinct signal marks "input was extreme/malformed" versus "input legitimately hit the ceiling" |
| Risk control measure | CrossHair bounded search + concrete test `normal_in_range_exact_value` — **no Dafny proof exists for this row**, stated plainly rather than implied at the same strength as the other three (`traceability_matrix.a.md`'s own `intended_method: BOUNDED_CHECKED`, not `PROVEN`). The finiteness clamp itself is real, exercised code (`dosage.py:37`), just not formally proven |
| Known, named residual | Weaker evidence strength than the GIP-sourced hazards above — a bounded symbolic search is not a proof that the finiteness clamp holds for every input, only that no counterexample was found within the recorded bounds. Separately: this kernel gives no distinguishing signal between an overflow-driven clamp and an ordinary at-ceiling dose (see above) — whether that conflation itself needs a distinct alarm/log path is a real open design question, not resolved here |
| Potential harm (qualitative, not scored) | Not a runaway/unbounded dose reaching delivery (the clamp prevents that) — the residual concern is a *masking* one: an erroneous or extreme input is silently treated as an ordinary maximum-dose request, with no error signal distinguishing the two, which could obscure a real upstream data problem rather than surface it |
| Severity | **DRAFT: S2 — Minor**, same class as HAZ-GIP-1.2/1.3 (a masked anomaly, not an unsafe dose) — with the weaker `BOUNDED_CHECKED`, not `PROVEN`, evidence strength noted as a reason this proposal should get extra scrutiny, not less. Proposed, not confirmed |
| Probability | **DRAFT: P5 (worst-case default, not a frequency estimate)** — especially warranted here given the weaker evidence strength |
| Risk evaluation (acceptable?) | **DRAFT: Unacceptable**, same reasoning as HAZ-GIP-1.2/1.3 |

---

## 3. Explicitly out of scope (named, not omitted)

The GIP v1.0 hazard table (§2.4, all eight categories: Operational,
Environmental, Electrical, Hardware, Software, Mechanical, Biological/
Chemical, Use) enumerates roughly 85 hazards. This kernel addresses
exactly the four rows above. Representative examples of what is **not**
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

---

*Hazard identification (Section 2's `GIP v1.0 source`, `Cross-reference`,
`Hazardous situation`, and `Risk control measure` fields) is drawn
directly from `sources/gip-v1.0-hazard-analysis.md` and this repo's own
committed evidence (`metadata.a.yaml`, `traceability_matrix.a.md`,
`dosage.py`'s own docstring). Severity, probability, and risk-
acceptability evaluation are, as of 2026-07-14, a **draft proposal**
reasoned from that same real evidence per `RISK_MANAGEMENT_PLAN.md`
Sections 4–5 — not fabricated, and not yet a confirmed SME
determination either. Every value above is marked `DRAFT` for exactly
that reason; none carries authority until Steven, the named Clinical
SME (`RISK_MANAGEMENT_PLAN.md` Section 2), reviews and confirms it.*
