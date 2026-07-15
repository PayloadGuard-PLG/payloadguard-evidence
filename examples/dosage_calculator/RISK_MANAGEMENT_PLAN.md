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

**Rebuilt 2026-07-15 — Finding 3/R3 resolved.** The bands below replace
the 2026-07-14 draft, which defined severity by *evidence strength*
("S1: Dafny-proven, no harm pathway is open") rather than by
consequence magnitude — a real conflation, confirmed against ISO
14971:2019 §3.27 (severity is "the measure of the possible
consequences of a hazard," independent of control status) and stated
directly by ISO/TR 24971 §5.5.4 ("severity levels... should not
include any element of probability"). Full finding:
`RISK_MANAGEMENT_FINDINGS.md` Finding 3.

**Steven's decision, 2026-07-15: Option 3 (hybrid).** Severity is
redefined by consequence alone below. A new column,
**"Evidence artifact (drives Probability, not Severity),"** is added
per hazard so the traceability strength this repo's evidence layer
actually produces — a proof, a bound, or a `GAP` — stays visible and
citable, without it silently inflating or deflating a severity label
the way the old model did. This is Option 3 exactly as assessed in the
original audit and R3's own write-up: "preserves the current model's
real strength... without asking severity to silently encode it."

Consequence bands, calibrated against generic medical-device harm
descriptors (this device's own IEC 62304 Class B classification, "non-
life-threatening injury is possible," already named the S3 boundary;
ISO/TR 24971 Table 4's five-level consequence-only descriptor set is a
further real, source-backed calibration reference) — **not yet mapped
to specific hazards below**, since that mapping is a clinical judgment
this repo's assistant cannot supply:

| Severity | Definition (consequence only — no reference to what's proven or bounded) |
|---|---|
| S1 — Negligible | If the underlying event occurred, no clinically significant harm would result — no intervention beyond routine monitoring |
| S2 — Minor | If the underlying event occurred, harm requiring minor clinical intervention (e.g. additional monitoring, a corrective dose adjustment) but not hospitalization or lasting injury |
| S3 — Serious | If the underlying event occurred, harm requiring clinical intervention to prevent lasting injury — consistent with this device's IEC 62304 Class B classification |
| S4 — Critical | If the underlying event occurred, harm that is life-threatening or causes permanent impairment or death |

Per-hazard severity, and the evidence artifact backing each hazard's
probability claim:

| Hazard | Severity | Evidence artifact (drives Probability) |
|---|---|---|
| `HAZ-GIP-1.14` (reverse delivery, kernel-proven-closed pathway) | `GAP` — **pending Steven's consequence determination**: what harm would reverse drug delivery actually cause if it reached a patient, independent of how strongly this kernel proves it doesn't. Not S1 by default just because the pathway is proven closed — that reasoning is exactly what Finding 3 found invalid | `raw_dafny_output.txt` / `run_manifest_dafny.json` — Dafny-**proven** `CalculateHourlyDose` yields exactly zero delivered dose on any negative-rate fault, both ordinary and overflow-magnitude (`ordinary_negative_rate_clamps_to_zero`, `overflow_negative_rate_clamps_to_zero`). The strongest evidence artifact in this register — now correctly read as a probability claim, not a severity one |
| `HAZ-GIP-1.2` (over-limit bolus request, kernel-proven-closed delivery pathway) | `GAP` — pending Steven's consequence determination for the narrowed, proof-closed pathway | Same Dafny/CrossHair/concrete-test evidence as `HAZ-GIP-1.14`'s kernel-scope claim (`raw_dafny_output.txt`, `traceability_matrix.a.md`) — the delivered dose is proven to stay within its safe bound |
| `HAZ-GIP-1.3` (over-limit bolus request, kernel-proven-closed delivery pathway — same evidence as `HAZ-GIP-1.2`, distinct GIP `HID 1.3` traceability anchor per `HAZARD_REGISTER.md`) | `GAP` — pending Steven's consequence determination for the narrowed, proof-closed pathway | Same Dafny/CrossHair/concrete-test evidence as `HAZ-GIP-1.2` and `HAZ-GIP-1.14`'s kernel-scope claim (`raw_dafny_output.txt`, `traceability_matrix.a.md`) — the delivered dose is proven to stay within its safe bound |
| `HAZ-GIP-1.2b` (clamp fires, clinician notification unproven) | `GAP` — pending Steven's consequence determination. Blocked on the same open question as everywhere else in this table, plus this row's own residual: even once severity is scored, whether a *probability* can be estimated for this specific hazard is Finding 5's separate open question, not resolved by Finding 3 | **None.** No Dafny, CrossHair, or concrete-test artifact addresses alarm signaling — a complete evidence gap, not a weak one (see `HAZARD_REGISTER.md`) |
| `HAZ-DOSE-003` (non-finite/out-of-range result) | `GAP` — pending Steven's consequence determination | `raw_crosshair_output.txt` + concrete test `normal_in_range_exact_value` — `BOUNDED_CHECKED`, not `PROVEN`; **structurally, permanently capped at this strength** in this toolchain (Dafny's `real` type has no IEEE-754 overflow/NaN semantics to prove against — see the "Path to sign-off" section below) |

**What this section does and does not do.** It replaces an invalid
severity model with a valid one, mechanically — every definition above
is consequence-only, sourced, and buildable without clinical input.
What it does **not** do is invent a severity value for any hazard:
doing so would require exactly the clinical judgment on real-world
consequence that this repo's assistant has never supplied for a
Gate C6 sign-off or an ALARP determination, and R3's own resolution
doesn't change that discipline. **Every hazard's severity is `GAP`
below** — not a regression from the old model's S1/S2 values, since
those values were never validly derived in the first place (they
measured evidence strength, not consequence). Section 4.3's matrix and
Section 5's overall-residual-risk method cannot produce an evaluation
until these are scored; both sections below state that cascading
effect explicitly rather than continuing to display the old,
invalidated Acceptable/Unacceptable outputs.

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
| P5 — Frequent | Expected to occur regularly, likely within normal use, **when assigned on the strength of real usage data** | **P5 is this device's default for every hazard below except `HAZ-GIP-1.2b`** (corrected 2026-07-15 — previously said "every hazard" without exception, stale since `HAZ-GIP-1.2b`'s probability was deliberately left `GAP`, not defaulted, per Finding 5), not as an occurrence-rate estimate — it is a conservative *proxy* applied per Section 4.4's policy because no field usage data exists yet (pre-market POC), not a claim that any hazard actually occurs frequently. Every P5-defaulted hazard entry marks this explicitly ("worst-case default," not "measured Frequent") to avoid the two meanings being conflated; `HAZ-GIP-1.2b`'s row states why it's excepted |

**Connection to §4.1's R3 rebuild, 2026-07-15:** each hazard's real
evidence artifact (a Dafny proof, a `BOUNDED_CHECKED` bound, or an
explicit `None`) is now named directly in §4.1's table — this is what
Finding 3/R3's Option 3 adds. It does **not**, by itself, change the
P5-default policy above: whether a strong evidence artifact (e.g.
`HAZ-GIP-1.14`'s Dafny proof) should ever justify a lower probability
band than the conservative default is a real, separate question this
section does not resolve — named here so it isn't silently begged
either direction, not answered.

### 4.3 Acceptance matrix

**DRAFT PROPOSAL, 2026-07-14 — same status as 4.1/4.2.** Extended from
a strict binary (acceptable/unacceptable) to a three-region
convention — proposed as more accurate to real practice than a pure
binary split, itself a judgment call for Steven to confirm, simplify
back to binary, or replace outright.

**Citation correction, 2026-07-15**: this was previously attributed to
"ISO 14971's own Annex D" — the 2019 edition has no Annex D (confirmed
against the standard's own Table B.1: the 2007 edition's Annex D,
"Risk concepts applied to medical devices," was moved to **ISO/TR
24971** in the 2019 revision, not retained as an annex). That document
has since been obtained (`sources/ISO-24971-2020.pdf`) and read
directly. The real basis: clause 4.2 NOTE 1 permits an ALARP-style
policy approach at all ("...can define the approaches to risk control:
reducing risk as low as reasonably practicable..."); **TR 24971 Annex
C.4, Figure C.1** gives the actual three-region matrix this plan's
structure is modelled on — confirmed verbatim: *"the risk matrix is
divided into three regions corresponding to a) unacceptable risk, b)
insignificant or negligible risk, and c) [risks] that require
investigation to determine if further risk control is feasible."*
**One real discrepancy this correction surfaces, left open, not fixed
here:** TR 24971's own region labels are "unacceptable risk /
investigate further risk control / insignificant or negligible risk"
— not "Acceptable / ALARP / Unacceptable" as the table below uses.
ALARP is a real TR 24971 concept (clause 4.2 NOTE 1 / TR §C.2), but it
names a risk-control *policy* approach, not this matrix's middle-region
label — the three-tier *structure* below is now source-backed; the
*labels* conflate two adjacent TR concepts. Whether to rename the
middle region to track TR's own wording, or keep "ALARP" as a stated,
deliberate departure from the source's terminology, is Steven's call —
see `RISK_MANAGEMENT_FINDINGS.md`'s "matrix region naming" item.

