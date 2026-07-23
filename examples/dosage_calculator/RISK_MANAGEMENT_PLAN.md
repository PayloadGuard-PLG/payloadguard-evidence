# Risk Management Plan — Generic Infusion Pump: Dose-Limit Safety Kernel (POC)

**Document ID:** RMP-GIP-001
**Risk Management File reference:** This plan is part of the risk
management file per ISO 14971:2019 clause 4.4. It does not itself
contain the hazard register, evaluation results, or risk management
report — those are separate documents this plan governs and
references, per clause 4.5's own traceability requirements for the
risk management file as a whole (neither of those documents exists yet
for this device — see Section 8).

**Status:** DRAFT | Version: 0.2 | Last reviewed: 2026-07-15

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
| Determination preparer / risk-evidence owner | **PayloadGuard Research** (role recorded 2026-07-14; corrected 2026-07-22, see below) | Assembles the evidence and structures the hazard analysis, severity inputs, and determinations so a qualified SME's judgment is easy and well-grounded. **Not a credentialed clinical SME**; does not make and cannot self-record the SME determination |
| Clinical/Subject Matter Expert | *(not yet assigned — pending qualified clinical/regulatory review)* | Reviews clinical plausibility of hazards and harms; makes the severity/acceptability determinations. Informal guidance from practising clinical contacts *informs* the preparer's work but does not fill this role |

**Role correction, 2026-07-22 — superseded in place, not silently
edited.** The row above previously named an individual as the
"Clinical/Subject Matter Expert." That was an overclaim, corrected: the
role was never to *make* an SME's judgment but to *make it easier for
one* — assemble evidence, structure the reasoning, surface where the
ground is weak. The Clinical SME role is therefore
**unfilled** (alongside Risk Manager and Technical/Verification Lead),
not filled by a non-SME; a qualified SME's sign-off is a genuinely open
prerequisite, recorded as such rather than papered over with a title.
This is the same drafter≠checker boundary the rest of this repo holds
(no Gate C6 spec sign-off is self-recorded); `ALARP_DETERMINATION.md`'s
two-role sign-off (Prepared by / SME determination `_PENDING_`) applies
it to risk acceptance. Downstream consequence, stated not hidden: every
2026-07-15 record that reads "Steven, the named Clinical SME, scored…"
(the S3×5 and S4 severity values) is, under this correction, a
**prepared** severity assessment awaiting SME confirmation, not a
completed SME determination — the values and reasoning stand as
preparation; the ratification does not yet exist.

