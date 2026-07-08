# KDIGO 2024 CKD Guideline — GFR staging, rounding convention, and Cockcroft-Gault reliability

**Source:** KDIGO 2024 Clinical Practice Guideline for the Evaluation and
Management of Chronic Kidney Disease. *Kidney International* (2024)
105(Suppl 4S), S117–S314. Full PDF committed at
`sources/KDIGO-2024-CKD-Guideline.pdf` (added to this repo 2026-07-08).
Text below extracted directly from that committed PDF (manual
zlib/content-stream extraction — no PDF-rendering tool was available in
this environment; extraction verified by cross-checking the recovered
table numbers, page footers, and practice-point numbering against the
source's own internal citation scheme, not just trusted as parsed).

Per `sources/README.md` rule 2 — what this **confirms, corrects, or
extends** relative to the renal-adjustment POC's Phase 1 scoping
document (uploaded 2026-07-08, not yet committed to this repo as of this
writing):

## Confirms: the exact GFR category table (page S126)

From "Current Chronic Kidney Disease (CKD) Nomenclature Used by KDIGO,"
p. S126 (*Kidney International* (2024) 105(Suppl 4S), S117–S314):

> CKD is classified based on Cause, Glomerular filtration rate (GFR)
> category (G1–G5), and Albuminuria category (A1–A3), abbreviated as
> CGA.

GFR categories (mL/min/1.73 m²), verbatim from the table:

| Category | Range | Description |
|---|---|---|
| G1 | ≥90 | Normal or high |
| G2 | 60–89 | Mildly decreased |
| G3a | 45–59 | Mildly to moderately decreased |
| G3b | 30–44 | Moderately to severely decreased |
| G4 | 15–29 | Severely decreased |
| G5 | <15 | Kidney failure |

This confirms the scoping document's stated boundaries exactly (G1 ≥90,
G2 60–89, G3a 45–59, G3b 30–44, G4 15–29, G5 <15) — no correction needed
to the numbers themselves.

## Extends: the boundary-inclusivity question has a real answer, and it isn't the one first assumed

The scoping document's own open question was whether these are simple
half-open continuous intervals (e.g. "is 89.5 in G1 or G2?"). The source
resolves this differently than assumed: **eGFR is not staged as a raw
continuous value at all.** Table 11 ("Implementation standards to ensure
accuracy and reliability of GFR assessments using creatinine and cystatin
C"), same document:

> Report eGFR rounded to the nearest whole number and relative to a body
> surface area (BSA) of 1.73 m² in adults using the units ml/min per 1.73
> m². Reported eGFR levels <60 ml/min per 1.73 m² should be flagged as
> being low.

**This is the actual resolution, and it is more precise than "G2 spans
[60, 90)":** eGFR is rounded to the nearest whole number *before*
staging. A continuous computed value doesn't compare directly against
90/60/45/30/15 — it's rounded first, and the *rounded integer* is
compared against the published integer boundaries. Consequence for a
formal model that takes continuous `real` input (the natural Dafny
convention, matching `dosage.dfy`'s own parameters): the effective
continuous G1/G2 boundary is at **89.5**, not 90.0 (round-half-up:
89.5 → 90 → G1; 89.499... → 89 → G2), not the naive "eGFR >= 90.0"
comparison the scoping document's Gate 1b sketch implicitly assumed. The
same half-integer-shift applies at every other boundary (59.5 for
G2/G3a, 44.5 for G3a/G3b, 29.5 for G3b/G4, 14.5 for G4/G5). **This is a
named design decision for Gate 1b, not yet resolved by this source
alone:** does `renal_adjustment.dfy` (a) accept a real-valued eGFR and
apply the rounding step explicitly as its own proven operation before
staging (recommended — it's the more faithful, more provable model, and
it's exactly the kind of boundary-precision question Gate C4's STPs
exist to pin down), or (b) accept an already-rounded integer eGFR as a
precondition and push the rounding step outside the spec's scope
entirely? Not decided here; flagged for Gate 1b.

## Confirms and partially resolves: `REQ-RENAL-3`'s citation gap

The scoping document's `REQ-RENAL-3` ("Cockcroft-Gault reliability
override: unstable renal function / very obese / oedematous → flag")
was attributed to the MHRA Drug Safety Update, but a direct fetch of that
page did not corroborate the obesity/oedema caveat. This source
partially resolves it — from the discussion of Cockcroft-Gault's known
limitations (unpaginated in the extracted text but immediately following
the Table 11 implementation-standards discussion, same section):

> Although the Cockcroft-Gault formula for estimating CrCl has been used
> in many past pharmacokinetic studies that serve as the basis for the
> drug dosing, there are multiple concerns with that equation. It was
> developed in an era when the need for standardization of creatinine
> measurements was not appreciated, women and individuals of Black race
> were not included, and there are concerns about use of weight, which
> can be impacted by edema or obesity.

This corroborates the **obesity/oedema** part of `REQ-RENAL-3` directly
(Cockcroft-Gault is weight-based, and weight is an unreliable proxy for
lean body mass when distorted by fluid retention or adiposity) — cite
KDIGO 2024 for that half of the requirement, not MHRA. **The "unstable
renal function" half of `REQ-RENAL-3` is still not corroborated by any
source fetched so far** (MHRA's actual stated caveat is about *rapidly
changing* renal function specifically — AKI reassessment — which is
already `REQ-RENAL-6`, not a general "unstable" flag distinct from that).
Recommend either merging that half of `REQ-RENAL-3` into `REQ-RENAL-6`
(same underlying concern: creatinine-based formulas assume steady state)
or dropping it as a separately-sourced claim if no other citation
surfaces — named here rather than left unresolved silently.

## New finding, not in the original scoping document: Practice Point 4.2.4 (p. S164)

> Practice Point 4.2.4: In people with extremes of body weight, eGFR
> nonindexed for body surface area (BSA) may be indicated, especially
> for medications with a narrow therapeutic range or requiring a minimum
> concentration to be effective. For assessment of CKD, it is relevant
> to compare the GFR according to a standard body size. For this reason,
> GFR estimating equations have been developed in units of ml/min per
> 1.73 m². However, because drug clearance is more strongly associated
> with nonindexed eGFR (ml/min) than indexed eGFR (ml/min per 1.73 m²),
> in very small or large individuals, this can result in over- or
> under-dosing.

This is a genuine, previously-unnamed requirement: for narrow-
therapeutic-index drugs specifically (already one of the five MHRA
formula-selection conditions), even the eGFR branch may need a BSA
de-normalization step before use in dose adjustment, not just a raw
"use eGFR" decision. Proposed as `REQ-RENAL-7` (de-normalization for
narrow-therapeutic-index drugs when eGFR is selected) — a real extension
to the requirements table, not inferred, cited directly to this practice
point.

## Not yet resolved by this source

- The "unstable renal function" half of `REQ-RENAL-3` (see above).
- Whether Gate 1b should implement the rounding-then-stage model or take
  pre-rounded input (see above) — a design decision, not a sourcing gap.
