# ALARP determination — `HAZ-GIP-1.14b`

**Document ID:** ALARP-DOSE-001
Part of the risk management file per ISO 14971:2019 clause 4.5 — this
is the risk *acceptability policy application* content (clause 4.4e,
Section 5's "Method for evaluating overall residual risk," Path 2).
Guidance basis, verified 2026-07-21 against the primary text
(`sources/CEN-ISO-TR-24971-2020-E.docx`): ISO/TR 24971:2020 Annex C.2
("Policy for establishing criteria for risk acceptability") and Annex
C.3 ("Criteria for risk acceptability").

**Terminology note — "ALARP" is this document's label, not the
standard's.** The primary text never uses "ALARP" as an acronym; Annex
C.2 spells out the underlying approach as *"reducing risk as low as
reasonably practicable"* alongside two siblings, *"reducing risk as
low as reasonably achievable"* and *"reducing risk as far as possible
without adversely affecting the benefit-risk ratio."* This document's
title retains "ALARP" as a familiar shorthand for the first of those
three, consistent with how the practicability approach is actually
argued below (Section 2) — not as a claim that the standard names or
defines an "ALARP determination" as such.

**Status:** _PENDING_ | Created: 2026-07-21 | Citations verified against
primary source: 2026-07-21

## What this document does and does not do

This is **structure only** — the same discipline
`contract_attestation.py`'s checker already enforces on contract
ratification: a script (if one is ever built for this file) could
verify every section below is present and non-`_PENDING_`, but it can
never judge whether the *content* of a section is a defensible clinical
and engineering judgment. That judgment belongs to Steven alone, as the
named Clinical SME (`RISK_MANAGEMENT_PLAN.md` Section 2) — this repo's
assistant does not draft ALARP justification prose pretending to be
Steven's words, for the same reason no Gate C6 sign-off has ever been
self-recorded in this repo's history.

## Scope of this determination

**Hazard:** `HAZ-GIP-1.14b` — reverse-delivery clamp fires with no
proven clinician notification (`HAZARD_REGISTER.md`).

**Why this hazard, specifically, needs an ALARP path rather than
waiting on Path 1 (real field data):** `HAZ-GIP-1.2b` and
`HAZ-GIP-1.14b` are both blocked on Finding 5's open question (whether
TR 24971 §5.5.3's severity-alone evaluation applies to a zero-evidence
hazard) — but `HAZ-GIP-1.14b` carries an additional structural fact:
at `S4 — Critical`, §4.3's acceptance matrix never yields `Acceptable`
at any probability band, not even a favorable one. The best attainable
result via Path 1 is `ALARP` at `P1 — Improbable` — meaning Path 2
(a real ALARP determination) is not a fallback here, it is the only
path that can ever resolve this specific hazard past `Unacceptable`
or an unresolved `GAP`, regardless of what field data eventually shows.

**What this determination does not attempt:** it does not argue
`HAZ-GIP-1.14b` should be `Acceptable` — the matrix structurally
forbids that outcome for an `S4` hazard. It argues, if the sections
below can honestly be completed, that `ALARP` is a legitimate resting
point for this specific residual risk, at this specific development
stage, with the reasoning recorded rather than asserted by omission.

---

## 0. Relationship to Finding 5 — must be stated before sections 1–4 are written

