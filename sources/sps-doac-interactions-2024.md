# NHS SPS — Managing interactions with direct oral anticoagulants (DOACs)

**Source:** NHS Specialist Pharmacy Service (SPS), "Managing interactions
with direct oral anticoagulants (DOACs)." Published 5 January 2024, last
updated 20 June 2025 (per-section update history on the page itself
notes the diltiazem section specifically as the 20 June 2025 change).
<https://www.sps.nhs.uk/articles/managing-interactions-with-direct-oral-anticoagulants-doacs/>

Fetched directly (raw HTML, not an AI-summarized pass) 2026-07-10 —
`curl` to `sps_doac.html`, stripped to plain text, cross-checked against
an earlier WebFetch summarization pass. The summarization pass was
directionally accurate but flattened real structure (see "What the
summary missed," below); this document is built from the raw text,
following this repo's own standing rule (`HANDOFF.md`) to verify
externally-supplied claims empirically rather than trust a summary,
after two real fabricated/misattributed citations were caught by hand
elsewhere in this session's work (MHRA/KDIGO, NICE NG203).

**Backing sources the page itself cites:** Summary of Product
Characteristics (SmPC) for dabigatran and the other DOACs; NICE CKS on
NSAID prescribing issues (for the NSAID section specifically).

**Scope statement, verbatim:** "The SPS interactions advice has been
developed from published evidence, literature reviews and expert
opinion, where needed. It includes commonly asked questions on medicine
interactions and is not comprehensive for all potential interactions
with DOACs." — this is the citable basis for treating an unlisted
drug/agent as `NotCovered`, distinct from an explicit `NoInteractionExpected`
finding (digoxin gets the latter; most drugs never mentioned on the page
get neither, i.e. the former).

## Per-entry extraction (verbatim quotes, condensed to interaction +
management text; mechanism-only "Further information" sentences omitted
except where they explain a per-DOAC split)

**Amiodarone** — "Amiodarone may increase the blood levels of DOACs,
increasing their anticoagulant effect." / "Use concomitantly with
caution. Monitor for anaemia and signs of bleeding." Uniform across all
four DOACs; no dose figure.

**Digoxin** — "No interactions are expected between digoxin and DOACs."
Uniform, explicit negative, no dose figure.

**Diltiazem** — "Diltiazem may increase the blood levels of DOACs,
increasing their anticoagulant effect." / "Monitor for anaemia and signs
of bleeding." Uniform; most recently updated section (20 June 2025); no
dose figure.

**Dronedarone** — "may increase the blood levels of DOACs... increase
their anticoagulant effect." Management: "Monitor for anaemia and signs
of bleeding." **For dabigatran and rivaroxaban: "Avoid concomitant
use."** **For edoxaban: "Reduce the dose of edoxaban to 30mg once
daily."** **Apixaban is never mentioned in this section at all** — a
real gap in the source, not an omission on this document's part;
recorded as `NotCovered` for (apixaban, dronedarone), not assumed safe.

**Verapamil** — "may increase the blood levels of DOACs... This is
unlikely to be clinically relevant interaction for rivaroxaban and
apixaban." Management: "Monitor for anaemia and signs of bleeding." **For
dabigatran: "Reduce the dose of dabigatran to 110mg twice daily"** for
AF-stroke-prevention and DVT/PE-prevention-and-treatment indications
specifically (the only indication-scoping on this row; both named
indications get the same dose, so this doesn't need an indication axis
to model correctly — the dose reduction just applies whenever dabigatran
is used for either).

**Macrolides** — "Macrolides such as clarithromycin and erythromycin
(systemic) may increase the blood levels of DOACs..." — the class is
named but only two specific drugs are given: clarithromycin, erythromycin
(systemic route specified; topical/non-systemic forms are out of scope
by the source's own wording). Management: "Use concomitantly with
caution. Monitor for anaemia and signs of bleeding, particularly in the
elderly or in people with renal impairment." **For edoxaban specifically
with erythromycin (systemic): "Reduce the edoxaban dose to 30mg daily."**
No dose adjustment stated for clarithromycin with any DOAC.

**Rifampicin** — "decreases the blood levels of DOACs and reduces their
anticoagulant effect." Management: "Prescribe a different anticoagulant
for which monitoring is available e.g. warfarin or consider an
alternative medicine." **Apixaban: "use apixaban with caution" — but
only "for the following indications: prevention of stroke and systemic
embolism in people with non-valvular atrial fibrillation; prevention of
recurrent deep vein thrombosis (DVT) and pulmonary embolism (PE)"** — an
explicit indication-dependent branch, the only one of its kind alongside
the carbamazepine/phenytoin/phenobarbital row below. **Dabigatran:
"Avoid concomitant use."** **Edoxaban and rivaroxaban: "monitor for
signs of thrombosis" if concomitant use cannot be avoided.**

**Other DOACs, heparin and warfarin** — "Concomitant use of DOACs with
other DOACs, heparin or warfarin may increase bleeding risk." Management:
"Avoid concomitant use unless switching to or from warfarin treatment or
under specialist supervision." Uniform across all four DOACs; the
switching/specialist-supervision exception is itself a caller-supplied
condition, not a separate outcome kind.

**SSRIs and SNRIs** — "may increase the bleeding risk associated with
DOACs." Management: "Use concomitantly with caution or avoid... Monitor
for anaemia and bleeding." **For dabigatran specifically: "consider a
dose reduction (as per the Summary of Product Characteristics) if the
individual also has other risk factors for bleeding"** — conditional on
a caller-supplied risk-factor flag, not an indication; no specific mg
figure given (defers to the SmPC itself for the number).

**Fluconazole** — "may increase the blood levels of apixaban, dabigatran
and rivaroxaban and increase their anticoagulant effect. This is not
considered to be clinically relevant for rivaroxaban." **"No interaction
is expected with edoxaban."** Management (for apixaban/dabigatran):
"Monitor for anaemia and signs of bleeding, particularly in renal
impairment." Three distinct per-DOAC outcomes on one row: apixaban/
dabigatran = caution, rivaroxaban = theoretical-only (explicitly
downgraded), edoxaban = explicit no-interaction.

**Itraconazole and ketoconazole** — "contraindicated with dabigatran";
"not recommended with apixaban or rivaroxaban." Management: "If
concomitant use with apixaban, edoxaban and rivaroxaban cannot be
avoided, monitor for anaemia and signs of bleeding" (edoxaban is grouped
into this monitoring clause without its own top-level "not recommended"
label, but is not treated as safer than apixaban/rivaroxaban either).
**For edoxaban specifically with ketoconazole: "Reduce the edoxaban dose
to 30mg daily"** — itraconazole gets no analogous dose figure for
edoxaban.

