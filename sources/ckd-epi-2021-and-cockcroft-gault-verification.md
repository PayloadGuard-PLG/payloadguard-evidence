# CKD-EPI 2021 equations and Cockcroft-Gault historical constants — independent verification

**Context:** Steven supplied a "research findings" document (external knowledge
base, explicitly flagged by him as unverified) proposing exact numeric
equations to close Gate 1c's Finding 1 (no function computes the actual
CrCl/eGFR value — see `examples/renal_adjustment/GATE_1C_AUDIT.md`) plus a
Dafny/Z3 architecture strategy. Every checkable claim was independently
verified against primary/authoritative sources before any of it was
accepted, per this repo's discipline. Verified 2026-07-08.

## Confirmed: the 2021 CKD-EPI creatinine-only eGFR equation (eGFRcr, race-free)

Independently checked against the National Kidney Foundation's own
published equation (not the supplied document alone):

> eGFR = 142 × min(Scr/κ, 1)^α × max(Scr/κ, 1)^−1.200 × 0.9938^Age × 1.012 [if female]

Constants: scaling constant 142; age-coefficient base 0.9938;
female multiplier 1.012; κ (kappa) = 0.7 female / 0.9 male; α (alpha) =
−0.241 female / −0.302 male. **Matches the supplied document exactly.**

