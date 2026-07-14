# Hazard Register — DOAC Drug-Drug Interaction Checker (POC)

**Document ID:** HZ-DDI-001
**Part of the risk management file** per ISO 14971:2019 clause 4.5 —
this is the risk *analysis* content (clause 5.4 hazard identification)
`RISK_MANAGEMENT_PLAN.md`'s Section 8 named as not yet existing. Third
and last of this repo's three hazard registers. Like `renal_adjustment`
(and unlike `dosage_calculator`'s GIP v1.0 source), this device has no
published, numbered hazard-analysis document to transcribe from — its
source, `sources/sps-doac-interactions-2024.md`, is an interactions
table, not a hazard analysis. What makes this device's construction
distinct from both prior registers: its own addenda history
(`nl_confirmation_drug_interaction_checker_dfy.md`) already contains a
real, closed hazard incident in full narrative detail — a genuine
fabricated-outcome bug, found by external review and fixed 2026-07-13
— which this register draws on directly rather than reconstructing.

**Status:** DRAFT | Version: 0.1 | Last reviewed: 2026-07-14

**What this register does, and does not, complete.** Same discipline
as both prior registers: hazard identification (clause 5.4) and the
qualitative half of clause 5.5 are real here, grounded in
`metadata.a.yaml`'s sourced `REQ-DDI-*` text and the Gate C6 sign-off
document's own addenda. Severity, probability, and acceptability
evaluation remain explicit `GAP`s, pending the clinical SME and
manufacturer policy `RISK_MANAGEMENT_PLAN.md` Sections 2 and 4 still
don't have.

---

## 1. Scope of this register

One entry per `REQ-DDI-*` requirement (six total). Unlike
`renal_adjustment`, all six are currently `PROVEN` — this device has no
prose-only, unformalized requirements at present. That does not mean
no residual risk exists: Section 2 documents a real bug this device's
own spec carried for a period before being caught and fixed, plus the
current Gate C5 mutation-testing residual. Section 3 names what's
genuinely outside this device's scope.

---

## 2. Hazard entries

### HAZ-DDI-1 — Ambiguous or collapsed interaction outcome

| Field | Value |
|---|---|
| Source | REQ-DDI-1, `metadata.a.yaml`: "The checker returns an `InteractionResult(outcome, direction)` pair, never a bare boolean... every one of the source's 17 sections is headed by exactly this distinction" |
| Hazardous situation | An interaction outcome is collapsed to a bare true/false or a single ambiguous signal, losing the distinction between (for example) `Caution` and `Contraindicated`, or `BleedingRisk` and `ThrombosisRisk` — a clinician acting on a collapsed signal could misjudge severity or the direction of the risk being flagged |
| Risk control measure | `InteractionResult`'s structured return type (7 `outcome` kinds × 4 `direction` kinds) is Dafny-proven for every one of the source's 17 named sections — `CheckInteraction` (`raw_dafny_output_ddi.txt`, `run_manifest_dafny_ddi.json`) |
| Known, named residual | None specific to this requirement beyond the general Gate C5 residual (see below) |
| Potential harm (qualitative, not scored) | Per `metadata.a.yaml`'s own `classification_rationale`: "failure could contribute to a missed contraindication or an over-cautious restriction, given clinician oversight" — reused verbatim rather than inventing new harm language |
| Severity | `GAP` |
| Probability | `GAP` |
| Risk evaluation (acceptable?) | `GAP` |

### HAZ-DDI-2 — Incomplete or incorrect pairwise coverage of the source table

| Field | Value |
|---|---|
| Source | REQ-DDI-2, `metadata.a.yaml`: "a total, hardcoded pairwise lookup covering 17 of the source's 17 named sections" |
| Hazardous situation | A `(doac, agent)` pair the source actually addresses is either missing from the lookup or mapped to the wrong outcome |
| Risk control measure | Dafny-proven totality over the full input domain (as of REQ-DDI-5, no precondition at all — every constructible input is provable) — `CheckInteraction`, same evidence as HAZ-DDI-1 |
| Known, named residual | None specific to this requirement — the two real incidents this register documents in detail (HAZ-DDI-5, HAZ-DDI-6) are indication-scoping bugs on top of an otherwise-complete lookup, not gaps in the lookup's own coverage |
| Potential harm (qualitative, not scored) | Same framing as HAZ-DDI-1 |
| Severity | `GAP` |
| Probability | `GAP` |
| Risk evaluation (acceptable?) | `GAP` |

### HAZ-DDI-3 — Conditional dose-reduction advice wrong on the unexercised branch

| Field | Value |
|---|---|
| Source | REQ-DDI-3, `metadata.a.yaml`: "SSRIs/SNRIs: dabigatran's dose-reduction advice is conditional on a caller-supplied `hasOtherBleedingRiskFactors` flag — both branches proven, not just the one exercised first" |
| Hazardous situation | A boolean-conditional outcome is correct for one value of `hasOtherBleedingRiskFactors` but wrong (or untested) for the other — a class of bug that a test suite exercising only the "obvious" branch could miss entirely |
| Risk control measure | Both branches Dafny-proven explicitly, not just the first one written — same evidence as HAZ-DDI-1 |
| Known, named residual | None specific to this requirement |
| Potential harm (qualitative, not scored) | Same framing as HAZ-DDI-1 |
| Severity | `GAP` |
| Probability | `GAP` |
| Risk evaluation (acceptable?) | `GAP` |

### HAZ-DDI-4 — Missing coverage silently treated as "no interaction" rather than "not covered"

| Field | Value |
|---|---|
| Source | REQ-DDI-4, `metadata.a.yaml`: "Fail-safe: any `(doac, agent)` pair not present in the source's named set — including within-source gaps like apixaban+dronedarone — returns `NotCovered`, never silently `NoInteractionExpected`" |
| Hazardous situation | The most dangerous possible failure mode for a decision-support tool of this kind: an unknown or unaddressed pairing is silently reported as "no interaction," giving false reassurance, rather than an honest "not covered" signal that prompts the clinician to check elsewhere. This is the DDI-checker analogue of `renal_adjustment`'s still-open `HAZ-RENAL-4` (fail-safe on missing data) — **the difference here is that this one is already closed, not open** |
| Risk control measure | Dafny-proven directly: any pair outside the sourced set — including a genuine within-source gap the source itself never states an apixaban outcome for (apixaban+dronedarone) — returns `NotCovered`, never `NoInteractionExpected`. Same evidence as HAZ-DDI-1 |
| Known, named residual | None — worth naming as a genuine strength of this device relative to `renal_adjustment`'s equivalent still-open item, not just a formality |
| Potential harm (qualitative, not scored) | Same framing as HAZ-DDI-1, but this is the one hazard in this register where the harm pathway (false reassurance on an untested pairing) is fully closed by proof, not left as residual |
| Severity | `GAP` |
| Probability | `GAP` |
| Risk evaluation (acceptable?) | `GAP` |

### HAZ-DDI-5 — Apixaban+inducer outcome not correctly scoped to clinical indication

| Field | Value |
|---|---|
| Source | REQ-DDI-5, `metadata.a.yaml`: apixaban's interaction with rifampicin/carbamazepine/phenytoin/phenobarbital depends on a third axis, `TreatmentIndication` (`AFStrokePrevention` \| `RecurrentVTEPrevention` \| `OrthopaedicVTEProphylaxis`) — the source only states an outcome for the first two |
| Hazardous situation | A cell the source never proves an outcome for (apixaban+inducer, orthopaedic-VTE-prophylaxis indication) returns a fabricated outcome instead of an honest `NotCovered` |
| Risk control measure | Each of the four apixaban+inducer match arms now branches on `treatmentIndication` explicitly, returning `NotCovered` for the orthopaedic indication — matching this repo's own `(Apixaban, Dronedarone)` silent-cell convention. Proven: 2 new STP lemmas (`STP_Accept_CheckInteraction_ApixabanRifampicin_OrthopaedicVTEProphylaxis_NotCovered`, `STP_Reject_..._NotCaution`), spec lint's weak-postcondition count for `CheckInteraction` rose to 68 |
| Known, named residual | **This hazard was real, not hypothetical — a genuine incident, documented in full below, not a preemptive "what if."** `nl_confirmation_drug_interaction_checker_dfy.md`'s Addendum 4 (2026-07-13): a second Qodo review, run against an already-merged PR, found that all four apixaban+inducer match arms computed `Caution` **unconditionally** — the code never inspected `treatmentIndication` at all, despite the paired `ensures` clause explicitly guarding on it. This was harmless while `TreatmentIndication` had only two constructors (the guard was always true for every constructible value — mutation testing had already flagged this exact pattern as a "redundant guard" survivor category). Adding the third constructor (`OrthopaedicVTEProphylaxis`), for an unrelated fix on the sibling `DoseReductionTargetMg` function, silently reopened the gap: `CheckInteraction(Apixaban, Rifampicin, _, OrthopaedicVTEProphylaxis)` started returning a fabricated `Caution` the source was never proven to support. Independently re-verified against the real merged source before acting (not trusted on the review's word alone), then fixed as described above. **This is this register's single clearest example of why "proven, given a fixed input domain" is not the same as "proven, given any future extension of that domain"** — the exact risk Gate C6's own Addendum 3 had already named in the abstract, caught here concretely on a sibling function |
| Potential harm (qualitative, not scored) | Same framing as HAZ-DDI-1, but concretely: a fabricated `Caution` (rather than `NotCovered`) for an indication the source is silent on could either under- or over-state the real risk — the direction isn't determinable from the bug itself, which is exactly why the fix returns the honest "not covered" rather than guessing a direction |
| Severity | `GAP` |
| Probability | `GAP` |
| Risk evaluation (acceptable?) | `GAP` |