**Prior framing, updated 2026-07-14 (now itself superseded by the
2026-07-22 correction above).** Risk Manager and
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
further real, source-backed calibration reference) — **mapped to
specific hazards below as of 2026-07-15 (later)**, Steven's real
consequence determination for each, not this repo's assistant's own
inference (that mapping was, and remains, a clinical judgment only
Steven can supply):

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
| `HAZ-GIP-1.14` (reverse delivery, kernel-proven-closed pathway) | **`S3` — Serious.** Steven's determination, 2026-07-15 (`AskUserQuestion`): what harm reverse drug delivery would actually cause if it reached a patient, independent of how strongly this kernel proves it doesn't. Not S1 by default just because the pathway is proven closed — that reasoning is exactly what Finding 3 found invalid | `raw_dafny_output.txt` / `run_manifest_dafny.json` — Dafny-**proven** `CalculateHourlyDose` yields exactly zero delivered dose on any negative-rate fault, both ordinary and overflow-magnitude (`ordinary_negative_rate_clamps_to_zero`, `overflow_negative_rate_clamps_to_zero`). The strongest evidence artifact in this register — correctly read as a probability claim, not a severity one. **R5, resolved 2026-07-15**: this proof's probability credit now extends to `dosage.py`'s real, independently-executed behavior too, not just the spec — `differential_test_results.json`, 9/9 vectors matched (`RISK_MANAGEMENT_FINDINGS.md`) |
| `HAZ-GIP-1.2` (over-limit bolus request, kernel-proven-closed delivery pathway) | **`S3` — Serious.** Steven's determination, 2026-07-15 (`AskUserQuestion`), for the narrowed, proof-closed pathway | Same Dafny/CrossHair/concrete-test evidence as `HAZ-GIP-1.14`'s kernel-scope claim (`raw_dafny_output.txt`, `traceability_matrix.a.md`) — the delivered dose is proven to stay within its safe bound. Same R5 differential-testing confirmation as `HAZ-GIP-1.14` above applies here |
| `HAZ-GIP-1.3` (over-limit bolus request, kernel-proven-closed delivery pathway — same evidence as `HAZ-GIP-1.2`, distinct GIP `HID 1.3` traceability anchor per `HAZARD_REGISTER.md`) | **`S3` — Serious.** Steven's determination, 2026-07-15 (`AskUserQuestion`), scored independently of `HAZ-GIP-1.2` despite the identical underlying mechanism, and landed at the same value | Same Dafny/CrossHair/concrete-test evidence as `HAZ-GIP-1.2` and `HAZ-GIP-1.14`'s kernel-scope claim (`raw_dafny_output.txt`, `traceability_matrix.a.md`) — the delivered dose is proven to stay within its safe bound. Same R5 differential-testing confirmation applies |
| `HAZ-GIP-1.2b` (clamp fires, clinician notification unproven) | **`S3` — Serious.** Steven's determination, 2026-07-15 (`AskUserQuestion`). Severity is no longer this row's blocker — even with it known, whether a *probability* can be estimated for this specific hazard is Finding 5's separate open question, not resolved by this scoring | **None.** No Dafny, CrossHair, or concrete-test artifact addresses alarm signaling — a complete evidence gap, not a weak one (see `HAZARD_REGISTER.md`) |
| `HAZ-DOSE-003` (non-finite/out-of-range result) | **`S3` — Serious.** Steven's determination, 2026-07-15 (`AskUserQuestion`) | `raw_crosshair_output.txt` + concrete test `normal_in_range_exact_value` — `BOUNDED_CHECKED`, not `PROVEN`; **structurally, permanently capped at this strength** in this toolchain (Dafny's `real` type has no IEEE-754 overflow/NaN semantics to prove against — see the "Path to sign-off" section below) |
| `HAZ-GIP-1.14b` (reverse-delivery clamp fires, clinician notification unproven) | **`S4` — Critical.** Steven's determination, 2026-07-21 (`AskUserQuestion`): if a reverse-flow fault clamps to zero but the clinician is never alerted, the underlying fault condition (line issue, connector failure, hardware defect) can recur or go unaddressed — the first hazard in this register to diverge from `S3` | **None.** No Dafny, CrossHair, or concrete-test artifact addresses clinician notification of a reverse-flow fault — a complete evidence gap, same class as `HAZ-GIP-1.2b` |

**What this section does and does not do.** It replaced an invalid
severity model with a valid one, mechanically — every definition above
is consequence-only, sourced, and buildable without clinical input —
and then (2026-07-15, later) Steven — PayloadGuard Research, the
determination preparer, **not a credentialed clinical SME** (Section 2,
role corrected 2026-07-22) — recorded a severity assessment for every
hazard: **`S3 — Serious`, all five**, a *prepared* assessment awaiting
qualified-SME ratification, not a completed SME determination. This
repo's assistant did not invent, propose, or infer any of these five
values;
each was recorded via `AskUserQuestion` against the real consequence
bands above and each hazard's own documented harm text, matching the
same discipline every Gate C6 sign-off in this repo has held to.
Section 4.3's matrix and Section 5's overall-residual-risk method can
now produce a real evaluation for the first time — see both below for
what that evaluation actually is, stated plainly rather than left
implicit.

