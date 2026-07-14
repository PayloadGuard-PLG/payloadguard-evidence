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

**Status:** DRAFT | Version: 0.1 | Last reviewed: 2026-07-14

**What this register does, and does not, complete.** ISO 14971:2019
clause 5.4 (identification of hazards and hazardous situations) and
part of clause 5.5 (the qualitative consequence description) are real
here — every hazard row below is a real GIP v1.0 hazard, cited by its
own `HID`, cross-referenced against this kernel's actual scope, not
invented. What remains `GAP`, deliberately, per the same discipline
`RISK_MANAGEMENT_PLAN.md` already established: severity classification,
probability estimation, and the acceptability evaluation (clauses 5.5's
quantitative half, 6, and 8) — all three require a named clinical SME
and manufacturer risk-acceptability policy that don't exist yet (see
`RISK_MANAGEMENT_PLAN.md` Sections 2 and 4).

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

### HAZ-GIP-1.2 — Overinfusion (dose limit exceeded via bolus requests)

| Field | Value |
|---|---|
| GIP v1.0 source | HID 1.2, `sources/gip-v1.0-hazard-analysis.md` §2.4.1. Verbatim: Hazard "Overinfusion", Type "All", Cause "Dose limit exceeded due to too many bolus requests", GIP's own stated mitigation "Flow sensor", GIP Safety Req "1.4, 3.4.6" |
| Cross-reference | This device's existing STRIDE threat entry `THR-GIP-1-2` (`metadata.a.yaml`) cites the same GIP hazard under a different discipline (security threat modeling, not clinical hazard analysis) — see `RISK_MANAGEMENT_PLAN.md` Section 1 for why these are kept distinct, not merged |
| Hazardous situation at this kernel's scope | A bolus request, when converted to an hourly dose by `calculate_hourly_dose`, would exceed `max_safe_dose_mg_per_hr` |
| Risk control measure | REQ-GIP-1-4-12, `kernel_scope`: the kernel detects the over-limit condition and returns it via a clamped output value. Formally verified — Dafny `CalculateHourlyDose` (`raw_dafny_output.txt`), CrossHair bounded search, concrete test `kernel_detects_bolus_limit_exceeded` (all three per `traceability_matrix.a.md`) |
| Known, named residual | REQ-GIP-1-4-12's `system_scope` (the full pump generating an audible/visual alarm *signal* once the kernel reports the condition) is explicitly deferred to integration testing — this kernel's detection is proven, but nothing yet proves a clinician would actually be alerted. Carried forward from `RISK_MANAGEMENT_PLAN.md` Section 1, not new information. |
| Potential harm (qualitative, not scored) | Per `metadata.a.yaml`'s own `classification_rationale`: "failure could contribute to a non-serious over- or under-dose given clinician oversight" — reused verbatim rather than inventing new harm language |
| Severity | `GAP` — pending clinical SME, `RISK_MANAGEMENT_PLAN.md` §4.1 |
| Probability | `GAP` — pending field data; interim worst-case policy per §4.4 |
| Risk evaluation (acceptable?) | `GAP` — pending §4.3 acceptance matrix |

### HAZ-GIP-1.3 — Overinfusion (bolus volume/concentration too high)

| Field | Value |
|---|---|
| GIP v1.0 source | HID 1.3, same table. Verbatim: Hazard "Overinfusion", Type "All", Cause "(Programmed) Bolus volume/concentration too high", mitigation "Drug library", Safety Req "1.4, 3.4.6" |
| Cross-reference | `THR-GIP-1-3` (`metadata.a.yaml`) |
| Hazardous situation at this kernel's scope | A high `concentration_mg_per_ml` or `infusion_rate_ml_per_hr` input drives the computed hourly dose above `max_safe_dose_mg_per_hr` — **the kernel does not distinguish this cause from HAZ-GIP-1.2's** (both collapse to the same detected over-limit condition; `calculate_hourly_dose` has no notion of "too many bolus requests" vs. "one bolus too large," only the resulting dose value). Stated explicitly rather than silently implying two independently-covered hazards. |
| Risk control measure | Same as HAZ-GIP-1.2 — REQ-GIP-1-4-12, same evidence |
| Known, named residual | Same `system_scope` gap as HAZ-GIP-1.2 |
| Potential harm (qualitative, not scored) | Same as HAZ-GIP-1.2 |
| Severity | `GAP` |
| Probability | `GAP` |
| Risk evaluation (acceptable?) | `GAP` |

### HAZ-GIP-1.14 — Improper flow (bleed back / reflux within device)

