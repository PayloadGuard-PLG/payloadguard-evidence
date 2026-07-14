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
| Clinical/Subject Matter Expert | **Steven** (assigned 2026-07-14) | Reviews clinical plausibility of hazards and harms; confirms or overrides the severity/probability proposal in Section 4 below |

**Partial GAP, updated 2026-07-14 — not fully closed.** The Clinical/
SME role is now filled by a named, real person (Steven), assigned by
his own explicit instruction, not inferred or assumed. Risk Manager and
Technical/Verification Lead remain unassigned — narrower than before,
not glossed over. Section 4 below now contains a **draft severity/
probability proposal**, written by this repo's assistant as a starting
point grounded in the real hazard register content, explicitly **not**
a completed SME review — matching this repo's Gate C6 discipline
exactly (substantive work is prepared, but the actual confirmation is a
recorded human decision, never self-declared on the human's behalf).
`metadata.a.yaml`'s own `classification_rationale` still applies until
that confirmation happens: the `B` safety classification is
`DECLARED`, not sourced — "GIP v1.0... does not assign IEC 62304
classes or ISO 14971 severity/probability scores per hazard...
requires a manufacturer-specific ISO 14971 risk file before this can be
upgraded from DECLARED to sourced." This document is still that file
in progress, not its completion.

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

**DRAFT PROPOSAL, 2026-07-14 — written by this repo's assistant,
grounded in `HAZARD_REGISTER.md`'s real hazard entries, awaiting
Steven's confirmation as the named Clinical SME (Section 2). Not yet
confirmed; do not treat as final.** This table is a structure the
assistant can reason about from already-committed evidence — it is
not a substitute for Steven's own clinical judgment, which may revise,
reject, or replace any definition below.

Unlike the other two worked examples, this device's harm pathway is
partially physical, not purely informational: `calculate_hourly_dose`
directly produces the number an infusion pump would deliver, clamped
by this kernel's own logic — so severity bands account for
over/under-infusion consequences directly, not just clinician
double-checking, while still respecting that alarm *signalling*
(the human-facing side) is explicitly out of this kernel's scope
(Section 1).

| Severity | Definition | Example specific to this device |
|---|---|---|
| S1 — Negligible | The kernel's contract is Dafny-**proven** (not merely `BOUNDED_CHECKED`); no harm pathway is open. `BOUNDED_CHECKED` evidence alone — a bounded symbolic search, not a proof per `traceability_matrix.a.md`'s own caveats — does not by itself justify S1; a hazard with only bounded-checked evidence caps out at S2 unless a real proof exists | HAZ-GIP-1.14 (reverse delivery): Dafny-**proven** to yield exactly zero delivered dose on any negative-rate fault — the mitigation is complete, not partial |
| S2 — Minor | The delivered dose itself stays within its proven-safe bound, but a real residual gap means a clinician isn't proven to be informed of an anomalous request, or an erroneous input is masked as an ordinary one | HAZ-GIP-1.2/1.3 (over-limit bolus requests: dose is always clamped safe, but the `system_scope` alarm *signal* proving a clinician is told is still an open `GAP`); HAZ-DOSE-003 (an overflow input is silently indistinguishable from a legitimate at-ceiling request — the dose stays bounded, but the underlying data anomaly could go unnoticed) |
| S3 — Serious, requiring intervention | A dose outside the proven-safe bound reaches a point where clinical intervention is needed to catch or correct it, consistent with this device's own IEC 62304 Class B classification ("non-life-threatening injury is possible") | Not currently applicable to any of the four real hazards in `HAZARD_REGISTER.md` as their mitigations stand today — this band exists to classify a *proof-validity failure* (the Dafny/CrossHair guarantees turning out not to hold in practice) or a future hazard this register doesn't yet cover, not a claim that one exists now |
| S4 — Critical | An unbounded or unproven failure mode allows a dose (or reverse delivery) outside any recorded control to reach delivery, contributing to a serious or life-threatening outcome | Not currently applicable — REQ-GIP-1-8-1 is specifically proven to prevent the reverse-delivery instance of this outcome. Retained as the scale's outer bound for hazards this register doesn't yet name, not to imply any known hazard reaches it |

**A real, honest finding from applying this draft scale:** given what
this kernel's evidence actually proves today, none of the four current
hazards reaches S3 or S4 — three land at S2 (a residual awareness/
masking gap, not a dose-safety gap) and one (HAZ-GIP-1.14) lands at S1
(fully proven zero-harm). S3/S4 are retained to classify hypothetical
proof failures or hazards not yet in scope, not smoothed away because
nothing currently occupies them.

### 4.2 Probability bands

**DRAFT PROPOSAL, 2026-07-14 — same status as 4.1: assistant-authored,
pending Steven's confirmation.** Uses a standard five-level qualitative
scale common to ISO 14971 implementations (frequency-of-occurrence
categories, not a specific mandated scale from the standard itself) —
adopted here as a reasonable starting structure, not asserted as the
only valid choice.

| Probability | Definition | Basis for estimate |
|---|---|---|
| P1 — Improbable | So unlikely it can be assumed not to occur, though not physically impossible | No field data exists to support this band for any current hazard — not assigned to any hazard below without real evidence |
| P2 — Remote | Unlikely, but plausible over the device's field life | Same — not assigned without evidence |
| P3 — Occasional | Expected to occur sometimes over the device's field life | Same — not assigned without evidence |
| P4 — Probable | Expected to occur several times over the device's field life | Same — not assigned without evidence |
| P5 — Frequent | Expected to occur regularly, likely within normal use, **when assigned on the strength of real usage data** | **P5 is this device's current default for every hazard below, but not as an occurrence-rate estimate** — it is a conservative *proxy* applied per Section 4.4's policy because no field usage data exists yet (pre-market POC), not a claim that any hazard actually occurs frequently. Every hazard entry marks this explicitly ("worst-case default," not "measured Frequent") to avoid the two meanings being conflated |

### 4.3 Acceptance matrix

**DRAFT PROPOSAL, 2026-07-14 — same status as 4.1/4.2.** Extended from
a strict binary (acceptable/unacceptable) to the three-region
convention ISO 14971's own Annex D discusses (broadly acceptable /
ALARP — As Low As Reasonably Practicable, tolerable only with
justification and further risk-reduction effort / unacceptable) —
proposed as more accurate to real practice than a pure binary split,
itself a judgment call for Steven to confirm, simplify back to binary,
or replace outright.

