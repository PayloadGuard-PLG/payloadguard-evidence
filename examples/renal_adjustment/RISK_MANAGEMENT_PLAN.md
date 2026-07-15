# Risk Management Plan — Renal-Function Dose Adjustment (GFR Staging and Formula Selection, POC)

**Document ID:** RMP-RENAL-001
**Risk Management File reference:** This plan is part of the risk
management file per ISO 14971:2019 clause 4.4. It does not itself
contain the hazard register, evaluation results, or risk management
report — those are separate documents this plan governs and
references, per clause 4.5's own traceability requirements for the
risk management file as a whole. **Correction, 2026-07-15**: this
sentence originally said none of those documents existed yet — stale
the same day it was written, since `HAZARD_REGISTER.md` landed
alongside this plan (see Section 8). Corrected: the hazard register
exists and completes clause 5.4 identification; evaluation results
(severity/probability/acceptability, clauses 5.5/6/8) and the risk
management report itself do not yet exist — see Section 8.

**Status:** DRAFT | Version: 0.1 | Last reviewed: 2026-07-14

**Provenance:** Mirrors `examples/drug_interaction_checker/RISK_MANAGEMENT_PLAN.md`,
the first plan built for this repo (2026-07-14), itself derived from a
provisional template cross-checked clause-by-clause against a direct
reading of ISO 14971:2019 (Third edition, 2019-12) before being landed.
The same clause citations (4.4a–g, and clause 1's stated exclusions)
apply unchanged — verified once against the standard's verbatim text,
not re-verified per device, since the citations describe the standard
itself, not this device.

---

## 1. Scope (ISO 14971:2019 clause 4.4a)

**Device covered:** Renal-Function Dose Adjustment — GFR Staging and
Formula Selection (POC) — `examples/renal_adjustment/`.

**Intended use** (verbatim, from `metadata.a.yaml`'s
`device.intended_use`): Stage a patient's renal function (KDIGO
G1–G5), select the correct formula (eGFR vs. Cockcroft-Gault CrCl) per
drug-classification flags, and compose the resulting bound with an
existing dose ceiling. Not a full dosing calculator — see
REQ-RENAL-3/4/6/7 for named, unbuilt extensions.

**Life-cycle phases this plan governs:** Design and verification only.
This device is a pre-market proof-of-concept with no manufacturing or
distribution pathway yet defined; production and post-production
sections (Section 7 below) are explicit placeholders, not silently
skipped.

**What this plan does NOT cover:** Per ISO 14971 §1's own exclusions —
clinical decision-making in the context of a specific patient
encounter, and business risk management, are both out of scope by the
standard's own terms, not just this plan's. This device stages and
bounds; it does not decide or override a clinician's dosing choice.

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
classification is `DECLARED`, not sourced, "requires a
manufacturer-specific ISO 14971 risk file before this can be upgraded
from DECLARED to sourced." This document is the start of that file,
not its completion.

---

## 3. Review requirements (ISO 14971:2019 clause 4.4c)

This repository already runs an out-of-cycle review trigger in
practice, ahead of this plan formalizing it — concrete precedent for
`renal_adjustment` specifically: the 2026-07-09 Gate C4 STP suite run
found two real unpinned-bound gaps in `ComposedCeiling` and
`AssessRenalFunction`, both fixed and re-verified before Gate C6
sign-off proceeded on the corrected spec.

Formalized as policy: any of the following triggers a hazard-register
review before the associated Gate C6 finding is closed —
- a spec-level scope change to any of `renal_adjustment.dfy`'s seven
  functions (new `requires`/`ensures` clause, new formula branch);
- a Gate C5 mutation-testing survivor reclassification;
- resolution of REQ-RENAL-8's currently-open process question (who
  populates the drug-classification flags operationally) — this is a
  named, deliberately parked GAP, not a hypothetical;
- formalization of any of REQ-RENAL-3/4/6/7 as a real Dafny signature
  (all four are currently prose-only, sourced, but unbuilt).

Cadence for review of the hazard register itself: not yet defined.
**Correction, 2026-07-15**: this originally said no hazard register
existed yet, which was already stale when written (`HAZARD_REGISTER.md`
landed the same day, see Section 8) — the register exists, only its
review cadence remains undefined.

