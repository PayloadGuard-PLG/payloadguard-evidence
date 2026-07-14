# Risk Management Plan — Generic Infusion Pump: Dose-Limit Safety Kernel (POC)

**Document ID:** RMP-GIP-001
**Risk Management File reference:** This plan is part of the risk
management file per ISO 14971:2019 clause 4.4. It does not itself
contain the hazard register, evaluation results, or risk management
report — those are separate documents this plan governs and
references, per clause 4.5's own traceability requirements for the
risk management file as a whole (neither of those documents exists yet
for this device — see Section 8).

**Status:** DRAFT | Version: 0.1 | Last reviewed: 2026-07-14

**Provenance:** Third and last of three plans built this session,
mirroring `examples/drug_interaction_checker/RISK_MANAGEMENT_PLAN.md`
and `examples/renal_adjustment/RISK_MANAGEMENT_PLAN.md` structurally.
The ISO 14971:2019 clause citations (4.4a–g, clause 1's exclusions)
were verified once against the real standard's verbatim text when the
first of the three plans was built; not re-verified per device, since
the citations describe the standard itself, not the device.

---

## 1. Scope (ISO 14971:2019 clause 4.4a)

**Device covered:** Generic Infusion Pump — Dose-Limit Safety Kernel
(POC) — `examples/dosage_calculator/`. This is this repo's original,
first-built worked example, and the only one of the three with a
kernel/system scope split named explicitly in its own requirements
(see below) and a companion STRIDE threat model.

**Intended use** (verbatim, from `metadata.a.yaml`'s
`device.intended_use`): Compute a safe hourly infusion dose from
patient and drug parameters, clamped so it never exceeds a configured
maximum safe dose.

**Life-cycle phases this plan governs:** Design and verification of
the dose-calculation *kernel* only — explicitly narrower than the full
infusion-pump system. This scoping is not this plan's own invention;
it is already load-bearing in the requirement text itself.
REQ-GIP-1-4-12 names a `kernel_scope` ("the kernel shall detect when a
bolus request would cause the computed hourly dose to exceed
`max_safe_dose_mg_per_hr`, and shall return that condition... via a
clamped output value" — alarm *detection* only) and a separately
tracked `system_scope` ("the full infusion pump system shall generate
an audible or visual... alarm signal" — alarm *generation*,
IEC 60601-1-8/62366-1 territory) that is explicitly deferred to
integration testing, not silently assumed covered. Production and
post-production sections (Section 7 below) are explicit placeholders
for the same reason: no manufacturing/integration pathway exists yet.

**What this plan does NOT cover:** Per ISO 14971 §1's own exclusions —
clinical decision-making in the context of a specific patient
encounter, and business risk management, are both out of scope by the
standard's own terms, not just this plan's. Separately, and specific
to this device: the alarm *signal* (system_scope above) is out of
scope for this plan until the integration phase exists — a plan scope
limit, not a standard exclusion.

**Related, but distinct, artifact already in place:** `metadata.a.yaml`
carries a STRIDE threat model (`THR-GIP-1-2`, `THR-GIP-1-3`,
`THR-GIP-1-14`, each mapped to a mitigating requirement). This is
security threat modeling, not ISO 14971 clinical/safety hazard
analysis — a different discipline with different vocabulary
(threat/asset/mitigation vs. hazard/hazardous situation/harm) that
happens to already exist for this device. Worth citing as a precedent
this plan should not conflate with the hazard register Section 8
below still needs, not treating one as a substitute for the other.

---

## 2. Roles and responsibilities (ISO 14971:2019 clause 4.4b)

| Role | Person | Responsibility |
|---|---|---|
| Risk Manager | *(not yet assigned)* | Owns this plan; approves hazard entries |
| Technical/Verification Lead | *(not yet assigned)* | Owns the mechanical evidence (CrossHair bounds, Dafny proofs, concrete tests, gate closures) that risk control claims cite |
| Clinical/Subject Matter Expert | *(not yet assigned)* | Reviews clinical plausibility of hazards and harms |

**GAP, stated explicitly rather than omitted:** no role above is
currently filled by a named person. `metadata.a.yaml`'s own
`classification_rationale` already flags this: the `B` safety
classification is `DECLARED`, not sourced — "GIP v1.0... does not
assign IEC 62304 classes or ISO 14971 severity/probability scores per
hazard... requires a manufacturer-specific ISO 14971 risk file before
this can be upgraded from DECLARED to sourced." This document is the
start of that file, not its completion.

---

## 3. Review requirements (ISO 14971:2019 clause 4.4c)

This repository already runs an out-of-cycle review trigger in
practice, ahead of this plan formalizing it — concrete precedent for
this example specifically: the 2026-07-05 Gate 1 review that split
REQ-GIP-1-4-12 into `kernel_scope`/`system_scope` rather than leaving
an ambiguous single scope claim, and the 2026-07-04 "Option A"
amendment that added the reverse-delivery fault model to
REQ-GIP-1-8-1.

Formalized as policy: any of the following triggers a hazard-register
review before the associated finding is closed —
- a spec-level scope change to `dosage.py::calculate_hourly_dose` or
  `dosage.dfy::CalculateHourlyDose`;
- a Gate C5 mutation-testing survivor appearing where none currently
  does (see Section 6 — this device's mutation-testing residual is
  currently zero, a genuinely different state from the other two
  worked examples, worth re-checking on any future spec change rather
  than assumed to stay zero);
- any change to the `kernel_scope`/`system_scope` split, since it is
  the one place this device's own requirement text already draws the
  exact boundary a hazard register needs;
- independent re-verification of the STRIDE threat model's
  `THR-GIP-1-14` `FRN` pump-type tag resolution against the raw GIP
  v1.0 §2.4.1 text — resolved 2026-07-05 (`README.md`'s "`FRN`
  pump-type tag: RESOLVED" section, `sources/README.md`), but that
  resolution's own stated caveat ("well-supported, but not yet
  independently re-verified against the raw source text") is still
  open. Correcting a stale claim here that mischaracterized this as an
  unresolved "open question" — caught during PR #46 review, fixed
  2026-07-14.

---

## 4. Risk acceptability criteria (ISO 14971:2019 clause 4.4d)

### 4.1 Severity bands

*(Fill these in only after clinical SME review — this table is a
structure, not a judgment call for an engineering-only draft to make
alone. GAP, stated explicitly: no clinical SME is assigned yet — see
Section 2.)*

Unlike the other two worked examples, this device's harm pathway is
partially physical, not purely informational: `calculate_hourly_dose`
directly produces the number an infusion pump would deliver, clamped
by this kernel's own logic — so severity bands should account for
over/under-infusion consequences directly, not just clinician
double-checking, while still respecting that alarm *signalling*
(the human-facing side) is explicitly out of this kernel's scope
(Section 1).

| Severity | Definition | Example specific to this device |
|---|---|---|
| S1 | *(not yet defined)* | e.g. a dose clamped correctly at the boundary, no delivery deviation |
| S2 | *(not yet defined)* | e.g. detection-only alarm condition raised but the system-layer signal is delayed/absent (system_scope gap), caught by other clinical process |
| S3 | *(not yet defined)* | e.g. an under/over-dose reaches delivery due to a kernel/system integration gap not yet built, requiring clinical intervention |
| S4 | *(not yet defined)* | e.g. reverse-delivery (REQ-GIP-1-8-1's fault case) or an unclamped over-dose contributes to a serious, non-recoverable adverse outcome |

### 4.2 Probability bands

*(Not yet defined — see 4.4 below for the interim fallback policy.)*

| Probability | Definition | Basis for estimate |
|---|---|---|
| P1 | *(not yet defined)* | |
| P2 | *(not yet defined)* | |
| P3 | *(not yet defined)* | |
| P4 | *(not yet defined)* | |
| P5 | *(not yet defined)* | |

### 4.3 Acceptance matrix

*(Not yet defined — depends on 4.1/4.2, which are themselves pending
clinical SME review. Marking each cell acceptable/unacceptable is a
manufacturer policy decision ISO 14971 deliberately does not make for
you — §1: "does not specify acceptable risk levels.")*

| Probability \ Severity | S1 | S2 | S3 | S4 |
|---|---|---|---|---|
| P5 | | | | |
| P4 | | | | |
| P3 | | | | |
| P2 | | | | |
| P1 | | | | |

### 4.4 Criteria for accepting risk when probability cannot be estimated

This is a pre-market POC with no field usage data. Interim policy:
probability estimates are conservative/qualitative per ISO
14971:2019 §5.5 NOTE 1 until real usage data exists — treat as
worst-case-probability for any hazard entered into the register before
field data exists, rather than inventing a number to fill Section 4.2.

---

## 5. Method for evaluating overall residual risk (ISO 14971:2019 clause 4.4e)

*(Not yet defined.)* No hazard register exists yet, so there is
nothing to combine into an overall residual-risk picture. This is
distinct from per-hazard acceptability (Section 4.3 above) —
ISO 14971:2019 clause 8 requires it as a separate step, to be done
once individual hazards are entered and evaluated. Note this device
has an existing STRIDE threat model (Section 1) whose severity-like
judgments are about security impact, not clinical harm — if this
device's overall-residual-risk method ever needs to account for both,
that reconciliation is itself a real design question, not yet decided.

---

## 6. Verification activities (ISO 14971:2019 clause 4.4f)

This is where PayloadGuard-Evidence's existing engine plugs in
directly: a risk control measure's implementation and effectiveness
verification can cite a specific Gate closure and evidence-strength
label rather than a fresh verification activity description. This
device is the only one of the three worked examples with **three
independent evidence types per requirement** (CrossHair bounded
symbolic search, concrete example tests, and a Dafny formal proof),
not Dafny alone — the strengths differ per row and are stated
honestly, not flattened to a single label.

| Requirement | Risk control measure | Verification method(s) | Strength | Evidence reference |
|---|---|---|---|---|
| REQ-GIP-1-4-12 | Bolus request exceeding the dose limit triggers detection (kernel_scope only — system_scope alarm signal explicitly deferred, see Section 1) | CrossHair + concrete test `kernel_detects_bolus_limit_exceeded` + Dafny `CalculateHourlyDose` | `BOUNDED_CHECKED` / `EXAMPLE_CHECKED` / `PROVEN` (system_scope: explicit `GAP`) | `raw_crosshair_output.txt`, `raw_pytest_output_concrete.txt`, `raw_dafny_output.txt` / `run_manifest_dafny.json` |
| REQ-GIP-1-8-1 | Reverse-delivery fault (negative infusion rate) yields exactly zero delivered dose | CrossHair + concrete tests `ordinary_negative_rate_clamps_to_zero`, `overflow_negative_rate_clamps_to_zero` + Dafny `CalculateHourlyDose` | `BOUNDED_CHECKED` / `EXAMPLE_CHECKED` / `PROVEN` | same |
| REQ-DOSE-003 | Calculation yields a finite, in-range result for all precondition-meeting inputs | CrossHair + concrete test `normal_in_range_exact_value` — **no Dafny proof for this row**, stated honestly rather than implied | `BOUNDED_CHECKED` / `EXAMPLE_CHECKED` (not `PROVEN`) | `raw_crosshair_output.txt`, `raw_pytest_output_concrete.txt` |

Gate C5 (mutation testing) residual status, current as of 2026-07-07:
56 mutants against `dosage.dfy::CalculateHourlyDose`; 41 killed, 15
filtered (6 statically, 4 magnitude-implied, 4 chain-incompatible, 1
arithmetic-group-incompatible) — **zero survive, zero unclassifiable.**
This is a genuinely different, cleaner residual than the other two
worked examples (which have 44 and 51 explained survivors
respectively) — the mid-run report once had 2 real survivors, both
closed by two later, real engineering extensions (chain-direction-
aware ROR, function-body AOR, and a literal-value LVR extension that
matched its own hand-derived prediction exactly). Full detail:
`mutation_report.md`, `README.md`'s Gate C5 amendments.

Note the distinction this repo already enforces: a `PROVEN` label
above means Gate C1–C4's mechanical checks passed on the Dafny side,
not that a human has signed off on the requirement's real-world scope
— that's Gate C6, separately. Gate C6 is **closed** for this spec —
`nl_confirmation_dosage_dfy.md`'s "Decision" section: **Confirmed,
2026-07-07, by Steven** ("it's good for the spec as is") — the first
Gate C6 sign-off recorded anywhere in this repo, preceding the other
two examples' own sign-offs by several days.

---

## 7. Production and post-production information collection (ISO 14971:2019 clause 4.4g)

Not yet applicable. This is a pre-market proof-of-concept with no
manufacturing, distribution, or field-deployment pathway defined —
stated explicitly here rather than left blank with no explanation, per
this repo's own "GAP is rendered explicitly, never omitted" discipline.
When a real deployment path exists, this section needs: what
production/post-production information will be collected (e.g. real
alarm-condition frequency, whether `system_scope`'s deferred alarm
signal ever fires as intended once integration testing exists), how
it feeds back into Section 4's probability bands, and who reviews it.

---

## 8. Change log

| Date | Change | Reason |
|---|---|---|
| 2026-07-14 | Initial draft landed for `dosage_calculator`, mirroring the other two examples' plans | Third and final risk-management-plan artifact across this repo's three worked examples; the three requirement rows and their real, mixed-strength evidence (Section 6) are real and committed, everything requiring clinical judgment (Sections 2, 4.1–4.3, 5) is left as an explicit GAP pending a named Risk Manager and clinical SME |
| 2026-07-14 (later) | `HAZARD_REGISTER.md` landed alongside this plan | First real hazard-register artifact in this repo — chosen as the easiest starting point of the three examples because this device's primary source (`sources/gip-v1.0-hazard-analysis.md`) is itself a formal hazard analysis, already partially cited in this device's own STRIDE threat model. Completes clause 5.4 hazard identification for the 4 hazards this kernel actually addresses; severity, probability, and risk-acceptability evaluation remain explicit `GAP`s within it, same discipline as this plan |

**What does not yet exist, stated explicitly:** as of the register
above, hazard *identification* (clause 5.4) is real for this device.
Risk *estimation* and *evaluation* (clauses 5.5, 6, 8 — severity,
probability, acceptability) and the risk management report are still
missing — both the register and this plan name them as explicit `GAP`s
rather than fabricating them, pending the same named Risk Manager and
clinical SME Section 2 above still lacks. Section 6's table remains the
model for how a hazard entry's risk control measure should cite
evidence; `HAZARD_REGISTER.md` now does exactly that, per hazard, not
just per requirement. The existing STRIDE threat model (Section 1) is
a related but distinct artifact and does not substitute for the
clinical hazard register either — `HAZARD_REGISTER.md` cross-references
it explicitly rather than duplicating or conflating it.

---

*Template structure derived independently from ISO 14971:2019 clauses
4.4(a–g), the standard's own bracketed requirement list — not copied
from any third-party template's wording, examples, or table layout.
Device-specific content (Sections 1, 3, 6) is drawn from this
repository's own committed, real evidence
(`metadata.a.yaml`, `traceability_matrix.a.md`, `mutation_report.md`,
`nl_confirmation_dosage_dfy.md`, `README.md`) — no clinical judgment
(severity, probability, acceptability) has been fabricated to fill in
Sections 2 or 4.*