| Field | Value |
|---|---|
| GIP v1.0 source | HID 1.14, §2.4.1. Verbatim: Hazard "Improper flow", Type "FRN" (pump-type tag, undecoded in the extracted source text — see `sources/README.md`'s open question, also carried in `RISK_MANAGEMENT_PLAN.md` and `README.md`'s own "Open questions"), Cause "Bleed back; reflux within device", mitigation "Flow sensor", Safety Req "1.8" |
| Cross-reference | `THR-GIP-1-14` (`metadata.a.yaml`) — that entry already flags the same `FRN`-decode gap |
| Hazardous situation at this kernel's scope | Modelled as a fault input per GIP Safety Requirement 1.8.1 ("Continuous reverse delivery shall not be possible during normal use or a single-fault condition," IEC 601-2-24): a negative `infusion_rate_ml_per_hr` (hardware reverse-flow fault) |
| Risk control measure | REQ-GIP-1-8-1: any negative rate yields exactly zero delivered dose — proven for both the ordinary and float-overflow-magnitude negative-rate cases (`ordinary_negative_rate_clamps_to_zero`, `overflow_negative_rate_clamps_to_zero`), plus CrossHair and Dafny `CalculateHourlyDose`. The docstring itself notes the negative check deliberately runs *before* the finiteness check, so an overflowing negative product clamps to zero rather than being misread as a positive overflow — `dosage_naive_widening.py` preserves the wrong-order variant this guards against, as a named negative example, not a hypothetical |
| Known, named residual | None currently identified beyond the general `system_scope` alarm-signal gap — REQ-GIP-1-8-1 has no separate system-scope split in `metadata.a.yaml`, unlike REQ-GIP-1-4-12; worth confirming, not assuming, if this register is extended |
| Potential harm (qualitative, not scored) | Reverse delivery of drug is a materially different failure mode from over/under-dose — GIP's own Type tag ("FRN") suggests it may not apply to every pump subtype this kernel could underlie; harm severity is left to clinical judgment, same as the others, not assumed comparable to HAZ-GIP-1.2/1.3 |
| Severity | `GAP` |
| Probability | `GAP` |
| Risk evaluation (acceptable?) | `GAP` |

### HAZ-DOSE-003 — Non-finite or out-of-range calculation result

| Field | Value |
|---|---|
| GIP v1.0 source | **None.** `metadata.a.yaml`'s own `REQ-DOSE-003` text says so directly: "DECLARED - not sourced from GIP v1.0, which does not address floating-point overflow at the implementation level." Included here for completeness of this kernel's real risk-control coverage, not because a primary hazard source names it — flagged as the one row in this register without a GIP `HID`, not silently presented as equivalent to the other three |
| Hazardous situation at this kernel's scope | An extreme input combination (e.g. `concentration_mg_per_ml` near `1e308`, per the overflow probe fixtures) causes `raw_dose` to overflow to a non-finite value before clamping, which could silently propagate a `NaN`/`inf` dose figure rather than a bounded number |
| Risk control measure | CrossHair bounded search + concrete test `normal_in_range_exact_value` — **no Dafny proof exists for this row**, stated plainly rather than implied at the same strength as the other three (`traceability_matrix.a.md`'s own `intended_method: BOUNDED_CHECKED`, not `PROVEN`) |
| Known, named residual | Weaker evidence strength than the GIP-sourced hazards above — a bounded symbolic search is not a proof. If this kernel is ever extended with a Dafny-provable finiteness postcondition, this row should be revisited |
| Potential harm (qualitative, not scored) | An unbounded/non-finite dose value reaching a delivery layer, if one existed, would be a more severe failure mode than a correctly-clamped over-limit condition — this is a judgment call this register is flagging, not resolving; still `GAP` pending clinical/systems-engineering input, not just clinical |
| Severity | `GAP` |
| Probability | `GAP` |
| Risk evaluation (acceptable?) | `GAP` |

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

---

*Hazard identification (Section 2's `GIP v1.0 source`, `Cross-reference`,
`Hazardous situation`, and `Risk control measure` fields) is drawn
directly from `sources/gip-v1.0-hazard-analysis.md` and this repo's own
committed evidence (`metadata.a.yaml`, `traceability_matrix.a.md`,
`dosage.py`'s own docstring). Severity, probability, and risk-
acceptability evaluation are explicit `GAP`s, not fabricated — this
register identifies hazards; it does not yet estimate or evaluate risk,
per ISO 14971:2019 clauses 5.5, 6, and 8, which require the clinical
SME and manufacturer policy `RISK_MANAGEMENT_PLAN.md` Sections 2 and 4
still name as unassigned.*