---

## 4. Risk acceptability criteria (ISO 14971:2019 clause 4.4d)

### 4.1 Severity bands

*(Fill these in only after clinical SME review — this table is a
structure, not a judgment call for an engineering-only draft to make
alone. GAP, stated explicitly: no clinical SME is assigned yet — see
Section 2.)*

This device is a decision-support classifier/bound-composer, not a
device that directly delivers a drug or energy, so the harms are
informational/consequential, not direct physical harms. Severity bands
must be derived from what a wrong stage, formula choice, or bound
could actually cause a clinician or patient to experience — not
reused verbatim from a generic physical-device severity table.

| Severity | Definition | Example specific to this device |
|---|---|---|
| S1 | *(not yet defined)* | e.g. minor, correctable clinical friction — clinician double-checks and catches a borderline staging call before acting |
| S2 | *(not yet defined)* | e.g. an overly conservative dose ceiling applied, correctable, no patient harm |
| S3 | *(not yet defined)* | e.g. wrong formula selected (eGFR used where Cockcroft-Gault was required) leads to a dose outside the safe range, requiring clinical intervention |
| S4 | *(not yet defined)* | e.g. a missed G4/G5 staging contributes to a serious, non-recoverable adverse outcome |

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
Every `PROVEN` row below is a real, currently-committed proof, not a
planned one; every `DECLARED`/GAP row is named honestly, not silently
dropped.

| Requirement | Risk control measure | Verification method | Evidence reference |
|---|---|---|---|
| REQ-RENAL-1 | GFR category assignment (G1–G5), type-safe by construction so a Cockcroft-Gault CrCl value can never be mis-staged | Dafny proof (Gates C1–C6), `GStage`, `AssessRenalFunction` | `raw_dafny_output_renal.txt`, `run_manifest_dafny_renal.json` |
| REQ-RENAL-1a | eGFR rounded (round-half-up) before staging, shifting effective boundaries | Dafny proof, `RoundHalfUp` | same |
| REQ-RENAL-2 | Formula selection (Cockcroft-Gault vs. eGFR) per the five MHRA-sourced conditions; CrCl computed from raw inputs on the Cockcroft-Gault branch | Dafny proof, `SelectFormula`, `AssessRenalFunction`, `CockcroftGaultCrClMlPerMin`, `AssessRenalFunctionFromInputs` | same |
| REQ-RENAL-3 | Cockcroft-Gault unreliability flag under obesity/oedema | **Not yet formalized** — named, KDIGO-sourced, prose only | none — `intended_method: PROVEN`, realized `GAP` in `traceability_matrix.a.md` |
| REQ-RENAL-4 | Fail-safe on missing/invalid renal-function data (never default to unadjusted full dose) | **Not yet formalized** — named, design invariant, prose only | none — realized `GAP` |
| REQ-RENAL-5 | Bound composition: the more conservative of the existing dose ceiling and the renal-derived ceiling provably wins, pinned exactly | Dafny proof, `ComposedCeiling` | same, plus `renal_adjustment_stp_suite.dfy` / `raw_dafny_output_stp_suite_renal.txt` (Gate C4 found and fixed two real unpinned-bound gaps here, 2026-07-09) |
| REQ-RENAL-6 | AKI reassessment flag on rapidly changing renal function | **Not yet formalized** — named, MHRA-sourced, prose only | none — realized `GAP` |
| REQ-RENAL-7 | BSA-nonindexed eGFR at extremes of body weight for narrow-therapeutic-index drugs | **Not yet formalized** — named, KDIGO-sourced, prose only | none — realized `GAP` |
| REQ-RENAL-8 | Drug-classification flags are caller-supplied, a deliberate, permanent trust boundary (MHRA's drug lists are illustrative, not closed) | `DECLARED` — a process fact, never a Dafny proof target; open item is only *who* populates the flags operationally | none — realized `GAP`, deliberately parked pending operational data |

Gate C5 (mutation testing) residual status, current as of 2026-07-09:
450 mutants across all seven functions; 250 killed, 137 filtered
pre-verification, 2 blocked (`blocked_lvr_clause_literal`), 10
unclassifiable (a genuine Dafny parser-ambiguity limit on
`SelectFormula`'s flat `||` chain, independently covered by Gate C4's
STP suite), **51 survive**. The 51 survivors are a **known, explained
residual** — not an open gap being silently carried — see
`KNOWN_LIMITATIONS.md` for the full account: 33 are ROR/LVR mutations
narrowing a one-way `==>` clause's antecedent (a structural blind spot
of the technique against guard-style clauses, not a proof gap), 17 are
`requires`-clause weakenings the currently-proven `ensures` clauses
don't depend on (the preconditions still correctly document real
domain facts), and 1 is a coincidental numeric survivor on
`RoundHalfUp`, independently resolved by Gate C4's STP suite. Full
detail: `mutation_report_renal.md`.

