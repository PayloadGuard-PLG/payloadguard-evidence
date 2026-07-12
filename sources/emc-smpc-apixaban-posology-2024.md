# eMC SmPC — Apixaban (Eliquis) posology, both strengths

**Source:** electronic Medicines Compendium (eMC), Summary of Product
Characteristics for Eliquis, Bristol-Myers Squibb / Pfizer.
Two product listings, same active substance, covering different
strength/indication splits:

- **Eliquis 5 mg film-coated tablets** (PLGB 54213/0002), product 2878.
  Date of revision of the text: 04 January 2024; eMC upload date 08
  January 2024. <https://www.medicines.org.uk/emc/product/2878/smpc>
- **Eliquis 2.5 mg film-coated tablets**, product 4756.
  <https://www.medicines.org.uk/emc/product/4756/smpc>

Fetched directly 2026-07-12 (WebFetch against both product pages,
verbatim extraction requested, not a summarized pass) — following this
repo's standing rule (`HANDOFF.md`) to verify externally-supplied claims
against the primary source before treating them as citable, after this
session reviewed an external research document ("Scoping REQ-DDI-5/6")
making claims about both SmPCs. Every load-bearing quote below was
independently confirmed against the fetched text via
`evidence/citation_gate.py` before being recorded here — see
`DEVLOG.md`'s 2026-07-12 entry for the full verification trace,
including a deliberate false-control claim ("decrease the dose of
apixaban by 50%") that correctly returned `NOT_FOUND`.

## Why two product pages

The 5 mg SmPC's own indications list (§4.1) covers NVAF and DVT/PE
treatment/recurrence-prevention only; it does not carry the
post-surgical VTE prophylaxis (VTEp) indication or its 2.5 mg regimen —
that indication and dose live entirely on the 2.5 mg product's own SmPC.
A complete posology picture for apixaban therefore requires reading
both pages, not one.

## Verbatim extracts

**1. NVAF standard dose reduction ("2-of-3" rule) — identical text on
both SmPCs, §4.2, subheading "Dose reduction":**

> "The recommended dose of apixaban is 2.5 mg taken orally twice daily
> in patients with NVAF and at least two of the following
> characteristics: age ≥ 80 years, body weight ≤ 60 kg, or serum
> creatinine ≥ 1.5 mg/dL (133 micromole/L)."

Confirmed present, word-for-word, on **both** the 5 mg and the 2.5 mg
product pages.

**2. The rule is NVAF-only.** On the 5 mg SmPC, "Dose reduction"
appears as a subheading directly under "Prevention of stroke and
systemic embolism in patients with non-valvular atrial fibrillation
(NVAF)"; the separate "Treatment of DVT, treatment of PE and prevention
of recurrent DVT and PE (VTEt)" heading carries its own dosing (10 mg
BID for 7 days, then 5 mg BID; see below) with no mention of the
age/weight/creatinine criteria.

**3. VTE prophylaxis (hip/knee replacement) — 2.5 mg SmPC only, §4.1
and §4.2:**

> §4.1: "Prevention of venous thromboembolic events (VTE) in adult
> patients who have undergone elective hip or knee replacement
> surgery."
>
> §4.2: "The recommended dose of apixaban is 2.5 mg taken orally twice
> daily." / "The initial dose should be taken 12 to 24 hours after
> surgery." / Hip surgery: "The recommended duration of treatment is 32
> to 38 days." / Knee surgery: "The recommended duration of treatment
> is 10 to 14 days."

**4. Interaction dosing is qualitative on the SmPC too — no numeric
figure, §4.2 / §4.5:**

> "The use of apixaban is not recommended in patients receiving
> concomitant systemic treatment with strong inhibitors of both CYP3A4
> and P-gp, such as azole-antimycotics (e.g., ketoconazole,
> itraconazole, voriconazole and posaconazole) and HIV protease
> inhibitors (e.g., ritonavir)."

No percentage or milligram adjustment is stated for any apixaban
drug-drug interaction anywhere on either SmPC — "not recommended" is
the strongest and only instruction given. This independently corroborates
`sources/sps-doac-interactions-2024.md`'s own finding that apixaban
carries no numeric interaction-based dose adjustment in UK sources,
from a second, independent primary source (the legal SmPC itself, not
just SPS's derived guidance page).

## What this confirms, corrects, or extends

**Confirms**, against a second independent primary source, three claims
already established via `sources/sps-doac-interactions-2024.md`:
apixaban's drug-interaction guidance is qualitative-only in UK sources
(no numeric target exists to source, for any interaction); the
rifampicin/carbamazepine indication-dependent branching pattern that
motivates `REQ-DDI-5` reflects real, sourced clinical structure, not an
invented modeling axis. **Extends** the existing requirements table
(`PHASE1_PLAN.md`) with new, citable ground for a possible future
posology axis this example does not currently model at all: the NVAF
"2-of-3" numeric dose-reduction rule and the VTE-prophylaxis regimen are
both real, dated, versioned, machine-transcribable rules — distinct from
`REQ-DDI-6` (which concerns *interaction*-triggered numeric targets, not
these baseline-posology ones). Not yet reflected in any requirement row;
recorded here as verified source material for whenever that scoping
decision is made, per this repo's standing discipline of citing before
building rather than after.

## What this does not resolve

Does not resolve — and does not attempt to resolve — REQ-DDI-6's
interaction-numeric gap for apixaban specifically: no UK source,
including this one, states a percentage or milligram adjustment for any
apixaban drug-drug interaction. See
`sources/fda-eliquis-label-interactions-2016.md` for the contrasting US
FDA position and the jurisdictional-divergence note that follows from
it.