| Probability \ Severity | S1 | S2 | S3 | S4 |
|---|---|---|---|---|
| P5 — Frequent | Acceptable | **Unacceptable** | Unacceptable | Unacceptable |
| P4 — Probable | Acceptable | ALARP | Unacceptable | Unacceptable |
| P3 — Occasional | Acceptable | ALARP | ALARP | Unacceptable |
| P2 — Remote | Acceptable | Acceptable | ALARP | ALARP |
| P1 — Improbable | Acceptable | Acceptable | Acceptable | ALARP |

**Applied to the current default (every hazard at P5, per 4.2):**
under this draft matrix, HAZ-GIP-1.2, HAZ-GIP-1.3, and HAZ-DOSE-003
(all S2) currently evaluate as **Unacceptable** — not because their
actual delivered-dose behavior is unsafe (it isn't; all three are
proven or bounded-checked to stay within their safe range), but because
the mandated conservative probability default, combined with even a
"minor" severity, doesn't clear this draft bar. HAZ-GIP-1.14 (S1)
evaluates as **Acceptable** at any probability. This is a real,
substantive output, not a formality: it correctly identifies that
either (a) the `system_scope` alarm-signal proof gets built, (b) real
field data eventually justifies a lower probability band, or (c)
Steven's own clinical judgment revises the severity/matrix itself,
before this device's risk profile could be considered acceptable as
currently evidenced.

### 4.4 Criteria for accepting risk when probability cannot be estimated

This is a pre-market POC with no field usage data. Interim policy:
probability estimates are conservative/qualitative per ISO
14971:2019 §5.5 NOTE 1 until real usage data exists — treat as
worst-case-probability for any hazard entered into the register before
field data exists, rather than inventing a number to fill Section 4.2.
**This policy is now actually applied, not just stated**: Section 4.2's
P5 default and Section 4.3's resulting evaluations above are the first
real instance of this policy being exercised, not merely described in
the abstract.

---

## 5. Method for evaluating overall residual risk (ISO 14971:2019 clause 4.4e)

**DRAFT PROPOSAL, 2026-07-14 — same status as Section 4: assistant-
authored, pending Steven's confirmation as Clinical SME.** A hazard
register now exists (`HAZARD_REGISTER.md`), so there is something real
to combine. Proposed method, deliberately simple and conservative
rather than a weighted/statistical combination this device's evidence
doesn't support: **overall residual risk is Acceptable only if every
individual hazard in Section 4.3's evaluation is Acceptable; if any
hazard evaluates ALARP, overall residual risk is Tolerable only with
an explicit justification recorded per hazard; if any hazard evaluates
Unacceptable, overall residual risk is Unacceptable until that hazard
is resolved.** Explicit mapping, since the label changes at the
device level: `Tolerable` (Section 5, overall) is the device-level
consequence of one or more individual hazards evaluating `ALARP`
(Section 4.3, per-hazard) with their justification recorded — the two
terms are not synonyms used loosely, `ALARP` is the per-hazard
finding, `Tolerable` is what that finding means for the device as a
whole. This is distinct from per-hazard acceptability (Section 4.3) —
clause 8 requires it as a genuinely separate step, not a restatement.

