# US FDA ELIQUIS label — §7.1 drug-interaction dosing (contrast source, non-UK)

**Source:** US Food and Drug Administration, ELIQUIS (apixaban) tablets
prescribing information, §7.1 "Combined P-gp and Strong CYP3A4
Inhibitors." Accessed via DailyMed (National Library of Medicine),
label set ID `a454cd24-0c6d-46e8-b1e4-197388606175`.
<https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=a454cd24-0c6d-46e8-b1e4-197388606175>
Cross-referenced against the FDA's own hosted copy:
<https://www.accessdata.fda.gov/drugsatfda_docs/label/2016/202155s012lbl.pdf>

Fetched directly 2026-07-12 (WebFetch/WebSearch, verbatim extraction
requested). Confirmed via `evidence/citation_gate.py` against the
fetched text — see `DEVLOG.md`'s 2026-07-12 entry.

**Scope flag, stated explicitly and deliberately: this is a US FDA
regulatory document, not a UK/MHRA one.** Every other source in this
folder for the apixaban/DOAC material is UK-jurisdiction (SPS, eMC
SmPC, MHRA DSU), matching `examples/drug_interaction_checker/`'s
established sourcing convention (NHS SPS, UK-jurisdiction, consistent
with `renal_adjustment`'s own MHRA/KDIGO/NICE sourcing). This document
is recorded here only to support an explicit, citable statement of
where UK and US guidance diverge — never as a substitute UK source, and
never as grounds to import a US-specific numeric rule into a
UK-scoped specification without an explicit jurisdiction annotation.

## Verbatim extracts

> "For patients receiving ELIQUIS 5 mg or 10 mg twice daily, the dose
> of ELIQUIS should be decreased by 50% when coadministered with drugs
> that are combined P-gp and strong CYP3A4 inhibitors."
>
> "For patients receiving ELIQUIS at a dose of 2.5 mg twice daily,
> avoid coadministration with combined P-gp and strong CYP3A4
> inhibitors."

## What this confirms, corrects, or extends

**Confirms** the specific divergence an external research document
("Scoping REQ-DDI-5/6") identified: the US label states an explicit
numeric (50%) interaction-based dose reduction for apixaban, where
every UK source checked in this folder
(`sources/sps-doac-interactions-2024.md`,
`sources/emc-smpc-apixaban-posology-2024.md`) gives only qualitative
language ("not recommended") for the equivalent interaction. This is a
genuine jurisdictional divergence, not a gap in UK source coverage —
the UK regulator's position is "not recommended" (avoid the
combination), not "an unstated number."

## What this does not resolve

Does not establish a citable UK numeric target for apixaban drug
interactions — it establishes the opposite: that no such target exists
in the jurisdiction this example is scoped to. No requirement currently
cites this document. If a future `REQ-DDI-6` extension were ever to
state a numeric apixaban interaction dose, it could only do so by
citing this US source explicitly and flagging the jurisdictional
departure from every other requirement in this example — not by
presenting it as UK guidance.