### HAZ-DDI-6 — Numeric dose-reduction target wrong or unscoped

| Field | Value |
|---|---|
| Source | REQ-DDI-6, `metadata.a.yaml`: `DoseReductionTargetMg` proves the specific mg figure for the five real cells the source states one for (Dabigatran+Verapamil: 110mg; Edoxaban+{Dronedarone, ErythromycinSystemic, Ketoconazole, Ciclosporin}: 30mg each) |
| Hazardous situation | The wrong numeric dose-reduction figure is returned for a cell, or a figure is returned for a cell/indication the source never actually states one for |
| Risk control measure | Dafny-proven per cell, each pinned to its individually-sourced figure — apixaban is excluded from this function's precondition entirely, a direct, confirmed consequence of `CheckInteraction` never producing `DoseReductionAdvised` for apixaban anywhere (not a hand-written exclusion). Dabigatran+SSRIOrSNRI is deliberately, permanently excluded — the source gives no mg figure for that cell at all, correctly left informational-only rather than guessed |
| Known, named residual | A second real, closed instance of the same indication-scoping risk as HAZ-DDI-5: the Dabigatran+Verapamil cell was found to need indication-scoping too — the source's 110mg figure applies only to AF-stroke-prevention and DVT/PE-prevention-and-treatment, not dabigatran's third UK-licensed indication (primary VTE prevention after elective hip/knee replacement surgery, confirmed via `sources/emc-smpc-dabigatran-indications-2025.md`) — a genuine source-silent cell for that third indication, now provably excluded via the same `TreatmentIndication` axis rather than left silently unaddressed |
| Potential harm (qualitative, not scored) | An incorrect or unscoped mg figure reaching a clinician could directly translate into an incorrect prescribed dose — arguably the most direct physical-harm pathway in this register, since the other five hazards are classification/informational, not numeric |
| Severity | `GAP` |
| Probability | `GAP` |
| Risk evaluation (acceptable?) | `GAP` |