| Probability \ Severity | S1 | S2 | S3 | S4 |
|---|---|---|---|---|
| P5 — Frequent | Acceptable | **Unacceptable** | Unacceptable | Unacceptable |
| P4 — Probable | Acceptable | ALARP | Unacceptable | Unacceptable |
| P3 — Occasional | Acceptable | ALARP | ALARP | Unacceptable |
| P2 — Remote | Acceptable | Acceptable | ALARP | ALARP |
| P1 — Improbable | Acceptable | Acceptable | Acceptable | ALARP |

**Applied — as of 2026-07-15, this cannot produce an evaluation for any
hazard.** §4.1's R3 rebuild replaced the old evidence-strength severity
values with `GAP` for every hazard, pending Steven's consequence-based
scoring — the S1/S2 values this matrix used to be applied against no
longer exist. This matrix cell lookup is a real mechanism, not
abandoned, but it has nothing to evaluate yet:
**Acceptable/ALARP/Unacceptable is `GAP` for every hazard in
`HAZARD_REGISTER.md` until §4.1's severity column is scored.**

**What this replaces, stated so the change is visible, not silent:**
the prior draft of this section reported `HAZ-GIP-1.2`, `HAZ-GIP-1.3`,
and `HAZ-DOSE-003` as `Unacceptable` and `HAZ-GIP-1.14` as `Acceptable`
under the (now-invalidated) evidence-strength severity model. Those
outputs are not being revised to new values here — they are withdrawn,
because the severity inputs that produced them were never a valid
consequence measurement in the first place (Finding 3's own diagnosis:
a proof of unreachability is a probability claim, not a severity one).
This is not a finding that the device got safer or riskier; it is a
finding that the prior evaluation was never actually computed from
what ISO 14971 means by severity, and an honest matrix cannot
special-case that away. See Section 5 and the "Path to sign-off"
section below for what this changes about this device's overall
residual-risk status.

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

