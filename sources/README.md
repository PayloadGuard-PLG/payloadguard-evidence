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

## Open questions

- **`FRN` pump-type tag:** the GIP v1.0 source tags several hazards with
  pump type `FRN` without defining the abbreviation in the extracted
  text. See `examples/dosage_calculator/README.md` for the current
  status of this question.
