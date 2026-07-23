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

**Status:** `PREPARED FOR SME REVIEW` (§§1–4 complete and
evidence-grounded, 2026-07-22; the SME ALARP determination itself
remains `_PENDING_` — see Sign-off) | Created: 2026-07-21 | Citations
verified against primary source: 2026-07-21

## What this document does and does not do

This is **structure only** — the same discipline
`contract_attestation.py`'s checker already enforces on contract
ratification: a script (if one is ever built for this file) could
verify every section below is present and non-`_PENDING_`, but it can
never judge whether the *content* of a section is a defensible clinical
and engineering judgment. That judgment — the ALARP determination
itself — belongs to a qualified clinical/regulatory **subject-matter
expert**, and remains `_PENDING_` in the sign-off below. What
PayloadGuard Research (`RISK_MANAGEMENT_PLAN.md` Section 2) provides is
the *preparation*: assembling the evidence and structuring §§1–4 so an
SME's determination is easy and well-grounded — never the determination
itself. This repo's assistant does not draft ALARP justification prose
pretending to be anyone's words, and no more than a non-SME preparer may
self-record the SME sign-off — the same drafter≠checker boundary for
which no Gate C6 spec sign-off has ever been self-recorded in this
repo's history.

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

`REQ-GIP-1-8-1` is `PROVEN`: `CalculateHourlyDose` yields exactly zero
delivered dose on any negative-rate (reverse-flow) fault — ordinary and
overflow-magnitude alike — via the Dafny proof, CrossHair bounded
search, and the concrete tests `ordinary_negative_rate_clamps_to_zero` /
`overflow_negative_rate_clamps_to_zero`. That is the whole of the fault
*response* this kernel can carry: detect the condition, zero the
delivered dose.

What it cannot carry is clinician *notification*. The kernel is a pure
numeric function; a signal to a human operator is not among its inputs
or outputs, and `metadata.a.yaml` confirms `REQ-GIP-1-8-1` has **no
`system_scope` field at all** (unlike `REQ-GIP-1-4-12`) — the
alarm-signal half is not even nameable at the requirement level here. No
further Dafny/CrossHair/concrete-test work over
`examples/dosage_calculator/` can produce evidence about whether a
clinician is alerted, because there is no output on which such evidence
could bear.

This is a genuine exhaustion of *this kernel's* risk-control surface —
**not** a claim that the notification gap is unsolvable. The distinction
is carried deliberately into §2: closing it is buildable; it simply
cannot be built inside this artifact, and building it here *now* is not
the proportionate step at this stage.

## 2. Practicability: why further reduction is not undertaken at this development stage

Per ISO/TR 24971 Annex C.4, practicability has two components,
addressed separately rather than blended into one "disproportionality"
claim. (§C.4 is *practicability*, technical and economic — not the
"gross disproportion" cost-benefit legal test, which is UK case law and
appears nowhere in the standard; verified against the primary text,
`sources/CEN-ISO-TR-24971-2020-E.docx`.)

**Technical practicability** (the ability to reduce the risk *regardless
of cost*) is **satisfied — not claimed impracticable.**
Clinician-notification hardware and firmware are commercially available
and could be obtained and tested; the fault-detection the kernel already
performs is a real, buildable input to such a path. This determination
does not rest on "it cannot be built" — it can.