Primary source for the equation's existence and derivation methodology:
Inker LA, Eneanya ND, Coresh J, et al. "New Creatinine- and Cystatin
C-Based Equations to Estimate GFR without Race." *N Engl J Med*.
2021;385(19):1737-1749. PMID 34554658, PMCID PMC8822996, DOI
[10.1056/NEJMoa2102953](https://doi.org/10.1056/NEJMoa2102953). Full text
fetched directly via PubMed Central — confirms the paper describes this
equation (the race-free "AS," age-and-sex-only creatinine equation) but
the numeric coefficient table (Table 2) does not render as extractable
text from that source; the exact constants above were corroborated via
the National Kidney Foundation's independently published equation page
instead, not assumed from the primary paper's prose alone.

## Confirmed: the 2021 CKD-EPI creatinine-cystatin C eGFR equation (eGFRcr-cys)

Independently checked, same NKF source family:

> eGFRcr-cys = 135 × min(Scr/κ, 1)^α × max(Scr/κ, 1)^−0.544 × min(Scys/0.8, 1)^−0.323 × max(Scys/0.8, 1)^−0.778 × 0.9961^Age × 0.963 [if female]

Constants: scaling constant 135; age-coefficient base 0.9961; female
multiplier 0.963; creatinine κ = 0.7 female / 0.9 male; creatinine α =
−0.219 female / −0.144 male; cystatin C κ = 0.8 (both sexes); cystatin C
min-term exponent −0.323; cystatin C max-term exponent −0.778 (both
sexes). **Matches the supplied document exactly.** Same primary source
as above (Inker et al. 2021).

## Corrected: UK NHS practice does NOT mandate "2009 CKD-EPI, race modifier removed" — the supplied document's citation was wrong

The supplied document claimed NICE NG203 "Recommendation 1.1.2 mandates
the 2009 equation" and "1.1.4 explicitly states: 'Do not use a person's
ethnicity to adjust their eGFR.'" **Both citations are wrong, verified
directly against the primary source:**

- NICE NG203's actual Recommendation 1.1.2 (fetched directly,
  https://www.nice.org.uk/guidance/ng203/chapter/Recommendations) states
  only: *"use the Chronic Kidney Disease Epidemiology Collaboration
  (CKD-EPI) creatinine equation to estimate GFRcreatinine for adults..."*
  — **no equation version (2009 vs. 2021) is specified anywhere in the
  guideline.**
- NICE NG203's actual Recommendation 1.1.4 states: *"Advise adults not
  to eat any meat in the 12 hours before having a blood test for
  eGFRcreatinine."* Nothing about ethnicity.
- The actual ethnicity-related recommendation is **1.1.24**: *"Do not
  use any of the following as risk factors indicating testing for CKD
  in adults, children and young people: age, gender, ethnicity..."* —
  this is about screening risk factors, not about eGFR equation
  selection or race-based adjustment of the calculation itself.

**The real picture, from a directly on-point independent source:** Roy R,
Green D, Raman M, Dark PM, Kalra PA. "Adoption of CKD-EPI (2021) for
Glomerular Filtration Rate Estimation: Implications for UK Practice."
*Nephron*. 2024/2025;149(3):133-. PMID 39342928, PMCID PMC11878410, DOI
[10.1159/000541689](https://doi.org/10.1159/000541689). Full text fetched
directly. Key findings, quoted:

> "In 2021, the NKF recommended the use of updated CKD-EPI equations
> which no longer carried within them coefficients related to ethnicity
> or racial group. The UK has followed the example from the USA and now
> advises that equation adjustments made for race or ethnicity may not
> be accurate. With this in mind, it is likely that an increasing
> number of biochemistry laboratories in the UK will move to using the
> updated CKD-EPI equation to report eGFR."

This is a **trend, not a settled mandate** — the same paper's own study
data shows the standard result at their major NHS teaching hospital
(Salford Royal, Northern Care Alliance NHS Foundation Trust) was
**MDRD**, not even CKD-EPI 2009, as of their study period. **Conclusion:
UK practice is heterogeneous and in transition; there is no citable
"UK mandates X equation" claim as of this verification.** The supplied
document's specific recommendation numbers and quoted text do not exist
in the real NICE NG203 page — a clear case of a plausible-sounding but
fabricated citation, caught by fetching the primary source directly
rather than trusting the summary.

## Confirmed: the original 1976 Cockcroft-Gault formula and the MHRA constant derivation

Primary source: Cockcroft DW, Gault MH. "Prediction of creatinine
clearance from serum creatinine." *Nephron*. 1976;16(1):31-41. PMID
1244564, DOI [10.1159/000180580](https://doi.org/10.1159/000180580) —
confirmed as the correct paper via PubMed metadata (abstract states the
formula predicts creatinine clearance in adult males with "15% less in
females," consistent with a ×0.85 female multiplier). The exact original
formula text is not machine-extractable from PubMed's abstract record
for this 1976 paper (pre-dates full-text digitization); independently
corroborated via a secondary peer-reviewed source (a *New Zealand
Medical Journal* "friendly deconstruction" paper on the Cockcroft-Gault
formula):

> CrCl (men) = (140 − age) × weight(kg) / (72 × Scr[mg/dL])
> CrCl (women) = above × 0.85

**Matches the supplied document.** The mg/dL→µmol/L conversion factor
(88.4) is standard clinical chemistry. Arithmetic check: 88.4/72 =
1.2278; ×0.85 = 1.0436 — consistent with the MHRA's rounded 1.23
(male)/1.04 (female) constants (`sources/mhra-renal-formula-selection-2019.md`).

**One correction to the supplied document's own reasoning, not its
numbers:** the document frames "72" as purely a units-conversion
artifact. Independent sources instead attribute it to the *average body
weight (~72kg) of the 1976 study cohort* — a historical coincidence, not
a derived conversion constant. This doesn't change any number used in
this repo's spec, but the original document's causal story for why "72"
appears is not well-supported and shouldn't be repeated as fact.

## Not independently verified (out of scope for this pass)

- Whether the specific numeric coefficients above are correctly
  transcribed in NKF's page relative to the NEJM paper's actual Table 2
  (the primary paper's table did not render as extractable text; the
  NKF page is treated as a reliable secondary transcription, consistent
  with NKF's role as the co-sponsoring body of the original 2020 Task
  Force that commissioned the equations, but this is not the same as
  reading Table 2 directly).
- The Dafny/Z3 architectural strategy proposed alongside the clinical
  data is a separate engineering question, evaluated on its own terms in
  `examples/renal_adjustment/GATE_1C_AUDIT.md`'s Finding 1 discussion —
  not a sourcing question, so not covered by this document.