**Applied — updated 2026-07-15 alongside §4.1/§4.3's R3 rebuild.** This
paragraph previously said three of "four" hazards evaluated
`Unacceptable` — already stale by the time of this correction:
`HAZARD_REGISTER.md` has held five hazard rows since `HAZ-GIP-1.2b`
was split out (`RISK_MANAGEMENT_FINDINGS.md` Finding 4), not four, and
none of them currently evaluate to anything at all. §4.3's matrix
cannot produce a per-hazard evaluation until severity is scored
(above), so this method has nothing to combine. **This device's
overall residual risk is currently `GAP` — not `Unacceptable`, not
`Acceptable` — pending Steven's consequence-based severity scoring for
each of the five hazards in `HAZARD_REGISTER.md`.** Once every hazard
has a real severity value, this method applies exactly as specified
above; it is unchanged by R3, only what it currently has to work with
is.

Note this device also has an existing STRIDE threat model (Section 1)
whose severity-like judgments are about security impact, not clinical
harm — this method does not attempt to merge the two; if that
reconciliation is ever needed, it remains a real, separate design
question, not resolved here.

---

## Path to sign-off: what evidence would actually resolve the current status

**Added 2026-07-14, at Steven's request** ("let's look at the evidence
required in order to ensure a safe sign off") — not part of ISO
14971:2019's own clause-by-clause structure, so deliberately left
unnumbered rather than forced into the 4.4(a–g) sequence above.

**Retitled and substantially rewritten 2026-07-15, alongside §4.1's R3
rebuild.** This section originally targeted "the current `Unacceptable`
finding" from Section 5's old evidence-strength severity model. That
finding no longer exists — Section 5's status is now `GAP`, not
`Unacceptable` — so this section's own premise changed under it. Two
other staleness items fixed in the same pass, found while rewriting
this section, not new discoveries requiring a separate note: it said
"four hazards" (stale since `HAZ-GIP-1.2b` split out, `Finding 4`), and
it said "the three Section 5 found `Unacceptable`," which presupposed
the very evaluation R3 just withdrew.