**Superseded 2026-07-21, not corrected in place:** the "all five"
result above described this register's state before `HAZ-GIP-1.14b`
existed. That row's severity, scored the same way, is **`S4 —
Critical`** — this section's real current state is five hazards at
`S3`, one at `S4`, not six at `S3`.

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
| P5 — Frequent | Expected to occur regularly, likely within normal use, **when assigned on the strength of real usage data** | **P5 is this device's default for every hazard below except `HAZ-GIP-1.2b` and `HAZ-GIP-1.14b`** (corrected 2026-07-15 for `HAZ-GIP-1.2b`, previously said "every hazard" without exception, stale since its probability was deliberately left `GAP`, not defaulted, per Finding 5; corrected again 2026-07-21 to add `HAZ-GIP-1.14b`, same Finding 5 basis), not as an occurrence-rate estimate — it is a conservative *proxy* applied per Section 4.4's policy because no field usage data exists yet (pre-market POC), not a claim that any hazard actually occurs frequently. Every P5-defaulted hazard entry marks this explicitly ("worst-case default," not "measured Frequent") to avoid the two meanings being conflated; both excepted rows state why they're excepted |

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

**Applied — updated 2026-07-15 (later), now that §4.1 has real
severity values.** Mechanical lookup, per hazard, against the matrix
above:

| Hazard | Severity | Probability | Evaluation |
|---|---|---|---|
| `HAZ-GIP-1.14` | S3 | P5 | **Unacceptable** |
| `HAZ-GIP-1.2` | S3 | P5 | **Unacceptable** |
| `HAZ-GIP-1.3` | S3 | P5 | **Unacceptable** |
| `HAZ-DOSE-003` | S3 | P5 | **Unacceptable** |
| `HAZ-GIP-1.2b` | S3 | `GAP` (Finding 5) | **`GAP`** — blocked only because its Probability, not its Severity, is unscored |
| `HAZ-GIP-1.14b` | S4 | `GAP` (Finding 5) | **`GAP`** — blocked by Probability, same as `HAZ-GIP-1.2b`; would remain at best `ALARP` even if resolved, never `Acceptable`, since S4 has no `Acceptable` cell in the matrix above at any probability band |

**Superseded 2026-07-22 — the two `GAP` rows above are no longer
matrix-evaluated.** Finding 5 is resolved (Option C, two-track;
`RISK_MANAGEMENT_FINDINGS.md`): the two zero-evidence hazards
(`HAZ-GIP-1.2b`, `HAZ-GIP-1.14b`) leave this matrix and are evaluated on
**severity alone** (TR 24971 §5.5.3). Their `Risk evaluation` is no
longer a matrix-`GAP` waiting on a probability band — it is determined
by a per-hazard severity-alone acceptability determination
(`HAZ-GIP-1.14b`: `ALARP_DETERMINATION.md`, Sections 1–4, in progress;
`HAZ-GIP-1.2b`: pending). The four matrix-evaluated `Unacceptable` rows
are unchanged. Rows left in place, superseded-not-corrected. The
`HAZ-GIP-1.14b` note above still holds under the severity-alone track:
`S4` alone can, at best, be argued `ALARP` at this stage — never
`Acceptable`.

**Four of six hazards evaluate `Unacceptable`.** This is a real,
mechanical output of Steven's own S3 scoring combined with §4.2's
standing worst-case P5 default — not a new judgment call, and not this
repo's assistant characterizing the device as unsafe on its own
authority. It is exactly what this matrix, built and confirmed before
any severity value existed, was always going to say once given a real
S3 input at P5. See Section 5 and the "Path to sign-off" section below
for what this means at the device level and what the two remaining
live paths off `Unacceptable` are.

**What this replaces, stated so the change is visible, not silent:**
the 2026-07-14 draft of this section reported the same four rows
(under different names — `HAZ-GIP-1.2`/`1.3` had not yet been split
from `HAZ-GIP-1.2b`) as `Unacceptable` and `HAZ-GIP-1.14` as
`Acceptable`, under the since-invalidated evidence-strength severity
model. Those old outputs were withdrawn, not revised, on 2026-07-15
(Finding 3/R3) because the severity inputs that produced them were
never a valid consequence measurement (a proof of unreachability is a
probability claim, not a severity one) — `HAZ-GIP-1.14`'s old
`Acceptable` in particular was reasoning from proof strength, exactly
the conflation Finding 3 found invalid. The `Unacceptable` result
recorded above is a new, independent computation from Steven's real
consequence-based severity values, not a reinstatement of the old
draft numbers — it is a coincidence of the matrix's structure, not a
sign the old reasoning was secretly right, that four of five rows land
on the same label either way.

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
authored, pending qualified-SME confirmation** (prepared for review by
Steven / PayloadGuard Research, who is not himself a credentialed SME —
Section 2, corrected 2026-07-22). A hazard
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

**Applied — updated 2026-07-15 (later), now that §4.3 has real
per-hazard evaluations.** Four of the five hazards in
`HAZARD_REGISTER.md` evaluate `Unacceptable` (§4.3). Per this method
(stated above, unchanged since 2026-07-14): if any hazard evaluates
Unacceptable, overall residual risk is Unacceptable until that hazard
is resolved. **This device's overall residual risk is
`Unacceptable`.** Not `GAP` — every hazard now has a real, Steven-
scored severity value, so this method has a real result to report, not
an unscored input to wait on. Not `Acceptable`, and not merely
`Tolerable`: `Tolerable` under this method requires every unresolved

**Superseded 2026-07-21, not corrected in place: `HAZ-GIP-1.14b` now
exists.** The register has six hazards, not five. The device-level
result above is unchanged — it was already `Unacceptable` on four of
the original five, and adding one more `GAP`-evaluation hazard
(`HAZ-GIP-1.14b`, alongside `HAZ-GIP-1.2b`) doesn't change a status
that's already `Unacceptable` for a different reason. What changes:
two hazards, not one, are now blocked on Finding 5's open Probability
question, and `HAZ-GIP-1.14b` specifically cannot resolve to
`Acceptable` even if Finding 5 lands favorably — see §4.3's added row.

`Tolerable` under this method requires every unresolved
hazard to evaluate no worse than `ALARP` with a recorded justification,
which is not this device's actual state — four hazards evaluate
`Unacceptable` outright, a stronger finding than `ALARP`. See the
"Path to sign-off" section immediately below for the two remaining
live paths off this result.

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
finding no longer existed at the time of this rewrite — Section 5's
status was `GAP`, not `Unacceptable` — so this section's own premise
changed under it. Two other staleness items fixed in the same pass,
found while rewriting this section, not new discoveries requiring a
separate note: it said "four hazards" (stale since `HAZ-GIP-1.2b` split
out, `Finding 4`), and it said "the three Section 5 found
`Unacceptable`," which presupposed the very evaluation R3 had just
withdrawn.

**Update, 2026-07-15 (later): superseded by real events, not a second
rewrite.** Section 5's `GAP` status, described immediately above as the
reason this section changed, was itself temporary — Steven's real
severity scoring (Step 0 below) has since produced a new, independently
computed `Unacceptable` finding (Section 5). The paragraph above is
preserved as an accurate record of the 2026-07-15 (earlier) state, not
corrected in place, per this repo's own discipline for superseded
claims; Step 0 and everything below it now describe this device's
actual current status, not a hypothetical one.

This section still does the same real job: walking every hazard in
`HAZARD_REGISTER.md` (five, not four), stating plainly what's still
buildable versus what's structurally out of reach, so "no more Dafny
work is possible" is never mistaken for "nothing more to do." What
changed is the ordering — a step that didn't need naming under the old
model now comes first.

**Superseded 2026-07-21, not corrected in place:** six, not five —
`HAZ-GIP-1.14b` split out of `HAZ-GIP-1.14` below (same pattern as
`HAZ-GIP-1.2b`'s split from `HAZ-GIP-1.2`/`1.3`). A new subsection for
it follows the existing three below, in the same walkthrough style.

### Step 0 (R3): severity scoring — done, 2026-07-15

Before any of the five hazards' *probability* questions could matter,
all five needed a real, consequence-based severity value from Steven
(§4.1) — without it, Section 4.3's matrix and Section 5's combination
method both stayed `GAP` regardless of how strong or weak the
probability-side evidence below was. **This step is now done**: Steven
scored all five `S3 — Serious` via `AskUserQuestion`, 2026-07-15. What
follows below is no longer a forward-looking description of what
*would* block sign-off once severity existed — it is this device's
actual current state.

**Step 0b, 2026-07-21: a sixth hazard, `HAZ-GIP-1.14b`, added and
scored the same way.** Split from `HAZ-GIP-1.14` (the reverse-delivery
clamp's own clinician-notification gap, structurally parallel to
`HAZ-GIP-1.2b`), triggered by a Gap-if question in `CalculateHourlyDose`'s
contract ratification that could not honestly be answered "eliminated."
Scored via the same process, `AskUserQuestion`, consequence-only per
§4.1 — but landed at **`S4 — Critical`**, not `S3`, the first hazard in
this register to diverge. Confirmed with Steven directly, not assumed:
the determination is genuinely consequence-only ("if and when this
problem was to occur, it would be a critical problem" — not a claim
that it will occur), the same separation Finding 3 required of every
other row.

### `HAZ-GIP-1.14` — probability side fully proven; severity `S3`, Steven's determination

Dafny-**proven** to yield exactly zero delivered dose on any
negative-rate fault, both ordinary and overflow-magnitude — the
strongest probability-side evidence in this register, unchanged by R3.
What changed: under the old model this proof was read as directly
justifying `S1` (severity). Finding 3 found that reading invalid — a
proof of unreachability is a probability claim, not a severity one —
and Steven's real scoring confirmed the point concretely: this hazard
is `S3`, not `S1`, despite carrying this register's strongest
probability-side evidence. Combined with §4.2's standing P5 default,
this hazard evaluates `Unacceptable` (§4.3) — the strength of the
proof affects how conservative the P5 default arguably ought to be
(§4.2's own still-open question), not whether this hazard needs
attention at all.

### `HAZ-DOSE-003` — probability side capped at `BOUNDED_CHECKED`, permanently; severity `S3`, Steven's determination

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
this toolchain. Its severity, separately, is `S3` — Steven's
determination, same as every other row — this technical ceiling
doesn't touch that question either way; combined with §4.2's P5
default this hazard evaluates `Unacceptable` (§4.3).

### `HAZ-GIP-1.2` / `HAZ-GIP-1.3` / `HAZ-GIP-1.2b` — the missing probability-side evidence lives outside this kernel's scope by design; severity `S3` for all three, Steven's determination

`HAZ-GIP-1.2`/`1.3`'s narrowed, proof-closed delivery pathway has the
same strong Dafny/CrossHair/concrete-test evidence as `HAZ-GIP-1.14`
(§4.1); both now evaluate `Unacceptable` (§4.3), same mechanism.
`HAZ-GIP-1.2b`'s residual — whether a clinician is ever told a
clamp fired — has **no** evidence of any kind; the `system_scope`
alarm-*signal* gap is scoped by Section 1 to "integration testing
against a real device/UI layer, per IEC 60601-1-8's alarm-system
requirements," explicitly out of scope for a kernel-unit-verification
POC. There is no more Dafny, CrossHair, or concrete-test work *inside*
`examples/dosage_calculator/` that closes this — it requires an actual
integrated pump system (hardware, firmware, alarm hardware, UI layer)
this POC was never scoped to build. Building it would not be "more
evidence for this hazard," it would be building a different, larger
product. All three rows' severity is `S3`, same as every other hazard;
`HAZ-GIP-1.2b`'s probability is additionally `GAP`
by design, not defaulted to P5 — see `RISK_MANAGEMENT_FINDINGS.md`
Finding 5, a separate, still-open question about which procedure
applies to a hazard with zero evidence of any kind, so `HAZ-GIP-1.2b`
alone still evaluates `GAP` (§4.3), not `Unacceptable` like the other
four.

### `HAZ-GIP-1.14b` — added 2026-07-21; same evidence gap as `HAZ-GIP-1.2b`, different severity

Split from `HAZ-GIP-1.14` for the same reason `HAZ-GIP-1.2b` split
from `HAZ-GIP-1.2`/`1.3`: the kernel proves the mechanical fault
response (reverse-flow input yields exactly zero delivered dose,
`PROVEN`), not that a clinician is ever told it happened. No Dafny,
CrossHair, or concrete-test artifact in this repo addresses clinician
notification of a reverse-flow fault — the same complete evidence gap
as `HAZ-GIP-1.2b`, not a weaker version of it. `metadata.a.yaml`
confirms this structurally: `REQ-GIP-1-4-12` carries both `kernel_scope`
and `system_scope` fields, but `REQ-GIP-1-8-1` carries only a flat
`text` field — no system-scope split exists to even name the gap at
the requirement level, let alone close it.

Where this row genuinely differs from `HAZ-GIP-1.2b`: severity.
Steven's determination is `S4 — Critical`, not `S3` — an unaddressed
reverse-flow fault (line issue, connector failure, hardware defect)
that recurs or escalates unnoticed has no severity ceiling this
register can currently rule out as clinically less than critical,
independent of whether it's likely. This is not a stronger evidence
gap than `HAZ-GIP-1.2b`'s — the *evidence* side is identical (`GAP`,
Finding 5, same open question) — it is a stronger *consequence*
judgment, prepared by Steven (PayloadGuard Research, determination
preparer — not a credentialed SME), awaiting qualified-SME ratification
like every other severity value in this register.

### The honest conclusion: the prerequisite is done — two paths remain, and one of them is now the live blocking question

**Prerequisite, from R3, now satisfied:** Steven's real,
consequence-based severity value for each of the six hazards above
(§4.1) — `S3 — Serious` for five, `S4 — Critical` for `HAZ-GIP-1.14b`
(2026-07-21). This device's overall residual risk is now a real,
computed `Unacceptable` (Section 5), not a placeholder waiting on
clinical input.

The same two paths named in the prior version of this section remain
the live options for resolving that result — R3 changed what feeds the
matrix, not what the matrix's outputs mean once it has real inputs,
and satisfying the prerequisite above didn't remove the need for one of
them, it made choosing between them the actual next decision:

1. **Real field/usage probability data.** Section 4.4's worst-case
   default (P5 for every hazard except `HAZ-GIP-1.2b` and
   `HAZ-GIP-1.14b`, whose probabilities are left `GAP` per Finding 5 —
   §4.2) exists specifically because none exists yet — this is a
   pre-market POC with no deployment. Note `HAZ-GIP-1.14b` specifically:
   even real field data resolving this to a Probability band cannot
   move it past `ALARP` (§4.3), since S4 has no `Acceptable` cell at
   any band. Real data would let Section 4.2 assign a genuinely lower probability band
   instead of the conservative default. This path requires an actual
   deployment or a real, structured field study — neither exists, and
   neither can be simulated honestly.

2. **A real ALARP determination from a qualified clinical/regulatory
   SME — a policy judgment, not more evidence.** (Steven / PayloadGuard
   Research *prepares* this determination — see `ALARP_DETERMINATION.md`,
   whose two-role sign-off leaves the SME call `_PENDING_` — but is not
   himself the SME who makes it; Section 2, corrected 2026-07-22.)
   Basis: clause 4.2
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

**What this section does not do:** it does not pick between the two
paths above, does not draft an ALARP justification pretending to be
Steven's words, and does not treat "no more Dafny work is possible" as
license to quietly relabel any hazard `Acceptable`. Section 5's
`Unacceptable` status stands — a real, computed result, not a
placeholder — until Steven picks one of the two paths above and it is
actually carried through.

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
worked examples (which have 44 and 53 explained survivors
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
| 2026-07-15 (later) | R5 resolved: differential-testing harness built between `dosage.py`/`dosage.dfy`; postcondition drift found and fixed | Direct instruction: "let's look into R5 directly." Verified the equivalence claim by direct comparison first, not assumed — branch logic matches exactly for every input where `raw_dose` is finite. Found one new, previously-unflagged issue during that verification: `dosage.py`'s docstring postcondition still said `>= 0`, three months stale against `dosage.dfy`'s own strict-`>` tightening (2026-07-07, Gate C5). Steven chose Option 2 (`AskUserQuestion`), confirmed feasible empirically (`dafny run` executes here) before being offered as the recommendation. Built: `dosage_differential_vectors.py` (9 shared vectors), `dosage_differential_driver.dfy` (generated, calls the real `CalculateHourlyDose` via Dafny's own `include`), `run_verify_dosage_differential.py` (real `dafny run` capture, `raw_dafny_differential_output.txt`/`run_manifest_dafny_differential.json`) → `differential_test_results.json`, all 9 vectors matched. Postcondition drift fixed: `dosage.py` tightened to `> 0` matching `dosage.dfy`, CrossHair re-run and re-verified clean, `traceability_matrix.a.*` and siblings regenerated. `RISK_MANAGEMENT_PLAN.md` §4.1's `HAZ-GIP-1.14`/`1.2`/`1.3` evidence-artifact cells updated to cite the new differential confirmation. Full record: `RISK_MANAGEMENT_FINDINGS.md`. 251 tests pass (5 new) |
| 2026-07-15 (yet later) | Steven's real severity scoring recorded for all 5 hazards (§4.1: `S3 — Serious`, every one); §4.3's matrix and Section 5's overall-residual-risk method both produced real evaluations for the first time | Direct instruction: "start on the severity values for the 5 hazards." Recorded via `AskUserQuestion`, one hazard at a time, against §4.1's real consequence-only bands and each hazard's own documented harm text. **Real, mechanical result: four of five hazards (`HAZ-GIP-1.14`, `1.2`, `1.3`, `HAZ-DOSE-003`) evaluate `Unacceptable` (§4.3: P5 × S3); `HAZ-GIP-1.2b` stays `GAP` at evaluation, blocked only by Finding 5's still-open Probability-side question, not by its now-known Severity. This device's overall residual risk is now `Unacceptable` (Section 5), not `GAP`.** Not a new judgment call by this repo's assistant — a mechanical application of a matrix this plan already specified, now given its first real inputs. The "Path to sign-off" section's two remaining paths (real field data, or a genuine ALARP determination from Steven) are now the live next decision, not a hypothetical one |
| 2026-07-21 | `HAZ-GIP-1.14` narrowed; `HAZ-GIP-1.14b` added (§4.1, §4.3, Section 5, "Path to sign-off") for the clinician-notification residual, parallel to `HAZ-GIP-1.2b`. Severity scored via `AskUserQuestion`: **`S4 — Critical`**, not `S3` — this register's first divergent severity value. Every "all five/every hazard: S3" claim in this document superseded in place (not silently edited) with a pointer to this row | Same trigger as `HAZARD_REGISTER.md`'s parallel change-log entry this date: `CalculateHourlyDose`'s contract ratification (`contract_attestation_dosage.md`) needed an honest Gap-if answer for REQ-GIP-1-8-1 that this repo's existing evidence could not supply. Probability left `GAP`, same Finding 5 basis as `HAZ-GIP-1.2b` — not a new procedural question, the same open one now blocking two rows instead of one. Device-level `Unacceptable` status (Section 5) is unchanged — it was already `Unacceptable` before this addition — but this row cannot resolve past `ALARP` even once Finding 5 is settled, unlike the `S3` rows |

**What does not yet exist, stated explicitly — updated 2026-07-15
(later).** Hazard *identification* (clause 5.4) is real and complete
for this device. The severity **model** (clause 5.5) is real and
correctly structured (consequence-only, per R3's resolution above), and
the per-hazard severity **values** are now real too — `S3 — Serious`,
all five, Steven's determination, recorded above. Evaluation (clauses
6, 8) is correspondingly real: four hazards `Unacceptable`, one
(`HAZ-GIP-1.2b`) still `GAP`, blocked only by Finding 5's open
Probability-side question. What genuinely does not yet exist: a
resolution of that `Unacceptable` finding itself — Steven has not yet
picked between the two paths named in "Path to sign-off" (real field
data, or a recorded ALARP determination), and the risk management
report required by clause 4.5 is still missing entirely.

**Superseded 2026-07-21, not corrected in place:** six hazards, not
five — `S3` for five, `S4` for `HAZ-GIP-1.14b`. Evaluation: still four
`Unacceptable`, now **two** `GAP` (`HAZ-GIP-1.2b` and `HAZ-GIP-1.14b`),
both blocked by the same Finding 5 question. What genuinely does not
yet exist is unchanged in substance — no path has been picked, the
clause 4.5 report is still missing — except that the ALARP path, if
chosen, must now also address a row that cannot reach `Acceptable`
even in the best case, not just `S3` rows that can. Section 6's table
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
either. It carries no authority until a qualified clinical/regulatory
SME reviews and confirms it — Steven / PayloadGuard Research prepares
the material but is not that SME (Section 2, corrected 2026-07-22) —
exactly the distinction this repo has held to for every Gate C6
sign-off.*