**Applied for real:** three of `dosage_calculator`'s four hazards
(`HAZ-GIP-1.2`, `HAZ-GIP-1.3`, `HAZ-DOSE-003`) currently evaluate
Unacceptable under Section 4.3's draft matrix. Under this method,
**this device's overall residual risk is currently `Unacceptable`,
pending either the `system_scope` alarm-signal proof, real field
probability data, or Steven's revision of the severity/probability
bands themselves** — not a comfortable conclusion to default to, but
an honest one given what's actually proven versus what's still `GAP`.

Note this device also has an existing STRIDE threat model (Section 1)
whose severity-like judgments are about security impact, not clinical
harm — this method does not attempt to merge the two; if that
reconciliation is ever needed, it remains a real, separate design
question, not resolved here.

---

## Path to sign-off: what evidence would actually resolve the current `Unacceptable` finding

**Added 2026-07-14, at Steven's request** ("let's look at the evidence
required in order to ensure a safe sign off") — not part of ISO
14971:2019's own clause-by-clause structure, so deliberately left
unnumbered rather than forced into the 4.4(a–g) sequence above. This
section walks all four hazards in `HAZARD_REGISTER.md`, stating
plainly which need no further action and which do — its real focus is
the three Section 5 found `Unacceptable` (`HAZ-GIP-1.2`, `HAZ-GIP-1.3`,
`HAZ-DOSE-003`), for which it answers one question directly: what
would actually change that finding, distinguishing evidence this repo
could still build from evidence it fundamentally cannot, so nobody
mistakes "no more Dafny work available" for "nothing more to do."

### `HAZ-GIP-1.14` — no action needed

Already `Acceptable` (S1) under the draft matrix. Fully Dafny-proven;
nothing in this analysis changes that.

### `HAZ-DOSE-003` — cannot be strengthened to `PROVEN`, ever, in this model

`dosage.dfy`'s own header comment already states this precisely, not
something newly discovered here: *"Dafny's `real` type is exact,
arbitrary-precision mathematical real arithmetic with no overflow, no
infinity, no NaN... A Dafny 'proof' of finiteness would therefore be
true of a model that cannot even represent the phenomenon REQ-DOSE-003
is about."* Confirmed empirically in this repo (`y := x / 0.0` on
Dafny `real` is a verification *error*, not IEEE `inf` — there is no
way to even pose the question Dafny's type system would need to answer
to prove this). This is a **permanent structural limit of the
toolchain as applied to this postcondition**, the same class of
boundary as `renal_adjustment`'s CKD-EPI `Pow` gap (`RISK_MANAGEMENT_PLAN.md`
of that example, `HAZ-RENAL-2`) — not a task waiting to be picked up.
`CrossHair`'s `BOUNDED_CHECKED` result is not a weaker version of the
same evidence a Dafny proof would give; it is a structurally different
kind of evidence, and it is the strongest kind this postcondition can
ever have in this repo's toolchain.

### `HAZ-GIP-1.2` / `HAZ-GIP-1.3` — the missing evidence lives outside this kernel's scope by design

The residual is the `system_scope` alarm-*signal* gap — Section 1
already scopes that as belonging to "integration testing against a
real device/UI layer, per IEC 60601-1-8's alarm-system requirements,"
explicitly out of scope for a kernel-unit-verification POC. There is
no more Dafny, CrossHair, or concrete-test work *inside*
`examples/dosage_calculator/` that closes this — it requires an actual
integrated pump system (hardware, firmware, alarm hardware, UI layer)
this POC was never scoped to build. Building it would not be "more
evidence for this hazard," it would be building a different, larger
product.

### The honest conclusion: two real paths remain, neither of them more spec work

1. **Real field/usage probability data.** Section 4.4's worst-case
   default (P5 for every hazard) exists specifically because none
   exists yet — this is a pre-market POC with no deployment. Real data
   would let Section 4.2 assign a genuinely lower probability band
   instead of the conservative default, which could move `HAZ-GIP-1.2`/
   `1.3`/`HAZ-DOSE-003` (all S2) out of `Unacceptable` under the current
   matrix without anyone's severity judgment changing at all. This
   path requires an actual deployment or a real, structured field
   study — neither exists, and neither can be simulated honestly.