---

Gate C5 (mutation testing) residual status, current as of 2026-07-13:
1342 mutants against `CheckInteraction`/`DoseReductionTargetMg`; 744
killed, 522 filtered as statically unreachable, 6 killed via STP-suite
escalation, **44 survive**, 26 inconclusive (`unclassifiable`). The 44
survivors are a **known, explained residual, not a silently-carried
gap** — full detail in `KNOWN_LIMITATIONS.md` and `mutation_report_ddi.md`:
37 are explained by Dafny's function-transparency semantics (same-
module STP lemmas verify by unfolding the function body directly,
making mutated `ensures`-clause wording provably irrelevant to those
proofs), 4 by a vacuous-antecedent pattern (`CheckInteraction`'s LOR
survivors), 3 by a redundant-consequent pattern (the SSRIOrSNRI ROR
survivors, independently proven by sibling `ensures` clauses). Gate C6
is **closed** for this spec — `nl_confirmation_drug_interaction_checker_dfy.md`'s
"Final review and Decision" section: **Confirmed, 2026-07-13, by
Steven**, following a full independent line-by-line review against the
raw sources and a two-round cross-check of an externally-produced
technical review report (which itself required real corrections before
being trusted).

---

## 3. Explicitly out of scope (named, not omitted)

- **Multi-drug (more than pairwise) interactions.** `CheckInteraction`
  takes exactly one DOAC and one concomitant agent — a real patient on
  three or more interacting drugs simultaneously has compounding risk
  this function does not model at all.
