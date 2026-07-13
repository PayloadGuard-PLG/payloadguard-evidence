# eMC SmPC — Dabigatran (Pradaxa) therapeutic indications and dosing regimens

**Source:** electronic Medicines Compendium (eMC), Summary of Product
Characteristics for Pradaxa, Boehringer Ingelheim. Two product listings
fetched, both relevant to the indication-scope question this document
was fetched to resolve:

- **Pradaxa 110 mg hard capsules** (product 6229). Date of revision:
  16 January 2025. <https://www.medicines.org.uk/emc/product/6229/smpc>
- **Pradaxa 150 mg hard capsules** (product 4703), fetched for §4.1
  comparison only — see "Why two product pages" below.
  <https://www.medicines.org.uk/emc/product/4703/smpc>

Fetched directly 2026-07-13 (WebFetch against both product pages,
verbatim extraction requested, cross-checked between the two pages) —
prompted by a Gate C6 review finding on
`nl_confirmation_drug_interaction_checker_dfy.md` (see that document's
"Addendum 3" and `DEVLOG.md`'s 2026-07-13 entry) that questioned whether
`TreatmentIndication`'s two constructors (`AFStrokePrevention`,
`RecurrentVTEPrevention`) cover dabigatran's real licensed indication
set, per this repo's standing rule to verify externally-supplied claims
against a primary source before treating them as citable.

## Why two product pages

The 150 mg capsule's §4.1 lists only two indication categories:
"Prevention of stroke and systemic embolism in adult patients with
non-valvular atrial fibrillation (NVAF)..." and "Treatment of deep vein
thrombosis (DVT) and pulmonary embolism (PE), and prevention of
recurrent DVT and PE in adults" (plus a paediatric VTE-treatment line,
out of scope for this example). It does **not** carry the
post-orthopaedic-surgery VTE-prophylaxis indication at all. The 110 mg
capsule's §4.1 carries all three — confirming the orthopaedic-VTE-
prophylaxis indication is real, current (revision date January 2025,
not historical/withdrawn), and specifically associated with the lower
strength product, the same strength REQ-DDI-6's verapamil interaction
rule reduces *to* (110mg twice daily).

## §4.1 Therapeutic indications, verbatim (Pradaxa 110 mg, product 6229)

> "Primary prevention of venous thromboembolic events (VTE) in adult
> patients who have undergone elective total hip replacement surgery or
> total knee replacement surgery.
>
> Prevention of stroke and systemic embolism in adult patients with
> non-valvular atrial fibrillation (NVAF), with one or more risk
> factors, such as prior stroke or transient ischemic attack (TIA); age
> ≥ 75 years; heart failure (NYHA Class ≥ II); diabetes mellitus;
> hypertension.
>
> Treatment of deep vein thrombosis (DVT) and pulmonary embolism (PE),
> and prevention of recurrent DVT and PE in adults
>
> Treatment of VTE and prevention of recurrent VTE in paediatric
> patients from the time the child is able to swallow soft food to less
> than 18 years of age."

**Three adult indication categories, not two** (the paediatric line is
out of scope for this example, which only ever modeled adult dosing):

1. Primary prevention of VTE after elective hip/knee replacement surgery
   (orthopaedic prophylaxis) — **once-daily** regimen.
2. Prevention of stroke/systemic embolism in NVAF — **twice-daily**
   regimen.
3. Treatment of DVT/PE and prevention of recurrent DVT/PE — **twice-daily**
   regimen.

## §4.2 Dosing regimens, verbatim extracts

**Orthopaedic VTE prophylaxis** (once daily): "single capsule of 110 mg
dabigatran etexilate" given 1-4 hours post-surgery, followed by "220 mg
dabigatran etexilate once daily taken as 2 capsules of 110 mg" for 10
days (knee) or 28-35 days (hip). Dose-reduced patients (age >75,
moderate renal impairment, or concomitant amiodarone/quinidine/
verapamil/ketoconazole) receive "75 mg" initial dose and "150 mg
dabigatran etexilate once daily taken as 2 capsules of 75 mg."