2. **A real ALARP determination from Steven, as the named Clinical
   SME — a policy judgment, not more evidence.** ISO 14971's own Annex
   D allows exactly this move: risk control has been exhausted within
   the stated scope (detection is proven, clamping is proven or
   bounded-checked, clinician oversight is a real compensating control
   already named in `metadata.a.yaml`'s `classification_rationale`),
   and the residual risk is accepted as tolerable *given that scope*,
   with the reasoning recorded explicitly — not asserted by omission.
   This is not something this repo's assistant can decide or draft on
   Steven's behalf, for the same reason no Gate C6 sign-off in this
   repo's history has ever been self-recorded: it is a real judgment
   call about what's an acceptable residual risk for a named person to
   stand behind, not a technical question with a checkable answer.

**What this section does not do:** it does not pick between these two
paths, does not draft an ALARP justification pretending to be Steven's
words, and does not treat "no more Dafny work is possible" as license
to quietly relabel these hazards `Acceptable`. The `Unacceptable`
finding in Section 5 stands until one of the two paths above actually
happens.

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
| 2026-07-14 (later still) | Steven assigned as Clinical/SME (Section 2); draft severity/probability proposal built (Sections 4, 5) and applied to `HAZARD_REGISTER.md`'s 4 hazards | Direct instruction: "assign a clinical SME and start the severity/probability tables." A real, named person now fills the Clinical/SME role — a fictitious name or invented clinical data was explicitly declined, matching this repo's Gate C6 discipline. The severity/probability/acceptance-matrix content is a substantive, evidence-grounded **draft proposal**, not a completed SME sign-off — every section says so explicitly. Real finding from applying it: none of the 4 hazards currently reaches S3/S4 given what's actually proven, but 3 of 4 evaluate provisionally Unacceptable under the mandated worst-case probability default, making this device's current overall residual risk `Unacceptable` pending further evidence or Steven's confirmation/revision |
| 2026-07-14 (yet later) | New unnumbered "Path to sign-off" section added between Sections 5 and 6 | Direct instruction: "let's look at the evidence required in order to ensure a safe sign off." Real finding, not previously stated this plainly: two of the three `Unacceptable` hazards (`HAZ-DOSE-003`'s finiteness postcondition, and the `system_scope` alarm-signal gap behind `HAZ-GIP-1.2`/`1.3`) have **no further evidence buildable inside this repo at all** — `dosage.dfy`'s own comment already documents that Dafny's `real` type cannot even represent the IEEE-754 overflow phenomenon REQ-DOSE-003 is about, and `system_scope` requires an integrated pump system outside this POC's stated scope. The only two real paths off `Unacceptable` are real field/usage data (which doesn't exist for a pre-market POC) or a genuine ALARP determination that only Steven, as the named SME, can make — not more spec work this repo's assistant can produce |

**What does not yet exist, stated explicitly:** hazard *identification*
(clause 5.4) is real and complete for this device. A **draft**
severity/probability/evaluation proposal (clauses 5.5, 6, 8) now
exists in this plan and in `HAZARD_REGISTER.md`, but it is exactly
that — a draft, authored by this repo's assistant from already-
committed evidence, not yet reviewed and confirmed by Steven in his
capacity as the named Clinical SME. The risk management report
required by clause 4.5 is still missing entirely. Section 6's table
remains the model for how a hazard entry's risk control measure should
cite evidence; `HAZARD_REGISTER.md` now does exactly that, per hazard,
not just per requirement. The existing STRIDE threat model (Section 1)
is a related but distinct artifact and does not substitute for the
clinical hazard register either — `HAZARD_REGISTER.md` cross-references
it explicitly rather than duplicating or conflating it.

---

*Template structure derived independently from ISO 14971:2019 clauses
4.4(a–g), the standard's own bracketed requirement list — not copied
from any third-party template's wording, examples, or table layout.
Device-specific content (Sections 1, 3, 6) is drawn from this
repository's own committed, real evidence
(`metadata.a.yaml`, `traceability_matrix.a.md`, `mutation_report.md`,
`nl_confirmation_dosage_dfy.md`, `README.md`). Sections 4 and 5's
severity/probability/acceptance-matrix content, added 2026-07-14, is a
**draft proposal reasoned from that same real evidence**, authored by
this repo's assistant at Steven's explicit request — not fabricated
clinical data, and not presented as a completed SME determination
either. It carries no authority until Steven, as the named Clinical
SME (Section 2), reviews and confirms it — exactly the distinction
this repo has held to for every Gate C6 sign-off.*