**Why it is nonetheless not built here, at this stage.** This is a
pre-market proof-of-concept whose stated purpose is *architecture
generalization* — testing whether this verification method holds across
domains — not a shipped medical device (cf. `aeb_kernel`, deliberately a
test environment, not a submission). The proportionate next engineering
step is to demonstrate the notification-verification architecture on a
**cheaper, lower-classification, domain-agnostic device**, where the
output is simpler and more defensible precisely because it sheds the
medical-device regulatory load — not to stand up an integrated
infusion-pump alarm-and-UI path with its full validation burden. The
regulatory gap is real: a US infusion pump is a **Class II** device
(special controls + 510(k) premarket notification); a domain-agnostic
non-medical device carries none of that. And the property is the *same*
property — ANSI/ISA-18.2-2016 / IEC 62682 (a domain-agnostic
alarm-management standard, `sources/ISA-18.2-2016.PDF`, read directly)
defines an **alarm** (§3.1.7) as an "audible and/or visible means of
indicating to the operator … requiring a timely response" and
**annunciation** (§3.1.8) as the "function of the alarm system to call
the attention of the operator to an alarm": the identical detect →
signal split as IEC 60601-1-8's ALARM CONDITION → ALARM SIGNAL, with no
patient and no medical regulation. The architecture-generalization step
is not a detour from this hazard; it is the same notification-integrity
question on a proportionate vehicle.

**Surviving the guard clause.** §C.4 forbids economic practicability
being "used as a rationale for the acceptance of unnecessary risk." This
determination does not lean on cost, and it accepts no unnecessary risk:
**this is a pre-market POC with no deployment — no patient is exposed to
`HAZ-GIP-1.14b` at all.** The residual is notional at this stage; nobody
is running it. Deferring the pump-specific notification path to a real
submission phase, while advancing the method on a low-stakes device, is
proportionate *precisely because there is no patient exposure to weigh
against the deferral*. Were this a shipped device with patients, the
same deferral would fail this clause; at POC stage with no deployment,
it does not.

## 3. Compensating controls already in place

`metadata.a.yaml`'s `classification_rationale` names *clinician
oversight* as a compensating control — but it was written for a specific
mechanism that does not transfer to this hazard. **The rationale's
mechanism:** a dose-*magnitude* error (over- or under-dose by degree)
produces a directional physiological deviation in the patient; the
patient's own clinical state is the sensor, and no device signal is
required for a clinician on routine monitoring to notice it.

**`HAZ-GIP-1.14b` is not a magnitude error.** Reverse-flow triggers
*complete cessation* of delivery, and the resulting clinical signal is
the **absence of an expected therapeutic effect** — a slower, less
specific signal than a directional deviation, and one far more easily
attributed to disease course, patient variability, or normal delay
before drug effect than an acute over-/under-dose reaction is. Over an
8–12 hour round, that ambiguity has a long window to go unresolved. This
is not a tension introduced here: `HAZARD_REGISTER.md`'s row for
`HAZ-GIP-1.14` (the parent this split from) already states that "reverse
delivery of drug is a materially different failure mode from
over/under-dose" and declines to assume comparability to the
magnitude-error hazards. And GIP v1.0's own hazard analysis lists this
hazard's designed response as **`Alarm();Log()`** — an active signal —
meaning the source analysis treated active notification as the intended
control here; passive clinical vigilance was never it.

**The compensating-control claim splits into two, and they do not hold
equally:**

1. *Oversight protects the immediate patient from prolonged, undetected
   under-delivery* — **weakly plausible.** A clinician on rounds who
   notices non-response can intervene — but the signal is ambiguous and
   delayed relative to the magnitude-error case the rationale was
   written for, for the structural reasons above.
2. *Oversight protects against the underlying fault (line/connector
   defect) recurring or going unaddressed* — **not materially
   supported.** A clinician who correctly infers "this patient isn't
   responding" and resets or replaces the pump has no cue, absent
   notification, to root-cause a reverse-flow event *specifically*; the
   fault can survive the incident that revealed it. `metadata.a.yaml`'s
   rationale was written for dose titration, not fault diagnosis, and
   was never built to support this claim — which is also precisely what
   this hazard's `S4` severity is about (`HAZARD_REGISTER.md`: "the
   fault condition can recur or go unaddressed").

**Conclusion:** clinician oversight is a real, if weak, compensating
control for claim 1, and **not** a real compensating control for claim
2. If §4's residual-risk statement or the sign-off leans on "clinician
oversight" as a single, undifferentiated control the way
`metadata.a.yaml` states it for the delivered-dose hazards, that would
be citing a control for a claim there is no evidence for.