This section still does the same real job: walking every hazard in
`HAZARD_REGISTER.md` (five, not four), stating plainly what's still
buildable versus what's structurally out of reach, so "no more Dafny
work is possible" is never mistaken for "nothing more to do." What
changed is the ordering — a step that didn't need naming under the old
model now comes first.

### Step 0 (new under R3): severity scoring blocks everything below it

Before any of the five hazards' *probability* questions matter, all
five need a real, consequence-based severity value from Steven (§4.1)
— without it, Section 4.3's matrix and Section 5's combination method
both stay `GAP` regardless of how strong or weak the probability-side
evidence below is. This is not evidence this repo's assistant can
build; it is exactly the clinical judgment §4.1 declined to invent.

### `HAZ-GIP-1.14` — probability side fully proven; severity still `GAP`

Dafny-**proven** to yield exactly zero delivered dose on any
negative-rate fault, both ordinary and overflow-magnitude — the
strongest probability-side evidence in this register, unchanged by R3.
What changed: under the old model this proof was read as directly
justifying `S1` (severity). Finding 3 found that reading invalid — a
proof of unreachability is a probability claim, not a severity one — so
this hazard is no longer "no action needed." Its severity is `GAP`
pending Steven's consequence determination, same as every other row,
even though its probability-side evidence is the best this register
has.

### `HAZ-DOSE-003` — probability side capped at `BOUNDED_CHECKED`, permanently; severity still `GAP`

`dosage.dfy`'s own header comment already states this precisely, not
something newly discovered here: *"Dafny's `real` type is exact,
arbitrary-precision mathematical real arithmetic with no overflow, no
infinity, no NaN... A Dafny 'proof' of finiteness would therefore be
true of a model that cannot even represent the phenomenon REQ-DOSE-003
is about."* Confirmed empirically in this repo (`y := x / 0.0` on
Dafny `real` is a verification *error*, not IEEE `inf` — there is no
way to even pose the question Dafny's type system would need to answer
to prove this). This is a **permanent structural limit of the
toolchain as applied to this hazard's probability-side evidence**, the
same class of boundary as `renal_adjustment`'s CKD-EPI `Pow` gap
(`RISK_MANAGEMENT_PLAN.md` of that example, `HAZ-RENAL-2`) — not a task
waiting to be picked up. `CrossHair`'s `BOUNDED_CHECKED` result is the
strongest evidence this hazard's probability side can ever have in
this toolchain. Its severity, separately, is `GAP` pending Steven —
this technical ceiling doesn't touch that question either way.

### `HAZ-GIP-1.2` / `HAZ-GIP-1.3` / `HAZ-GIP-1.2b` — the missing probability-side evidence lives outside this kernel's scope by design; severity still `GAP`

`HAZ-GIP-1.2`/`1.3`'s narrowed, proof-closed delivery pathway has the
same strong Dafny/CrossHair/concrete-test evidence as `HAZ-GIP-1.14`
(§4.1). `HAZ-GIP-1.2b`'s residual — whether a clinician is ever told a
clamp fired — has **no** evidence of any kind; the `system_scope`
alarm-*signal* gap is scoped by Section 1 to "integration testing
against a real device/UI layer, per IEC 60601-1-8's alarm-system
requirements," explicitly out of scope for a kernel-unit-verification
POC. There is no more Dafny, CrossHair, or concrete-test work *inside*
`examples/dosage_calculator/` that closes this — it requires an actual
integrated pump system (hardware, firmware, alarm hardware, UI layer)
this POC was never scoped to build. Building it would not be "more
evidence for this hazard," it would be building a different, larger
product. All three rows' severity is `GAP` pending Steven, same as
every other hazard; `HAZ-GIP-1.2b`'s probability is additionally `GAP`
by design, not defaulted to P5 — see `RISK_MANAGEMENT_FINDINGS.md`
Finding 5, a separate, still-open question about which procedure
applies to a hazard with zero evidence of any kind.

### The honest conclusion: one prerequisite, then the same two paths as before

**Prerequisite, new under R3:** Steven's real, consequence-based
severity value for each of the five hazards above (§4.1). Nothing
below can be evaluated without it — this is not optional groundwork,
it is the actual blocking step.

