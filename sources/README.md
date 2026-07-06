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
