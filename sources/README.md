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
- `gip-v1.0-full-2009.pdf` — added 2026-07-15. The actual GIP v1.0 PDF
  (17 pages, complete — Introduction through §4 Conclusion and Future
  Work), obtained directly from the University of Pennsylvania and
  supplied by Steven, not a third-party mirror. Used to independently
  re-verify `gip-v1.0-hazard-analysis.md`'s own transcription against
  the real primary text — found and fixed one real wording drift in
  Safety Requirement 1.8.1 (reverse delivery), confirmed the full
  §2.4.1 Operational Hazards table (HID 1.1–1.28) matches, and
  confirmed **no hazard table in this document, across all eight
  categories, carries a severity column for any hazard** — GIP v1.0
  itself never scores severity, a source-backed fact now citable
  directly rather than inferred from `metadata.a.yaml`'s
  `classification_rationale`. Full account:
  `examples/dosage_calculator/RISK_MANAGEMENT_FINDINGS.md`.
- `iec-60601-2-24-1998.pdf` — added 2026-07-15 (later). IEC 60601-2-24,
  First edition, 1998-02, "Medical electrical equipment — Part 2-24:
  Particular requirements for the safety of infusion pumps and
  controllers" — the actual edition GIP v1.0 (Feb 2009) cites, obtained
  and supplied by Steven, read in full (58 pages, cover through Annex
  ZB). Used to independently verify GIP Safety Requirement 1.8.1's own
  citation, one hop further than `gip-v1.0-full-2009.pdf` alone could
  reach: clause **51.102 "Reverse delivery"** (p.36, no Annex AA
  rationale marker) reads "During NORMAL USE and/or SINGLE FAULT
  CONDITION of the EQUIPMENT, continuous reverse delivery, which may
  cause a SAFETY HAZARD, shall not be possible" — GIP's own
  transcription is a near-verbatim match, omitting only the "which may
  cause a SAFETY HAZARD" clause. This is this repo's first direct read
  of the IEC 60601-2-24 standard text itself, not a secondary source.
  Full account: `examples/dosage_calculator/RISK_MANAGEMENT_FINDINGS.md`
  Finding 6.
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
  the original scoping document. **Amended 2026-07-09** — the
  round-half-up tie-break rule this document originally implied was
  "KDIGO's own convention" was challenged directly and found
  unsupported: KDIGO states no tie-breaking method at all, and an
  authoritative implementation-guidance paper (Miller et al., *Clin
  Chem* 2022;68(4):511-520, PMID 34918062) explicitly defers the tie
  case to each laboratory's own information-system software. Corrected
  in place; the base rounding requirement remains KDIGO-sourced, only
  the tie-break specifically was overclaimed.
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
  standard unit-conversion arithmetic behind the commonly-used rounded
  1.23/1.04 multiplier — **corrected 2026-07-09**: a direct re-fetch of
  the MHRA source page found MHRA states no formula or constants at all;
  1.23/1.04 was mischaracterized here as "MHRA's constants" when it's
  just 88.4/72 (and ×0.85) applied to the sourced 1976 formula, not an
  MHRA-specific number (see `mhra-renal-formula-selection-2019.md`'s
  2026-07-09 amendment) — and **corrects**
  a fabricated citation: the supplied document's claimed NICE NG203
  recommendation numbers and quoted text (1.1.2 mandating the 2009
  equation, 1.1.4 barring ethnicity-based eGFR adjustment) do not exist
  in the real guideline — verified directly by fetching NICE NG203's
  actual recommendations list. The real picture, per an independent 2024
  UK study (Roy et al., *Nephron*, PMID 39342928), is that UK lab
  practice is heterogeneous and in transition, not settled on any single
  equation version.

- `emc-smpc-apixaban-posology-2024.md` — added 2026-07-12. Two eMC
  Summaries of Product Characteristics (products 2878, 5 mg; 4756, 2.5
  mg), revised 04 January 2024. Verifies an external research document's
  claims about apixaban's NVAF "2-of-3" dose-reduction rule and the
  hip/knee VTE-prophylaxis regimen. Per rule 2 above: **confirms**, from
  a second independent primary source, `sps-doac-interactions-2024.md`'s
  own finding that apixaban drug-interaction guidance is qualitative
  only (no numeric dose figure anywhere on either SmPC); **extends** the
  requirements table with new, citable ground for a posology axis
  `examples/drug_interaction_checker/` does not currently model. Does
  not resolve `REQ-DDI-6`'s interaction-numeric gap for apixaban — see
  `fda-eliquis-label-interactions-2016.md` below.