## 4. The residual risk, stated without minimization

After §§1–3, what remains true and unresolved:

- The reverse-flow fault is detected and the delivered dose is proven
  zero (§1) — but **no clinician is notified**, and per §3 there is no
  compensating control for the fault itself. A clinician may never learn
  that a reverse-flow event occurred; and even where routine oversight
  catches the resulting under-delivery (§3, claim 1 — weakly), it
  provides no cue to root-cause the fault, so **the underlying
  line/connector/hardware defect can recur or go unaddressed** (§3, claim
  2 — uncovered). The fault can survive the incident that revealed it.
- This repo has **zero evidence — not weak evidence, zero** — bearing on
  how often a reverse-flow fault would occur, or how often it would go
  unaddressed. There is no Dafny, CrossHair, concrete-test, or field
  data on frequency; that absence is exactly why this hazard is on the
  severity-alone track (Finding 5, Option C), not the probability
  matrix.
- Evaluated on severity alone, `HAZ-GIP-1.14b` is `S4 — Critical`.
  §4.3's matrix has no `Acceptable` cell for `S4` at any band; the
  highest resting point this residual can reach, even granting
  everything in §§1–3, is **`ALARP` — and only at this development
  stage.** It is not `Acceptable`, and this determination does not claim
  it to be.

What is therefore **not** being claimed: that the hazard is closed; that
a notification path exists; that clinician oversight covers the
fault-recurrence dimension (§3 is explicit it does not); or that a
shipped device with real patients could rest here. The acceptance is
narrow and conditional: at a **pre-market POC with no deployment and no
patient exposure** (§2), with kernel-scope risk control exhausted (§1)
and further reduction here not the proportionate stage-appropriate step
(§2), the `S4` residual is recorded as `ALARP` *for this stage only*. A
real deployment must build and validate the notification path — the
domain-agnostic architecture-generalization work §2 points to, then its
medical-device instantiation — before this hazard could be reduced
further; until then the residual stands, explicitly not minimized and
explicitly not `Acceptable`.

---

## Sign-off

- **Prepared by:** PayloadGuard Research — Steven (DarkVader-PLG),
  2026-07-22. Evidence assembly and the §§1–4 reasoning, structured for
  SME review. The §3 clinical-mechanism reasoning (how a
  delivery-cessation fault presents versus a dose-magnitude error) was
  informed by **informal guidance from practising clinical contacts** —
  advisory input to this preparation, not a sign-off; they advise on the
  POC and cannot ratify it during development. This is a **prepared
  determination package, not a clinical-SME determination.**
- **SME determination:** _PENDING_ — the ALARP call itself awaits a
  qualified clinical/regulatory subject-matter expert. It is
  deliberately left open: a POC preparing the ground does not also sign
  the ground off. The template's determination sentence is retained
  below for the SME to affirm, edit, or replace, not as a recorded
  determination: *"Having examined sections 1–4 above, I determine that
  the residual risk represented by `HAZ-GIP-1.14b` is ALARP at this
  development stage, and record this as a policy judgment I stand behind,
  not a technical conclusion the evidence compelled."*
- **Status:** `PREPARED FOR SME REVIEW` — §§1–4 complete and
  evidence-grounded; the ALARP determination is not yet made.

**If sections 1–4 cannot honestly be completed as written** — for
example, if further risk control genuinely is proportionate at this
stage, or the compensating-control argument doesn't actually hold for
this hazard the way it does for others — **this document should say
so and stop**, the same way `contract_attestation.py`'s own
instructions tell a reviewer to stop and change the contract rather
than force a Wrong-if/Gap-if to eliminate when it cannot honestly be
eliminated. An honest `ALARP` determination that was never reached is
worth more than one recorded to close this out.