**Why this section exists, added 2026-07-21:** Section 5's own stated
method requires a hazard to actually evaluate `ALARP` (§4.3's matrix)
before its residual can become device-level `Tolerable` — and for
`HAZ-GIP-1.14b` at `S4`, the matrix only outputs `ALARP` at `P1`, never
at `GAP`. An ALARP determination therefore cannot simply bypass
`RISK_MANAGEMENT_FINDINGS.md` Finding 5 (whether TR 24971 §5.5.3's
severity-alone evaluation applies to a zero-evidence hazard) — it must
either resolve it or explicitly declare it is not relying on it. Doing
this silently, by writing a disproportionality argument in Section 2
that happens to rest on "severity alone justifies tolerability
regardless of likelihood," would be exactly Option A adopted by
omission rather than recorded as a real Finding 5 closure — the
failure mode this repo's change-log discipline exists to prevent.

**Resolved 2026-07-22 — path (a): Finding 5 is closed first, via Option
C.** Recorded in `RISK_MANAGEMENT_FINDINGS.md` as a dated Finding 5
closure (not inferred from this document's prose), per the requirement
above. Steven's decision, in his framing: **two-track — severity-alone
for the zero-evidence hazards, the full P×S matrix retained for hazards
with genuinely estimable probability.**

Why (a) and not (b): path (b) asked for a mechanism by which a hazard
whose §4.3 evaluation is `GAP` reaches device-level `Tolerable` under
Section 5's method as written. There is none — Section 5 defines
outcomes for `Acceptable` / `ALARP` / `Unacceptable` hazards and is
silent on `GAP`. So (b) was never actually available, and (a) is the
honest path, as this section anticipated.

What Option C changes for this hazard, concretely: `HAZ-GIP-1.14b` is a
zero-evidence hazard (no Dafny/CrossHair/concrete-test artifact bears on
clinician notification), so it leaves the P×S matrix and is evaluated
**on its `S4 — Critical` severity alone**, per TR 24971 §5.5.3 ("When
the probability of occurrence of harm cannot be estimated, it is
necessary to evaluate the risk on the basis of the severity of harm
alone"). Its `Probability` is no longer a `GAP` the matrix waits on; it
is deliberately not scored, because under this track it does not need to
be. **Sections 1–4 below _are_ that severity-alone acceptability
determination** — they are what decides whether this `S4` residual risk
is a legitimate resting point at this development stage, with the
practicability reasoning (§2) recorded rather than asserted by
omission. This section does not pre-judge that outcome; it only
establishes that the determination may now honestly be written.

---

## 1. Risk control measures already exhausted within this kernel's stated scope

_PENDING_ — name, specifically, what has actually been proven or
bounded-checked at kernel scope (the fault-detection and zeroing
behavior — `REQ-GIP-1-8-1`, `PROVEN`), and state plainly that no
further Dafny/CrossHair/concrete-test work inside
`examples/dosage_calculator/` can close the notification gap, because
notification is not a property of this kernel's inputs and outputs at
all — it requires components (alarm hardware, UI layer, integrated
firmware) this artifact does not contain. This section should read as
a genuine exhaustion argument, not a restatement of the hazard.

## 2. Practicability: why further reduction is not undertaken at this development stage

**Basis, corrected 2026-07-21 against the primary text:** not a
cost-benefit legal test — Annex C.4 ("Risk control") names two
distinct components instead, and both should be addressed separately,
not blended into one "disproportionality" argument:

- **Technical practicability** — the ability to reduce the risk
  *regardless of cost*. For `HAZ-GIP-1.14b`, this is close to a
  factual question: can clinician notification be built at all inside
  this repo's current scope? The honest answer is no — it requires an
  integrated pump system (hardware, firmware, alarm hardware, UI layer
  per IEC 60601-1-8's alarm-system requirements — already named in
  `RISK_MANAGEMENT_PLAN.md`'s "Path to sign-off" section), not
  additional Dafny/CrossHair/test work inside
  `examples/dosage_calculator/`.
- **Economic practicability** — the ability to reduce the risk
  *without making the device an unsound economic proposition*. The
  primary text is explicit that this cannot be argued as "too
  expensive for a POC, so it's accepted" — it carries its own guard
  clause: economic practicability "should not be used as a rationale
  for the acceptance of unnecessary risk." If this section leans on
  economic practicability at all, it must state why building a minimal
  notification path is genuinely disproportionate to what a pre-market
  POC needs to demonstrate, not merely costly or inconvenient.

_PENDING_ — write both components separately. If technical
practicability is the real answer (this literally cannot be built
inside this repo's stated scope, independent of cost), say so plainly
and the economic-practicability paragraph may be short or unnecessary.
If economic practicability is doing real work in the argument, it must
survive the guard clause above, explicitly, not by omission. If
neither holds — if a minimal notification path actually is
technically and economically practicable even at this stage — that is
itself a finding this section should surface, not suppress.

## 3. Compensating controls already in place

_PENDING_ — what stands between this residual risk and a patient right
now, independent of any signal this kernel could emit. `RISK_MANAGEMENT_PLAN.md`
and `metadata.a.yaml`'s `classification_rationale` already name
clinician oversight as a real compensating control for related
hazards — state whether, and how, that same compensating control
applies here, and be specific about its limits (an unaddressed line
fault has no signal *prompting* that oversight to look in the right
place — state whether that materially weakens the compensating-control
argument compared to the other hazards it's cited for).

## 4. The residual risk, stated without minimization

_PENDING_ — what remains true and unresolved after sections 1–3, in
plain terms: a clinician may never learn that a reverse-flow fault
occurred, the underlying hardware defect can recur or go unaddressed,
and this repo has zero evidence — not weak evidence, zero — bearing on
how often that would actually happen. This section exists specifically
so the determination cannot read as resolving the risk; it should read
as a clear-eyed acceptance of what is *not* being claimed.

---

## Sign-off

- Clinical SME: _PENDING_
- Date: _PENDING_
- Determination: _PENDING_ — "Having examined sections 1–4 above, I
  determine that the residual risk represented by `HAZ-GIP-1.14b` is
  ALARP at this development stage, and record this as a policy
  judgment I stand behind, not a technical conclusion the evidence
  compelled."
- Status: _PENDING_ (a freshly created template is `_PENDING_` —
  structurally present, not yet a real determination)

**If sections 1–4 cannot honestly be completed as written** — for
example, if further risk control genuinely is proportionate at this
stage, or the compensating-control argument doesn't actually hold for
this hazard the way it does for others — **this document should say
so and stop**, the same way `contract_attestation.py`'s own
instructions tell a reviewer to stop and change the contract rather
than force a Wrong-if/Gap-if to eliminate when it cannot honestly be
eliminated. An honest `ALARP` determination that was never reached is
worth more than one recorded to close this out.