- `mhra-dsu-doac-renal-dosing-2023.md` — added 2026-07-12. MHRA Drug
  Safety Update volume 16, issue 10, May 2023, renal-impairment dosing
  table. Per rule 2 above: **confirms**, from a third independent
  primary source, that apixaban's UK dosing guidance is genuinely
  indication-branched (the same structural pattern `REQ-DDI-5`'s scoping
  identified for drug interactions, here shown for renal severity
  instead); **extends** the posology picture with the renal-severity
  axis. Not currently cited by any requirement.
- `fda-eliquis-label-interactions-2016.md` — added 2026-07-12. US FDA
  ELIQUIS prescribing information §7.1, accessed via DailyMed.
  Deliberately a non-UK contrast source, not a substitute for UK
  guidance — every other apixaban/DOAC source in this folder is
  UK-jurisdiction. Per rule 2 above: **confirms** a genuine
  jurisdictional divergence an external research document identified:
  the US label states a numeric (50%) interaction-based dose reduction
  for apixaban that no UK source states. Not currently cited by any
  requirement; recorded to support an explicit, citable statement of
  where UK and US guidance diverge, should that ever become relevant to
  a scoping decision.

- `emc-smpc-dabigatran-indications-2025.md` — added 2026-07-13. Two eMC
  Summaries of Product Characteristics for Pradaxa (dabigatran; product
  6229, 110 mg, revised 16 January 2025; product 4703, 150 mg, for
  §4.1 comparison). Fetched to verify a Gate C6 review finding
  questioning whether `TreatmentIndication`'s two constructors cover
  dabigatran's real licensed indication set. Per rule 2 above:
  **confirms** `sps-doac-interactions-2024.md`'s own stated scope for
  the verapamil dose-reduction row (tied specifically to the two
  twice-daily indications, NVAF and DVT/PE) and that its two partial
  phrasings of the DVT/PE indication refer to the same single
  eMC-licensed category `RecurrentVTEPrevention` already models — no
  new constructor needed for that specific naming concern. **Corrects/
  extends**: dabigatran has a real, current, third UK-licensed
  indication (primary VTE prevention after elective hip/knee
  replacement, a structurally different once-daily regimen) that
  `TreatmentIndication` does not represent at all, and that
  `sps-doac-interactions-2024.md`'s verapamil row is silent on. Does
  not resolve, by itself, whether `TreatmentIndication` should gain a
  third constructor — see
  `examples/drug_interaction_checker/nl_confirmation_drug_interaction_checker_dfy.md`'s
  "Addendum 3" for the open design decision this leaves for Steven.
- `ISO-24971-2020.pdf` — added 2026-07-15, obtained and committed
  directly by Steven, not via this repo's assistant. ISO/TR 24971:2020(E),
  second edition, "Medical devices — Guidance on the application of ISO
  14971" — marked "PROOF/ÉPREUVE" (pre-publication proof copy) on its
  own title page; noted, not treated as invalidating its content. Per
  rule 2 above: **corrects** the risk-management plan's prior "ISO
  14971's own Annex D" citation (the 2019 edition's own Table B.1
  records the 2007 edition's Annex D as moved to this document, not
  retained as an annex — see `RISK_MANAGEMENT_FINDINGS.md` Finding 2
  and `RISK_MANAGEMENT_PLAN.md` §4.3's citation correction); **extends**
  the severity/probability discussion via §5.5.3 (risks with inestimable
  probability evaluated on severity alone, not the full matrix) and
  §5.5.4 (severity levels must exclude any element of probability — see
  `RISK_MANAGEMENT_FINDINGS.md` Finding 3), and supplies the actual
  three-region acceptance-matrix source (Annex C.4, Figure C.1) the
  plan's matrix structure is modelled on, though the plan's own region
  *labels* have not yet been reconciled to this source's wording — open
  item, `RISK_MANAGEMENT_FINDINGS.md`'s "matrix region naming" entry.