**NVAF stroke prevention** (twice daily): standard dose "300 mg
dabigatran etexilate taken as one 150 mg capsule twice daily." **"Dose
reductions are recommended for patients who receive concomitantly
verapamil"** with "dabigatran etexilate and verapamil should be taken
at the same time" — reduced dose "220 mg dabigatran etexilate taken as
one 110 mg capsule twice daily" (the same instruction given for age ≥80
years).

**DVT/PE treatment and recurrence prevention** (twice daily): standard
dose "300 mg dabigatran etexilate taken as one 150 mg capsule twice
daily following treatment with a parenteral anticoagulant for at least
5 days." Verapamil dose-reduction guidance stated as identical to the
NVAF indication above — same instruction, not repeated verbatim in this
section.

**The verapamil dose-reduction instruction is given only under the two
twice-daily indications (NVAF, DVT/PE) — it is not mentioned anywhere
in the orthopaedic-VTE-prophylaxis dosing section, which uses a
structurally different once-daily regimen (220mg OD standard / 150mg OD
reduced, for reasons unrelated to drug interactions: age, renal
function, and a *different* dose-reduction trigger list that happens to
also include verapamil, but as an *initial-dose* selection criterion,
not a same-regimen dose reduction).**

## What this confirms, corrects, or extends

**Confirms** `sources/sps-doac-interactions-2024.md`'s own stated scope
for the verapamil row: the 110mg-twice-daily dose-reduction instruction
really is tied specifically to the NVAF and DVT/PE (both twice-daily)
indications, verified independently against the legal SmPC itself, not
just SPS's derived guidance page. **Also confirms** that SPS's two
partial phrasings — the rifampicin row's "prevention of recurrent deep
vein thrombosis (DVT) and pulmonary embolism (PE)" and the verapamil
row's "DVT/PE-prevention-and-treatment" — both refer to the *same*
single eMC-licensed indication category ("Treatment of DVT/PE, and
prevention of recurrent DVT/PE," one indication line in the real SmPC,
not two), which is what `drug_interaction_checker.dfy`'s
`RecurrentVTEPrevention` constructor already models. No third
constructor is needed to resolve *this* specific naming concern.

**Corrects/extends** a real gap the Gate C6 review flagged and this
document confirms is genuine: dabigatran has a **third, current, UK-
licensed indication** (orthopaedic VTE prophylaxis, once-daily regimen)
that `TreatmentIndication`'s two constructors do not represent at all,
and that `sources/sps-doac-interactions-2024.md`'s verapamil row is
silent on — it names only the two twice-daily indications, never
mentioning orthopaedic prophylaxis at all, positively or negatively.
This is structurally the same shape as `(Apixaban, Dronedarone)`'s
already-modeled source silence (`NotCovered`), not a case this repo's
existing categories can currently express for `DoseReductionTargetMg`
(which has no `NotCovered`-equivalent — see the Gate C6 review's own
Fix 2A/2B proposals and open decisions for the design question this
raises).

## What this does not resolve

Does not resolve, by itself, whether `TreatmentIndication` should gain
a third constructor, or what `DoseReductionTargetMg`'s signature should
look like if it does — those are real design decisions (Gate C6
review's "Open decisions," items 2 and 3), not settled by sourcing
alone. Also does not check whether apixaban's own already-decided
two-constructor scope (REQ-DDI-5, confirmed via `AskUserQuestion` in an
earlier session, on the grounds that the orthopaedic-prophylaxis
indication belongs only to a different, posology source with no stated
interaction outcome) needs revisiting in light of this — apixaban's own
orthopaedic-VTE-prophylaxis indication was already known and explicitly
scoped out at that time; this document does not re-litigate that
decision, only dabigatran's.
