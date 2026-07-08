# Sources

This folder holds primary source documents (hazard analyses, safety
requirements documents, standards excerpts) that ground the claims in
`examples/*/metadata.yaml`. When a new document is added here:

1. Read it closely before touching any metadata.yaml.
2. Check whether it **confirms, corrects, or extends** anything already
   in metadata.yaml. Note all three cases explicitly.
3. Never silently overwrite an existing requirement, hazard, or
   citation based on a new source. Propose the change (as a diff or a
   clearly marked "PROPOSED UPDATE" note) for human review instead.
4. If the new document resolves a previously-flagged GAP or unresolved
   term (see the `dosage_calculator/README.md` open-questions list),
   say so explicitly and cite the exact page/section.
5. If it doesn't resolve anything relevant, say that too — silence is
   not an acceptable output when a new source is added.

## Contents

- `gip-v1.0-hazard-analysis.md` — Arney, Jetley, Jones, Lee, Ray,
  Sokolsky, Zhang (2009), "Generic Infusion Pump Hazard Analysis and
  Safety Requirements v1.0," University of Pennsylvania / FDA OSEL /
  Fraunhofer CESE. Audit-trail record behind
  `examples/dosage_calculator/metadata.yaml`.
- `req-gip-1-4-12-alarm-scope-decision.md` — added 2026-07-05 (Gate 1
  review). Per rule 2 above: this document **extends** the existing
  REQ-GIP-1-4-12 entry (dual-scope split per IEC 60601-1-8's ALARM
  CONDITION / ALARM SIGNAL separation) and **corrects** its prior
  single-claim framing — the concrete evidence verified condition
  detection, not signal emission. It does not confirm, correct, or
  extend any other requirement, threat, or citation, and it does not
  resolve the FRN open question below.
- `KDIGO-2024-CKD-Guideline.pdf` — added 2026-07-08. KDIGO 2024 Clinical
  Practice Guideline for the Evaluation and Management of Chronic Kidney
  Disease, *Kidney International* (2024) 105(Suppl 4S), S117–S314.
  Primary clinical source for the renal-adjustment POC's Phase 1 (GFR
  staging categories, eGFR reporting/rounding convention,
  Cockcroft-Gault reliability limitations).
- `kdigo-2024-gfr-staging.md` — added 2026-07-08. Per rule 2 above: this
  document **confirms** the renal-adjustment scoping document's GFR
  category boundaries (G1–G5) exactly, **extends** the boundary-
  inclusivity question with KDIGO's own eGFR-rounding convention (the
  effective continuous G1/G2 boundary is 89.5, not 90.0, once rounding
  is accounted for — flagged as an open Gate 1b design decision, not
  resolved here), and **partially resolves** REQ-RENAL-3's citation gap
  (corroborates the obesity/oedema half via KDIGO rather than MHRA; the
  "unstable renal function" half remains unresolved). Also surfaces a
  new proposed requirement, REQ-RENAL-7, from Practice Point 4.2.4 (BSA
  de-normalization for narrow-therapeutic-index drugs), not present in
  the original scoping document.
- `mhra-renal-formula-selection-2019.md` — added 2026-07-08. Per rule 2
  above: this document **confirms** REQ-RENAL-2's five formula-selection
  conditions directly against the primary MHRA page, and **upgrades**
  the BMI-boundary citation for "extremes of muscle mass": MHRA's own
  text states `BMI <18 kg/m2 or >40 kg/m2` verbatim (strict inequality),
  verified directly rather than only via NHS Tayside's secondary
  restatement of the same MHRA text. Also **names as weaker than
  initially proposed** two ClinicalTrials.gov citations (NCT02942810,
  NCT02039817) offered as independent corroboration — both are real,
  verified trials using a similar BMI eligibility range, but for general
  PK-study screening, not as a validation of MHRA's specific threshold;
  recorded as corroborating, not confirming.
- `ckd-epi-2021-and-cockcroft-gault-verification.md` — added 2026-07-08.
  Independently verifies a "research findings" document Steven supplied
  (explicitly flagged by him as unverified external knowledge) proposing
  data to close Gate 1c's Finding 1. Per rule 2 above: this document
  **confirms** the 2021 CKD-EPI creatinine-only and creatinine-cystatin C
  eGFR equations exactly (checked against the National Kidney
  Foundation's own published equations, not the supplied document
  alone), **confirms** the original 1976 Cockcroft-Gault formula and the
  arithmetic behind MHRA's rounded 1.23/1.04 constants, and **corrects**
  a fabricated citation: the supplied document's claimed NICE NG203
  recommendation numbers and quoted text (1.1.2 mandating the 2009
  equation, 1.1.4 barring ethnicity-based eGFR adjustment) do not exist
  in the real guideline — verified directly by fetching NICE NG203's
  actual recommendations list. The real picture, per an independent 2024
  UK study (Roy et al., *Nephron*, PMID 39342928), is that UK lab
  practice is heterogeneous and in transition, not settled on any single
  equation version.

## Resolved questions

- **`FRN` pump-type tag (resolved 2026-07-05):** the GIP v1.0 source tags
  several hazards with pump type `FRN` without defining the abbreviation
  in the extracted text. `FRN` = FDA Product Code for "Infusion Pump"
  (21 CFR 880.5725); within the GIP taxonomy specifically, denotes
  general-purpose volumetric infusion pumps (peristaltic mechanism,
  cassette-based administration set), distinct from the `All` tag used
  elsewhere in the source's hazard tables. Resolved via NotebookLM's
  extraction of the full source PDF, cross-checked against independent
  FDA-registry research landing on the same product code. Per rule 4
  above: this resolves the previously-flagged open term. Caveat carried
  forward, not silently dropped: well-supported, but **not yet
  independently re-verified against the raw Sec 2.4.1 text** of the
  source document itself — no new primary-source file was added to this
  folder for this resolution (the extraction is a research finding about
  an existing archived source, not a new document). See
  `examples/dosage_calculator/README.md` and `KNOWN_LIMITATIONS.md` for
  the full status.
  Prior failed resolution attempts (web search for GIP project pages;
  direct retrieval of `rtg.cis.upenn.edu/gip-UPenn/` and the UPenn
  `cis_reports/893` tech-report page — host unreachable / HTTP 403 from
  this environment) are preserved in the dev log for the record.
