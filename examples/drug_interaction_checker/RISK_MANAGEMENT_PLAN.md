# Risk Management Plan — DOAC Drug-Drug Interaction Checker (POC)

**Document ID:** RMP-DDI-001
**Risk Management File reference:** This plan is part of the risk
management file per ISO 14971:2019 clause 4.4. It does not itself
contain the hazard register, evaluation results, or risk management
report — those are separate documents this plan governs and
references, per clause 4.5's own traceability requirements for the
risk management file as a whole (neither of those documents exists yet
for this device — see Section 8).

**Status:** DRAFT | Version: 0.1 | Last reviewed: 2026-07-14

**Provenance:** Derived from a provisional, externally-supplied
template, cross-checked clause-by-clause against a direct reading of
the real ISO 14971:2019 standard (Third edition, 2019-12) before being
landed here. One citation error found in the template (the "part of
the risk management file" claim was attributed to clause 4.5; it is
actually clause 4.4's own text) — corrected in the header above.
Everything else in the template's clause citations (4.4a–g, and
clause 1's stated exclusions) was verified accurate against the
standard's verbatim text and is preserved below.

---

## 1. Scope (ISO 14971:2019 clause 4.4a)

**Device covered:** DOAC Drug-Drug Interaction Checker (POC) —
`examples/drug_interaction_checker/`.

**Intended use** (verbatim, from `metadata.a.yaml`'s
`device.intended_use`): Check a specific direct oral anticoagulant
(DOAC) and concomitant agent pairing against a known interactions
table, returning an outcome/risk-direction classification, plus the
specific numeric dose-reduction target for the five real cells the
source states one for (REQ-DDI-6) — not a general dose calculator for
every DOAC/agent pairing, since most cells have no numeric figure to
prove at all.

**Life-cycle phases this plan governs:** Design and verification only.
This device is a pre-market proof-of-concept with no manufacturing or
distribution pathway yet defined; production and post-production
sections (Section 7 below) are explicit placeholders, not silently
skipped.

**What this plan does NOT cover:** Per ISO 14971 §1's own exclusions —
clinical decision-making in the context of a specific patient
encounter, and business risk management, are both out of scope by the
standard's own terms, not just this plan's. This checker is decision
*support*; it does not make or override a clinical decision.

---

## 2. Roles and responsibilities (ISO 14971:2019 clause 4.4b)

| Role | Person | Responsibility |
|---|---|---|
| Risk Manager | *(not yet assigned)* | Owns this plan; approves hazard entries |
| Technical/Verification Lead | *(not yet assigned)* | Owns the mechanical evidence (Dafny proofs, gate closures) that risk control claims cite |
| Clinical/Subject Matter Expert | *(not yet assigned)* | Reviews clinical plausibility of hazards and harms |

**GAP, stated explicitly rather than omitted:** no role above is
currently filled by a named person. In particular, no clinical SME has
reviewed this device — `metadata.a.yaml`'s own
`classification_rationale` already flags this: the `B` safety
classification is `DECLARED`, not sourced, "provisional... requires a
manufacturer-specific ISO 14971 risk file before this can be upgraded
from DECLARED to sourced." This document is the start of that file,
not its completion.

---

## 3. Review requirements (ISO 14971:2019 clause 4.4c)

This repository already runs an out-of-cycle review trigger in
practice, ahead of this plan formalizing it: any Gate C6 finding that
touches a proven claim's real-world scope triggers a fresh sign-off
review before the finding is closed. (Concrete precedent: Addenda 1–5
of `nl_confirmation_drug_interaction_checker_dfy.md`, each triggered
by exactly this kind of finding, most recently the 2026-07-13
apixaban orthopaedic-indication scope-leak fix.)

Formalized as policy: any of the following triggers a hazard-register
review before the associated Gate C6 finding is closed —
- a spec-level scope change to `CheckInteraction` or
  `DoseReductionTargetMg` (new `requires`/`ensures` clause, new
  datatype constructor);
- a Gate C5 mutation-testing survivor reclassification (e.g. the
  2026-07-13 STP-suite escalation, which moved 6 survivors to
  `killed_via_stp_suite`);
- any external review report (e.g. the "Gate C Technical Review
  Report" cycle, 2026-07-13) that identifies a real discrepancy.

Cadence for review of the hazard register itself, once it exists: not
yet defined — no hazard register exists yet for this device (see
Section 8).

---

## 4. Risk acceptability criteria (ISO 14971:2019 clause 4.4d)

### 4.1 Severity bands

*(Fill these in only after clinical SME review — this table is a
structure, not a judgment call for an engineering-only draft to make
alone. GAP, stated explicitly: no clinical SME is assigned yet — see
Section 2.)*

This device is a decision-support classifier, not a device that
directly delivers a drug or energy, so the harms are
informational/consequential, not direct physical harms. Severity
bands must be derived from what a wrong or missing classification
could actually cause a clinician or patient to experience — not
reused verbatim from a generic physical-device severity table.

| Severity | Definition | Example specific to this device |
|---|---|---|
| S1 | *(not yet defined)* | e.g. minor, correctable clinical friction — clinician double-checks and catches it before acting |
| S2 | *(not yet defined)* | e.g. a superseded/overly cautious restriction, correctable, no patient harm |
| S3 | *(not yet defined)* | e.g. clinician acts on an unscoped/wrongly-extrapolated dose figure, requiring clinical intervention |
| S4 | *(not yet defined)* | e.g. contributes to a serious, non-recoverable adverse outcome |

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
once individual hazards are entered and evaluated.

---

## 6. Verification activities (ISO 14971:2019 clause 4.4f)

This is where PayloadGuard-Evidence's existing engine plugs in
directly: a risk control measure's implementation and effectiveness
verification can cite a specific Gate C1–C6 closure and evidence-
strength label rather than a fresh verification activity description.
Every row below is a real, currently-committed proof, not a planned
one.

| Requirement | Risk control measure | Verification method | Evidence reference |
|---|---|---|---|
| REQ-DDI-1 | Outcome is always a structured `InteractionResult(outcome, direction)` pair, never a bare boolean | Dafny proof (Gates C1–C6), `CheckInteraction` | `raw_dafny_output_ddi.txt`, `run_manifest_dafny_ddi.json` |
| REQ-DDI-2 | Total, hardcoded pairwise lookup covering all 17 named source sections, no precondition | same | same |
| REQ-DDI-3 | Dabigatran+SSRI/SNRI conditional dose-reduction advice proven on both branches of `hasOtherBleedingRiskFactors` | same | same |
| REQ-DDI-4 | Fail-safe: any unlisted `(doac, agent)` pair returns `NotCovered`, never silently `NoInteractionExpected` | same | same |
| REQ-DDI-5 | Apixaban+inducer outcome correctly scoped by `TreatmentIndication`; orthopaedic-VTE-prophylaxis cells return `NotCovered`, not a fabricated `Caution` | same | same, plus `drug_interaction_checker_stp_suite.dfy` / `raw_dafny_output_ddi_stp_suite.txt` |
| REQ-DDI-6 | `DoseReductionTargetMg` proves the exact mg figure for the 5 sourced cells; Dabigatran+Verapamil correctly indication-scoped | Dafny proof (Gates C1–C6), `DoseReductionTargetMg` | same |

Gate C5 (mutation testing) residual status, current as of 2026-07-13:
1342 mutants generated against `CheckInteraction`/
`DoseReductionTargetMg`; 744 killed, 522 filtered as statically
unreachable, 6 killed via STP-suite escalation, 44 survive, 26
inconclusive (`unclassifiable`). The 44 survivors are a **known,
explained residual** — not an open gap being silently carried — see
`KNOWN_LIMITATIONS.md` for the full account: 37 are explained by
Dafny's function-transparency semantics (same-module STP lemmas
verify by unfolding the function body directly, making mutated
`ensures`-clause wording provably irrelevant to those proofs), 4 by a
vacuous-antecedent pattern, 3 by a redundant-consequent pattern. Full
detail: `mutation_report_ddi.md`.

Note the distinction this repo already enforces: a `PROVEN` label
above means Gate C1–C4's mechanical checks passed, not that a human
has signed off on the requirement's real-world scope — that's Gate
C6, separately. Gate C6 is **closed** for this spec as of 2026-07-13
(`nl_confirmation_drug_interaction_checker_dfy.md`'s "Final review and
Decision" section) — Decision recorded by Steven, confirmed against
the primary sources directly, not rubber-stamped.

---

## 7. Production and post-production information collection (ISO 14971:2019 clause 4.4g)

Not yet applicable. This is a pre-market proof-of-concept with no
manufacturing, distribution, or field-deployment pathway defined —
stated explicitly here rather than left blank with no explanation, per
this repo's own "GAP is rendered explicitly, never omitted" discipline.
When a real deployment path exists, this section needs: what
production/post-production information will be collected (e.g. real
prescribing-decision outcomes, override rates), how it feeds back into
Section 4's probability bands, and who reviews it.

---

## 8. Change log

| Date | Change | Reason |
|---|---|---|
| 2026-07-14 | Initial draft landed for `drug_interaction_checker`, derived from a provisional template cross-checked against ISO 14971:2019 directly | First real risk-management-plan artifact for any worked example in this repo; the six PROVEN requirement rows and Gate C1–C6 status (Section 6) are real and committed, everything requiring clinical judgment (Sections 2, 4.1–4.3, 5) is left as an explicit GAP pending a named Risk Manager and clinical SME |
| 2026-07-14 (later) | `HAZARD_REGISTER.md` landed alongside this plan | Third and last hazard-register artifact in this repo. Distinct construction: no published hazard table exists for this device either, so hazard identification is built from `metadata.a.yaml`'s sourced `REQ-DDI-*` text plus a real, closed hazard incident already documented in full in this spec's own Gate C6 addenda (a fabricated-outcome bug, found by external review and fixed 2026-07-13). Completes clause 5.4 hazard identification for all 6 `REQ-DDI-*` requirements; severity, probability, and risk-acceptability evaluation remain explicit `GAP`s within it |

**What does not yet exist, stated explicitly:** as of the register
above, hazard *identification* (clause 5.4) is real for this device.
Risk *estimation* and *evaluation* (clauses 5.5, 6, 8 — severity,
probability, acceptability) and the risk management report are still
missing — both the register and this plan name them as explicit `GAP`s
rather than fabricating them, pending the same named Risk Manager and
clinical SME Section 2 above still lacks. Section 6's table remains the
model for how a hazard entry's risk control measure should cite
evidence; `HAZARD_REGISTER.md` now does exactly that, per hazard, not
just per requirement.

---

*Template structure derived independently from ISO 14971:2019 clauses
4.4(a–g), the standard's own bracketed requirement list — not copied
from any third-party template's wording, examples, or table layout.
Device-specific content (Sections 1, 3, 6) is drawn from this
repository's own committed, real evidence
(`metadata.a.yaml`, `traceability_matrix.a.md`, `mutation_report_ddi.md`,
`nl_confirmation_drug_interaction_checker_dfy.md`,
`KNOWN_LIMITATIONS.md`) — no clinical judgment (severity, probability,
acceptability) has been fabricated to fill in Sections 2 or 4.*