Once severity is scored, the same two paths named in the prior version
of this section remain the live options for whatever risk level
results — R3 changed what feeds the matrix, not what the matrix's
outputs mean once it has real inputs:

1. **Real field/usage probability data.** Section 4.4's worst-case
   default (P5 for every hazard except `HAZ-GIP-1.2b`, whose probability
   is left `GAP` per Finding 5 — §4.2) exists specifically because none
   exists yet — this is a pre-market POC with no deployment. Real data
   would let Section 4.2 assign a genuinely lower probability band
   instead of the conservative default. This path requires an actual
   deployment or a real, structured field study — neither exists, and
   neither can be simulated honestly.

2. **A real ALARP determination from Steven, as the named Clinical
   SME — a policy judgment, not more evidence.** Basis: clause 4.2
   NOTE 1, which names ALARP as one policy a manufacturer's
   risk-acceptability criteria can adopt, pointing to ISO/TR 24971 for
   guidance on defining it — TR 24971 §C.2 is where that guidance
   actually lives (this citation was itself corrected 2026-07-15; see
   §4.3). Substance: risk control has been exhausted within the stated
   scope (detection is proven, clamping is proven or bounded-checked,
   clinician oversight is a real compensating control already named in
   `metadata.a.yaml`'s `classification_rationale`), and the residual
   risk is accepted as tolerable *given that scope*, with the reasoning
   recorded explicitly — not asserted by omission. This is not
   something this repo's assistant can decide or draft on Steven's
   behalf, for the same reason no Gate C6 sign-off in this repo's
   history has ever been self-recorded: it is a real judgment call
   about what's an acceptable residual risk for a named person to
   stand behind, not a technical question with a checkable answer.

**What this section does not do:** it does not score any hazard's
severity, does not pick between the two paths above, does not draft an
ALARP justification pretending to be Steven's words, and does not
treat "no more Dafny work is possible" as license to quietly assign a
severity or relabel any hazard `Acceptable`. Section 5's `GAP` status
stands until the prerequisite above is actually done.

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
| 2026-07-15 | Finding 3/R3 resolved: severity model rebuilt consequence-only (§4.1), Option 3 (hybrid, evidence-artifact column added) | Direct instruction: "work through R3's severity model." Option 2 eliminated on textual grounds (TR 24971 §5.5.4 states severity must exclude probability, directly contradicting the old evidence-strength bands); Steven chose Option 3 over Option 1 (`AskUserQuestion`). Real, cascading consequence, stated rather than hidden: the old S1/S2 severity values were never a valid consequence measurement, so §4.3's matrix, Section 5's overall-residual-risk method, and the "Path to sign-off" section's entire argument all changed from reporting `Unacceptable`/`Acceptable` outputs to reporting `GAP` — not because the device got safer or riskier, but because the prior evaluation was never actually computed from what ISO 14971 means by severity. Every hazard's severity is now an explicit `GAP` pending Steven's real, consequence-based scoring — the concrete next blocking step, not an abstract model question anymore. Two pre-existing staleness bugs fixed in the same pass (found while rewriting, not separately reported): Section 5 and the "Path to sign-off" section both still said "four hazards," stale since `HAZ-GIP-1.2b` split out on 2026-07-15 earlier the same day (Finding 4) |

**What does not yet exist, stated explicitly — updated 2026-07-15.**
Hazard *identification* (clause 5.4) is real and complete for this
device. The severity **model** (clause 5.5) is now real and correctly
structured (consequence-only, per R3's resolution above); the
per-hazard severity **values** are not — every one is an explicit
`GAP` pending Steven's clinical scoring, which in turn blocks
evaluation (clauses 6, 8) for all five hazards. This is a more
precise statement than the prior version of this paragraph, which
described a "draft severity/probability/evaluation proposal" as if the
model and the values were the same kind of pending item — they
weren't: the old values were actively wrong (evidence-strength, not
consequence), not merely unconfirmed. The risk management report
required by clause 4.5 is still missing entirely. Section 6's table
remains the model for how a hazard entry's risk control measure should
cite evidence; `HAZARD_REGISTER.md` now does exactly that, per hazard,
not just per requirement, and §4.1's new evidence-artifact column
extends the same discipline into the severity/probability tables
themselves. The existing STRIDE threat model (Section 1) is a related
but distinct artifact and does not substitute for the clinical hazard
register either — `HAZARD_REGISTER.md` cross-references it explicitly
rather than duplicating or conflating it.

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