- `ISO-26262-3-2018.pdf` — added 2026-07-16, obtained and committed
  directly by Steven (pushed straight to `main` via GitHub's web
  upload), not via this repo's assistant. ISO 26262-3:2018(E), second
  edition, "Road vehicles — Functional safety — Part 3: Concept phase."
  **Confirmed PARTIAL — this is the iTeh "STANDARD PREVIEW" excerpt,
  not the full purchased standard**: 12 pages, encrypted (RC4,
  print/copy allowed, no edit/annotate), against a real document whose
  own table of contents runs to page 28 plus a Bibliography. Read
  directly via the `Read` tool before this entry was written, same
  discipline as every other file in this folder.

  **What this file actually contains** (real, citable): Clause 1
  (Scope) in full; Clause 2 (Normative references) in full; Clause 3
  (Terms and definitions, a pointer to ISO 26262-1) in full; Clause 4
  (Requirements for compliance, 4.1–4.6) in full; Clause 5 (Item
  definition) partial — 5.1 Objectives, 5.2 General, 5.3 Inputs, and
  5.4.1's requirement list (a)–(e) with its three notes, cutting off
  immediately after.

  **What this file does NOT contain, and it's the part that matters
  most for building any risk-management artifact for `aeb_kernel`**:
  Clause 6 (Hazard analysis and risk assessment — situation analysis,
  hazard identification, classification of hazardous events,
  determination of safety goals) and Clause 7 (Functional safety
  concept — derivation of functional safety requirements, safety
  validation criteria) are both entirely absent; so are Annex A
  (overview/workflow of the concept phase), Annex B (a worked hazard
  analysis and risk assessment example), and the Bibliography. These
  are the clauses that would play the role ISO 14971 played for the
  three medical-device examples' hazard registers/risk-management
  plans — **no ISO 26262 risk-management artifact should be built from
  this file alone**.

  **Update, 2026-07-16 (later):** Table 4 (ASIL determination) and
  Clause 6.4.4 (Determination of safety goals) — the two most
  operationally load-bearing pieces of Clause 6 — are now sourced for
  real, verbatim, from a different, independent fragment: see
  `iso-26262-3-2018-table4-and-6.4.4.md` below. Steven's explicit
  decision on cost/scope: `aeb_kernel` is a proof-of-concept testing
  architecture generalization, not a real regulatory submission ("lives
  aren't on the line... this is a big ass test environment") — paying
  for the full standard to source two clauses wasn't warranted once a
  legitimate free verbatim source was found and independently verified.
  Still not sourced: 6.4.1 (Initiation), 6.4.2 (Situation analysis and
  hazard identification — the actual HARA methodology), 6.4.3.1–.10
  (the classification methodology itself, as opposed to just its output
  table), 6.4.5 (Management of variances — not relevant to `aeb_kernel`'s
  light-vehicle scope regardless), 6.4.6 (Verification), and all of
  Clause 7 (Functional safety concept). Full account:
  `examples/aeb_kernel/PHASE1_PLAN.md`, `DEVLOG.md`'s 2026-07-16 entry.

- `iso-26262-3-2018-table4-and-6.4.4.md` — added 2026-07-16. Verbatim
  transcription of Table 4 (ASIL determination) and Clause 6.4.4
  (Determination of safety goals), sourced from an unusual but
  legitimate provenance: a 2-page PDF (page 10 of the real standard)
  bundled as a regression-test fixture in the open-source PyMuPDF
  library's test suite, obtained via Debian's official source-package
  mirror, originally attached to a public PyMuPDF GitHub issue as an
  incidental table-extraction bug report. Cross-checked and confirmed
  authentic against `ISO-26262-3-2018.pdf`'s own table of contents (the
  page-10 location for "6.4.4 Determination of safety goals" matches
  exactly). Also documents a real, checked correction to a pasted
  secondary-source ASIL table that had three wrong cells, and a
  follow-up "resolution" message whose "C1 always defaults to QM"
  claim and Clause 7.4.3 title claim were both directly falsified by
  this real text — full triangulation account in the file itself.

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