**Antiplatelets** — "Antiplatelet medicines such as aspirin, clopidogrel
and ticagrelor may increase the bleeding risk associated with DOACs.
Ticagrelor has also been shown to increase the blood levels of
dabigatran" (a distinct, second mechanism beyond the class-wide bleeding-
risk-additive one). Management: "Avoid concomitant use unless advised by
a specialist. If concomitant use is indicated, consider appropriate
gastroprotection. Monitor for anaemia and bleeding." Uniform outcome
across all four DOACs; three named example drugs, not an exhaustive list
(the source says "such as").

**Carbamazepine, phenytoin and phenobarbital** — "may decrease the blood
levels of DOACs, reducing their anticoagulant effect." Same
indication-dependent structure as rifampicin: **apixaban — "use apixaban
with caution" only for the same two named indications** (AF-stroke-
prevention; DVT/PE-recurrence-prevention). **Dabigatran: "Avoid
concomitant use"** — with a documented evidence-quality caveat: "Although
the [SmPC] for dabigatran does not document an interaction between
phenobarbital and dabigatran, it is still predicted." **Edoxaban and
rivaroxaban: "monitor for signs of thrombosis"** if concomitant use
cannot be avoided.

**Levetiracetam and valproate-containing medicines** — "may decrease the
blood levels of DOACs, reducing their anticoagulant effect. Although,
evidence is lacking and the mechanism of this interaction is unknown."
Management: "Use concomitantly with caution and be aware of the
interaction in the case of an unexpected response to treatment." Uniform
across all four DOACs; explicitly flagged by the source itself as
theoretical/low-evidence-quality; no dose figure.

**Ciclosporin** — "is contraindicated with dabigatran. It may increase
the blood levels of the other DOACs, increasing their anticoagulant
effect." Management (apixaban/edoxaban/rivaroxaban): "Consult with the
specialist and use... cautiously... Monitor for anaemia and signs of
bleeding." **For edoxaban specifically: "Reduce the edoxaban dose to
30mg daily with ciclosporin."**

**Tacrolimus** — "may increase the blood levels of dabigatran,
increasing its anticoagulant effect. An interaction to a lesser extent is
expected with the other DOACs." **Dabigatran: "Avoid concomitant use of
dabigatran with tacrolimus"** — note this is worded "avoid," not
"contraindicated" (the word ciclosporin's dabigatran entry uses); kept
distinct in the requirements table below rather than treated as a
synonym. Others: "Consult with specialist and use... cautiously...
Monitor for anaemia and signs of bleeding, particularly in those who are
elderly or have renal impairment." No dose figure for any DOAC.

**NSAIDs** — "NSAIDs such as ibuprofen and naproxen may increase the
bleeding risk associated with DOACs." Management: "Use concomitantly
with caution or avoid if possible. Review the need for the NSAID and
avoid chronic use... prescribe the lowest effective dose for the
shortest possible duration... consider appropriate gastroprotection."
Cites NICE CKS on NSAID prescribing issues. Uniform across all four
DOACs; two named example drugs, not exhaustive ("such as").

## What the summary missed

An earlier WebFetch pass (AI-summarized, not the raw text above)
reported the substance of every row correctly but lost: verapamil's and
fluconazole's per-DOAC downgrades ("unlikely to be clinically relevant"
/ "not considered clinically relevant"); the two indication-dependent
apixaban branches (rifampicin, carbamazepine/phenytoin/phenobarbital);
the dabigatran+SSRI dose reduction's dependency on a patient risk-factor
flag rather than being unconditional; the specific named macrolides
(clarithromycin, erythromycin) behind the class label; and the
apixaban+dronedarone gap (silence, not a stated "no interaction"). None
of these are fabrications — they're the kind of precision loss a
summarization pass predictably introduces, which is exactly why this
document exists as a raw-text extraction rather than relying on the
summary alone.

## Feeds

`examples/drug_interaction_checker/PHASE1_PLAN.md`'s Gate 1a requirements
table (`REQ-DDI-*`).