- **Non-DOAC anticoagulants.** The source, and this device, are
  DOAC-specific (dabigatran, edoxaban, rivaroxaban, apixaban) —
  warfarin and other vitamin-K antagonists are entirely outside scope.
- **Jurisdiction.** `sources/sps-doac-interactions-2024.md` is a UK
  (NHS) source; this session's own earlier research
  (`sources/fda-eliquis-label-interactions-2016.md`) confirmed the US
  FDA label states materially different management for at least one
  interaction — this checker's outcomes reflect UK clinical practice
  specifically, not a jurisdiction-agnostic standard.
- **Quantitative patient-specific risk scoring.** The checker returns
  the source's own qualitative categories (`Caution`, `Avoid`,
  `Contraindicated`, etc.) — it does not compute a HAS-BLED-style score
  or any other patient-specific numeric risk estimate.
- **Renal function.** `hasOtherBleedingRiskFactors` is an opaque,
  caller-supplied flag — this device does not itself assess or stage
  renal function, even though DOAC dosing and interaction management
  both depend on it in practice. See `examples/renal_adjustment/` for
  the device that addresses that hazard surface specifically; the two
  are not currently wired together.

---

## 4. Change log

| Date | Change | Reason |
|---|---|---|
| 2026-07-14 | Initial draft: 6 hazard entries (one per `REQ-DDI-*`), Gate C5 residual note, explicitly-out-of-scope section | Third and final hazard register in this repo. Distinct from both prior registers in one real way: this device's own Gate C6 addenda history already contains a real, closed hazard incident (Addendum 4's fabricated-`Caution` bug) documented in full narrative detail, drawn on directly rather than reconstructed |

---

*Hazard identification (Section 2's `Source`, `Hazardous situation`,
and `Risk control measure` fields, and the real incidents documented
under `HAZ-DDI-5`/`HAZ-DDI-6`) is drawn directly from this repo's own
committed evidence (`metadata.a.yaml`,
`nl_confirmation_drug_interaction_checker_dfy.md`,
`traceability_matrix.a.md`, `mutation_report_ddi.md`) — not fabricated.
Severity, probability, and risk-acceptability evaluation are explicit
`GAP`s, same discipline as both prior registers and
`RISK_MANAGEMENT_PLAN.md`: this register identifies hazards; it does
not yet estimate or evaluate risk, per ISO 14971:2019 clauses 5.5, 6,
and 8, which require the clinical SME and manufacturer policy
`RISK_MANAGEMENT_PLAN.md` Sections 2 and 4 still name as unassigned.*