Note the distinction this repo already enforces: a `PROVEN` label
above means Gate C1–C4's mechanical checks passed, not that a human
has signed off on the requirement's real-world scope — that's Gate
C6, separately. Gate C6 is **closed** for this spec as of 2026-07-11
(`nl_confirmation_renal_adjustment_dfy.md`'s "Decision" section) —
Decision recorded by Steven, confirmed against the raw KDIGO/MHRA
sources directly, not rubber-stamped. One external citation (a
"Sheffield and BSW" clinical-calculator source for the 88.4 µmol/L
conversion factor) was checked and found unverifiable in this repo's
`sources/` directory — flagged, not silently absorbed, and confirmed
not load-bearing for anything this spec actually proves.

---

## 7. Production and post-production information collection (ISO 14971:2019 clause 4.4g)

Not yet applicable. This is a pre-market proof-of-concept with no
manufacturing, distribution, or field-deployment pathway defined —
stated explicitly here rather than left blank with no explanation, per
this repo's own "GAP is rendered explicitly, never omitted" discipline.
When a real deployment path exists, this section needs: what
production/post-production information will be collected (e.g. real
staging-decision outcomes, formula-selection override rates,
REQ-RENAL-8 flag-provenance data once that operational process is
decided), how it feeds back into Section 4's probability bands, and
who reviews it.

---

## 8. Change log

| Date | Change | Reason |
|---|---|---|
| 2026-07-14 | Initial draft landed for `renal_adjustment`, mirroring `drug_interaction_checker/RISK_MANAGEMENT_PLAN.md`'s structure | Second real risk-management-plan artifact in this repo; the five PROVEN requirement rows and Gate C1–C6 status (Section 6) are real and committed, everything requiring clinical judgment (Sections 2, 4.1–4.3, 5) is left as an explicit GAP pending a named Risk Manager and clinical SME, and the four already-named-but-unformalized requirements (REQ-RENAL-3/4/6/7) plus REQ-RENAL-8's open operational question are carried forward honestly rather than glossed over |
| 2026-07-14 (later) | `HAZARD_REGISTER.md` landed alongside this plan | Second real hazard-register artifact in this repo, extending the approach built for `dosage_calculator`. Genuinely different construction: no published hazard table exists for this device, so hazard identification is built from `metadata.a.yaml`'s sourced `REQ-RENAL-*` text and `GATE_1C_AUDIT.md`'s own hand-trace findings (which already name concrete failure modes, including one — the CrCl/eGFR type-confusion risk — closed by a real type-safety redesign, and one — CKD-EPI's caller-supplied value — confirmed as a genuine Dafny/Z3 expressiveness limit, not a choice). Completes clause 5.4 hazard identification for all 8 `REQ-RENAL-*` requirements; severity, probability, and risk-acceptability evaluation remain explicit `GAP`s within it |
| 2026-07-15 | Correction: two sentences in Sections 1 and 3 saying "no hazard register exists yet" were stale the same day they were written | Caught by an external reviewer (Qodo) auditing an unrelated root-README PR (#52) that described this repo's risk-management artifacts as a set — found the plan's own header still denied `HAZARD_REGISTER.md`'s existence despite the very next change-log row above recording its landing. Both sentences corrected in place; no evidence, severity, or probability content changed |

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
(`metadata.a.yaml`, `traceability_matrix.a.md`, `mutation_report_renal.md`,
`nl_confirmation_renal_adjustment_dfy.md`, `KNOWN_LIMITATIONS.md`) — no
clinical judgment (severity, probability, acceptability) has been
fabricated to fill in Sections 2 or 4.*
