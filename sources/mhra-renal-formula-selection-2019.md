# MHRA Drug Safety Update, vol. 13, issue 3 (Oct 2019) — formula-selection rule and BMI boundary

**Source:** "Prescribing medicines in renal impairment: using the appropriate
estimate of renal function to avoid the risk of adverse drug reactions,"
MHRA Drug Safety Update, vol. 13, issue 3 (October 2019).
https://www.gov.uk/drug-safety-update/prescribing-medicines-in-renal-impairment-using-the-appropriate-estimate-of-renal-function-to-avoid-the-risk-of-adverse-drug-reactions
— fetched directly and verified 2026-07-08 (WebFetch).

Per `sources/README.md` rule 2 — what this **confirms, corrects, or
extends**:

## Confirms: the five formula-selection conditions (REQ-RENAL-2)

Direct fetch confirms MHRA states Cockcroft-Gault CrCl should be used
instead of eGFR for: direct-acting oral anticoagulants; patients on
nephrotoxic drugs; patients aged 75 and older; patients at extremes of
muscle mass; medicines that are renally excreted with a narrow
therapeutic index. Matches the original scoping document's `REQ-RENAL-2`
exactly.

## Confirms and upgrades: the BMI boundary for "extremes of muscle mass" is stated in MHRA itself, not just a secondary source

A draft revision of this Phase 1 work (uploaded 2026-07-08, "research
findings") proposed citing NHS Tayside ADTC's *Tayside Prescriber* No.
157 (Jan 2020) as the source for a specific numeric BMI threshold, with
two ClinicalTrials.gov PK studies (NCT02942810, NCT02039817) as
independent corroboration. Verified directly against the primary MHRA
page itself (not just Tayside's restatement of it) — the MHRA source
gives the literal number:

> patients at extremes of muscle mass (BMI <18 kg/m2 or >40 kg/m2)

Strict inequality confirmed directly (`<18`, `>40` — exactly 18.0 or
40.0 is not itself "extreme"). This **upgrades** the citation: MHRA
itself is the primary source for this number, not Tayside — Tayside's
*Tayside Prescriber* No. 157 (verified separately, PDF fetched and read
directly, same verbatim wording, footnoted to "Drug Safety Update vol
13, issue 3: October 2019: 3") is a faithful secondary restatement of
the same MHRA text, not an independent source. Cite MHRA directly for
`REQ-RENAL-2`'s BMI boundary; Tayside may be kept as a corroborating
secondary reference.

**The two ClinicalTrials.gov citations are weaker than the draft
implied — corroborating, not confirming.** Verified directly
(`get_trial_details`): NCT02942810 and NCT02039817 are both real,
completed Phase 1 PK studies in renal impairment, and both do use "BMI
18.0–40.0 kg/m²" as a general subject-eligibility inclusion range. But
that is standard PK-study eligibility screening (keeping body
composition typical across the whole cohort, healthy volunteers
included), not a citation of MHRA's specific "extremes of muscle mass"
formula-selection rule — the trials were not designed to validate that
threshold. They are consistent with strict inequality at 18.0/40.0
being the "normal" boundary, but should not be cited as if they
independently establish MHRA's number; MHRA's own text already does
that directly and needs no secondary corroboration.

## Confirms: no independent source found for a general "unstable renal function" flag distinct from AKI reassessment

Consistent with the finding already recorded in
`sources/kdigo-2024-gfr-staging.md`: this page's actual stated caveat is
about reassessment under rapidly changing renal function (AKI), not a
separate, general "unstable renal function" override. No correction to
that earlier finding.

## Not covered by this source

Per-drug numeric dose-reduction factors (explicit Phase 1 non-goal, see
`examples/renal_adjustment/PHASE1_PLAN.md`); the classification-flag
provenance question (who sets `isDirectActingOralAnticoagulant` etc. and
by what process) — MHRA's drug lists are illustrative ("such as
vancomycin and amphotericin B"), not closed, which is itself part of why
that flag-ownership question was scoped as caller-supplied rather than
spec-owned.
