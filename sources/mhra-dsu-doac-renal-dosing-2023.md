# MHRA Drug Safety Update — DOAC renal-impairment dosing table (May 2023)

**Source:** MHRA, "Direct-acting oral anticoagulants (DOACs): paediatric
formulations; reminder of dose adjustments in patients with renal
impairment," Drug Safety Update volume 16, issue 10, May 2023.
<https://www.gov.uk/drug-safety-update/direct-acting-oral-anticoagulants-doacs-paediatric-formulations-reminder-of-dose-adjustments-in-patients-with-renal-impairment>

Fetched directly 2026-07-12 (WebFetch, verbatim extraction requested,
not a summarized pass) — following this repo's standing rule
(`HANDOFF.md`) to verify externally-supplied claims against the primary
source, after reviewing an external research document making claims
about this table's indication-dependent structure.

## Verbatim extracts

**1. Confirms this update carries forward, rather than replaces, an
earlier position:**

> "Recommendations for use of DOACs in patients with renal impairment
> were published in the June 2020 issue of Drug Safety Update."

**2. Apixaban dosing by renal severity band, Table 1 (per-cell
extraction):**

| Renal function (CrCl) | Apixaban recommendation |
|---|---|
| Mild (50–80 mL/min) | "No dose adjustment required" |
| Moderate (30–49 mL/min) | "Dose reduction is required in SPAF in some patients*" |
| Severe (15–29 mL/min) | "To be used with caution in VTEp and VTEt; dose reduction is recommended in SPAF" |
| End stage (<15 mL/min) / dialysis | "Not recommended" |

(SPAF = stroke prevention in atrial fibrillation, i.e. NVAF; VTEp = VTE
prophylaxis; VTEt = VTE treatment. The asterisk on the "Moderate" row
ties back to the same age/weight/serum-creatinine criteria as the
SmPC's NVAF "2-of-3" rule — see
`sources/emc-smpc-apixaban-posology-2024.md`.)

**3. Indication-dependent branching, confirmed directly in the table
structure.** At the same renal-severity level (severe, CrCl 15–29),
apixaban receives a materially different recommendation for
SPAF/NVAF ("dose reduction is recommended," i.e. the numeric 2.5 mg
rule) than for VTEp/VTEt ("to be used with caution," a qualitative
instruction with no numeric change stated). This is the same
indication-conditional structure `REQ-DDI-5`'s scoping already
identified for interaction handling (rifampicin/carbamazepine
branching by indication) — here confirmed as a general pattern in
apixaban's UK dosing guidance, not specific to drug interactions.

## What this confirms, corrects, or extends

**Confirms**, from a third independent primary source (after the SPS
interactions page and both eMC SmPCs), that apixaban's UK dosing
guidance is genuinely indication-branched, not uniformly applied
regardless of indication — corroborating the structural premise behind
`REQ-DDI-5`. **Extends** `sources/emc-smpc-apixaban-posology-2024.md`
with the renal-severity axis specifically, presented here as an
indication × severity matrix rather than prose, which is the shape a
future formal specification would need if this axis were ever modeled.
Does not by itself resolve anything about drug-drug interaction dosing
(`REQ-DDI-6`) — renal impairment and drug interaction are two distinct
dose-modifying axes in the source material, not the same question.

## What this does not resolve

Renal function is not currently a modeled input anywhere in
`examples/drug_interaction_checker/` (`CheckInteraction` takes `doac`,
`agent`, and `hasOtherBleedingRiskFactors` only) — recorded here as
verified source material for a possible future scoping decision, not as
grounds for a new requirement row. No requirement currently cites this
document.
