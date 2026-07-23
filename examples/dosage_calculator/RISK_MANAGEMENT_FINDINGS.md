# Risk Management Findings — dosage_calculator (provisional)

**Status:** PROVISIONAL — working ledger, not a closed document.
**Covers:** `RISK_MANAGEMENT_PLAN.md` and `HAZARD_REGISTER.md`, this
example only.
**Purpose:** single point of reference for every finding raised against
these two artifacts to date, whether resolved or open, so a reader
doesn't need the original chat session or the standalone audit report
to know current state.
**Last updated:** 2026-07-15 (yet later still — Finding 6 fully closed:
the underlying IEC 60601-2-24:1998 clause 51.102 itself now read
directly and confirmed to match GIP's citation near-verbatim, closing
the "IEC standard's own text remains unread" gap Finding 6 originally
left open).

---

## Status ledger

| # | Finding | Verdict | Status | Where |
|---|---|---|---|---|
| 1 | Clause 4.4 header citation stale | Refuted on audit | Closed, no action | — |
| 2 | "ISO 14971's own Annex D" cited — doesn't exist in 2019 edition | Confirmed | **Remediated, 2026-07-15 (verified applied, not just claimed)** | `RISK_MANAGEMENT_PLAN.md` §4.3, Path-to-sign-off; `HANDOFF.md`; `DEVLOG.md` (×2, corrected in place with a bracketed note per this log's append-only discipline); `README.md`. **Correction to this row's own location list:** `KNOWN_LIMITATIONS.md` was checked directly and does not contain the "Annex D" citation error — its one "ALARP" mention is a correct use of the policy concept (clause 4.2 NOTE 1), not a false citation. This ledger's earlier claim that it needed the fix was itself inaccurate. |
| 3 | Severity bands conflate risk control with risk estimation | Confirmed | **Fully resolved, 2026-07-15 — model rebuilt (Option 3), then real severity values recorded from Steven the same day: `S3 — Serious`, all 5 hazards. Device overall residual risk now `Unacceptable`, computed, not `GAP`** | `RISK_MANAGEMENT_PLAN.md` §4.1, §4.3, Section 5, Path-to-sign-off; `HAZARD_REGISTER.md` (all 5 hazards) |
| 4 | `HAZ-GIP-1.2`/`1.3` name a proven-closed pathway while describing an open one | Confirmed | **Remediated (structurally), 2026-07-15 (verified applied, not just claimed)** — `HAZ-GIP-1.2b` split out; `HAZ-GIP-1.2`/`1.3`'s own Severity/Probability marked stale/pending re-derivation rather than silently carried over; `HAZ-GIP-1.2b`'s Probability left `GAP`, not defaulted to P5, per Finding 5 below | `HAZARD_REGISTER.md` |
| — | No checked equivalence claim between `dosage.py`/`dosage.dfy` | Confirmed, then resolved | **Resolved, 2026-07-15 — Option 2 (differential-testing harness) built; 9/9 vectors matched; postcondition drift found and fixed in the same pass** | `dosage_differential_vectors.py`, `dosage_differential_driver.dfy`, `differential_test_results.json` |
| 5 | Inestimable-probability hazards should be evaluated on severity alone (TR §5.5.3), not the full matrix | New, from direct TR 24971 read | **Resolved 2026-07-22 — Steven chose Option C (two-track): severity-alone for the zero-evidence hazards, full matrix retained for hazards with estimable probability.** The two zero-evidence hazards (`HAZ-GIP-1.2b`, `HAZ-GIP-1.14b`) move onto the severity-alone track; each still needs its own severity-alone acceptability determination (`HAZ-GIP-1.14b`'s is `ALARP_DETERMINATION.md`, in progress; `HAZ-GIP-1.2b`'s is pending) | `HAZ-GIP-1.2b`, `HAZ-GIP-1.14b`; `ALARP_DETERMINATION.md` §0 |
| — | TR 24971's real three-region matrix uses different region names than "ALARP" | New, from direct TR 24971 read | **Open — naming reconciliation, Steven's call** | `RISK_MANAGEMENT_PLAN.md` §4.3 |
| 6 | `HAZ-GIP-1.14`'s GIP Safety Requirement 1.8.1 citation, quoted as "verbatim" in this repo, was never checked against the primary IEC-cited text | Confirmed — real wording drift found, then the underlying IEC clause itself independently confirmed | **Fully closed, 2026-07-15.** GIP-transcription wording corrected in `sources/gip-v1.0-hazard-analysis.md`, `metadata.yaml`/`.a`/`.b`/`.c.yaml`, `HAZARD_REGISTER.md`; traceability matrices regenerated (no hand-editing). Two primary sources now archived, both obtained directly by Steven, not third-party mirrors: `sources/gip-v1.0-full-2009.pdf` (GIP v1.0 itself) and `sources/iec-60601-2-24-1998.pdf` (the actual IEC standard, Edition 1). **Clause 51.102 "Reverse delivery" read directly — GIP's citation confirmed near-verbatim.** Byproduct, also confirmed directly: GIP v1.0 assigns no severity rating to any hazard in any of its 8 hazard-table categories | `sources/gip-v1.0-hazard-analysis.md`, `sources/gip-v1.0-full-2009.pdf`, `sources/iec-60601-2-24-1998.pdf`, `sources/README.md`, `HAZARD_REGISTER.md`, `metadata.yaml`/`.a`/`.b`/`.c.yaml` |

---

## Resolved items — brief record

### Finding 2 — Annex D citation

ISO 14971:2019 has no Annex D (third edition contains only A, B, C).
Table B.1 records the 2007 edition's Annex D as moved to ISO/TR 24971.
Both citation sites corrected; `sources/ISO-24971-2020.pdf` has since
been obtained and read (2026-07-15), see Finding 5 and the naming item
below for what that reading actually surfaced.

### Finding 4 — hazard split

`HAZ-GIP-1.2`/`HAZ-GIP-1.3` previously named "overinfusion," a pathway
Dafny-proves closed, while their own residual/severity fields already
described a different, open situation (no proof a clinician is ever
told a clamp fired). Split, not renamed: the GIP-sourced traceability
anchor (HID 1.2/1.3) stays on the original rows, narrowed to the
pathway it actually covers; the real residual moved to a new row,
`HAZ-GIP-1.2b`. `HAZ-DOSE-003`'s related masking mechanism was
cross-referenced but deliberately not folded in — left as Steven's
register-organization call.

**What's still open here:** `HAZ-GIP-1.2b`'s severity is `GAP`, not
scored — same clinical-judgment dependency as everything else in §4.1.
Its probability is also left `GAP`, deliberately **not** defaulted to
P5 — Finding 5 below questions whether P5-plus-matrix is even the
right procedure for this specific row, and presuming P5 during the
restructuring would have prejudged that open question rather than
just restructured the register. `HAZ-GIP-1.2`/`1.3`'s own prior
`DRAFT: S2`/`P5` values are likewise not carried over to the narrowed
rows — marked stale/pending re-derivation instead, since that DRAFT
reasoning was based on the residual that moved to `HAZ-GIP-1.2b`.

### Finding 3 — severity model

Direct instruction, 2026-07-15: "work through R3's severity model."
Option 2 was eliminated on textual grounds before asking Steven to
choose (TR 24971 §5.5.4 states severity must exclude probability,
directly contradicting the old evidence-strength bands). Steven chose
**Option 3 (hybrid)** over Option 1 (`AskUserQuestion`). Applied across
`RISK_MANAGEMENT_PLAN.md` (§4.1's bands rebuilt consequence-only, plus
a new per-hazard evidence-artifact column; §4.3's matrix, Section 5's
overall-residual-risk method, and the "Path to sign-off" section all
updated to report `GAP` instead of the old, invalidated
`Acceptable`/`Unacceptable` outputs) and `HAZARD_REGISTER.md` (all 5
hazards' `Severity`/`Risk evaluation` set to `GAP`, `Probability`
reverted to the standing §4.2 default policy). Full record below.

**Update, 2026-07-15 (later): fully closed.** The per-hazard severity
**values** are no longer open — Steven scored all five hazards `S3 —
Serious` via `AskUserQuestion` the same day. `RISK_MANAGEMENT_PLAN.md`
§4.3's matrix and Section 5's combination method both now produce real
evaluations: four hazards `Unacceptable`, `HAZ-GIP-1.2b` still `GAP`
(blocked by Finding 5's separate, still-open Probability-side
question, not by Severity). This device's overall residual risk is now
`Unacceptable`, a computed result, not `GAP`. See the full write-up
below for detail this brief record doesn't repeat.

### R5 — equivalence gap (`dosage.py` / `dosage.dfy`)

Direct instruction, 2026-07-15: "let's look into R5 directly." Verified
the equivalence claim by direct comparison before proposing options: for
every input where `raw_dose` is finite, both implementations' branch
logic matches exactly (`raw_dose < 0` → 0; `raw_dose > max` → max; else
→ `raw_dose`) — confirmed, not assumed. Found one new, previously
unflagged issue during that verification: the two files' *documented*
postconditions had already drifted — Dafny's `ensures` was tightened to
strict `infusionRateMlPerHr > 0.0` on 2026-07-07 (Gate C5 mutation
finding), never back-ported to `dosage.py`'s docstring `post:` line,
still `>=`. Confirmed `dafny run` executes concrete inputs in this
environment before proposing Option 2, changing its cost/risk profile
from "moderate effort, not attempted" to "concretely buildable now."

Steven chose **Option 2 (differential-testing harness)**, plus fixing
the postcondition drift (`AskUserQuestion`). Both built:

- `dosage.py`'s postcondition tightened to `> 0`, matching `dosage.dfy`;
  CrossHair re-run and re-verified clean (`raw_crosshair_output.txt`,
  `run_manifest.json`); `traceability_matrix.a.*` and siblings
  regenerated via `generate_artifacts.py`.
- `dosage_differential_vectors.py` — 9 shared test vectors (single
  source of truth for both sides), `generate_dosage_differential_driver.py`
  → `dosage_differential_driver.dfy` (generated, committed, calls the
  real `CalculateHourlyDose` via Dafny's own `include`, not a
  reimplementation), `run_verify_dosage_differential.py` → real `dafny
  run` capture (`raw_dafny_differential_output.txt`,
  `run_manifest_dafny_differential.json`) compared against `dosage.py`'s
  live output → `differential_test_results.json`. **All 9 vectors
  matched.** `tests/test_dosage_differential.py` checks the generated
  driver matches its generator, the capture shows full agreement, and
  Python's live behavior still reproduces the captured values — no live
  Dafny invocation in CI, same discipline as every other Dafny capture
  here.

**Scope, stated explicitly, not implied:** this validates equivalence
only within the domain Dafny can represent — `raw_dose` finite. One
vector deliberately mirrors `tests/test_dosage_concrete.py`'s own
overflow case; both implementations agree there too, but via genuinely
different reasoning (Python: float overflow to `-inf`, still `< 0`;
Dafny: the exact large value, also `< 0`) — coincidental to this
vector's chosen magnitudes, not a general REQ-DOSE-003 equivalence
claim, which is structurally impossible in Dafny's `real` type and
remains permanently out of reach (`dosage.dfy`'s own header comment).

---

## Resolved — Finding 6: `HAZ-GIP-1.14`'s "verbatim" GIP citation had never been checked against the primary text

Surfaced by Steven pressing on the S3 severity discussion for
`HAZ-GIP-1.14`: this repo cited GIP Safety Requirement 1.8.1
("Continuous reverse delivery shall not be possible during normal use
or a single-fault condition," attributed to IEC 601-2-24) as if it were
a direct quote, in `HAZARD_REGISTER.md`, `metadata.yaml`/`.a`/`.b`/`.c.yaml`,
and `sources/gip-v1.0-hazard-analysis.md` — but that transcription had
never actually been checked against GIP v1.0's own PDF. This repo only
ever had a reformatted markdown copy of that PDF, whose own header
claimed "wording... unchanged" without that claim ever being tested.

**What actually happened, in order:**

1. Steven independently researched the underlying IEC 60601-2-24
   citation externally (free-flow vs. reverse-delivery distinction,
   edition history) and found a secondary (ResearchGate-hosted)
   rendering of GIP's own text that read: "During normal use and/or
   single fault condition of the equipment, continuous reverse delivery
   shall not be possible (from IEC 601-2-24)" — reported as a "verbatim
   match" to this repo's citation.
2. Direct comparison against what this repo actually had committed
   showed it was **not** a verbatim match — clause order reversed, "or"
   vs. "and/or", "of the equipment" present in one and not the other.
   Flagged rather than accepted at face value: this repo's own
   transcription and the newly-found secondary source disagreed on
   exact wording, and neither had been checked against a primary copy.
3. Steven obtained the actual GIP v1.0 PDF directly from the University
   of Pennsylvania (not a mirror) and supplied it. Read directly, all 17
   pages (`sources/gip-v1.0-full-2009.pdf`, now archived).

**Result: the secondary (ResearchGate) source was right; this repo's
own transcription was the one that had drifted.** The primary PDF's
§1.8 "Reverse delivery," requirement 1.8.1 (page 12), reads exactly:
"During normal use and/or single fault condition of the equipment,
continuous reverse delivery shall not be possible (from IEC 601-2-24)."
Fixed in all six places it appeared, verbatim, not by choosing whichever
reading seemed more natural. The §2.4.1 Operational Hazards table row
for HID 1.14 ("Improper flow," Type `FRN`, Cause "Bleed back; Reflux
within device," mitigated by "Flow sensor," Safety Req "1.8") was also
checked directly and matches this repo's existing citation exactly — no
drift there, so that row's own long-standing "not yet independently
re-verified against the raw §2.4.1 text" caveat is now resolved too.

**A genuine byproduct, not the original question, but now closed
either way**: the primary PDF's hazard tables span all eight categories
(§2.4.1–2.4.8, HID 1.1 through 8.14 across Operational, Environmental,
Electrical, Hardware, Software, Mechanical, Biological/Chemical, and
Use hazards) — none of them carry a severity column. GIP v1.0 simply
never rates severity for any hazard it lists, confirmed directly rather
than inferred from `metadata.a.yaml`'s `classification_rationale`
alone. This closes the "GIP's own hazard-table severity rating" item
that was still open in the `HAZ-GIP-1.14` severity discussion — not by
finding a rating, but by confirming none exists to find.

**Update, 2026-07-15 (later): the remaining gap is now closed too.**
The paragraph above, as originally written, said the IEC standard's own
text remained unread — that stood only briefly. Steven obtained and
supplied the actual IEC 60601-2-24:1998 (First edition, 1998-02) — the
correct edition, confirmed by the same publication-date logic already
established (GIP, Feb 2009, predates Edition 2's October 2012
publication by three years). Read directly and in full, 58 pages,
cover through Annex ZB, not excerpted or assumed.

**Clause 51.102, "Reverse delivery" (p.36, no Annex AA rationale
marker — one of the few clauses in this standard without one):**
"During NORMAL USE and/or SINGLE FAULT CONDITION of the EQUIPMENT,
continuous reverse delivery, which may cause a SAFETY HAZARD, shall not
be possible." Compared directly against GIP's own transcription (fixed
above): the match is near-verbatim — same clause order, same "and/or,"
same "single fault condition of the equipment" — GIP omits only the
middle clause "which may cause a SAFETY HAZARD." Not a loose paraphrase
GIP happened to get right; a citation this close to word-for-word that
this repo can now confirm directly, not take on GIP's authority alone.

This repo's evidentiary basis for `HAZ-GIP-1.14`'s regulatory citation
is no longer GIP v1.0 as a trusted secondary source one hop short of
the standard — it is now the standard's own clause text, read directly,
archived (`sources/iec-60601-2-24-1998.pdf`), with GIP's paraphrase
independently confirmed faithful to it. This is this repo's first
direct read of any IEC 60601-2-24 edition's actual text, for any
requirement.

Full pipeline discipline followed: no traceability matrix was
hand-edited — `generate_artifacts.py` (variants a/b/symbolic/concrete/
formal) and `generate_matrix.py` (the frozen base) were both re-run
against the corrected `metadata.*.yaml` files, all Tier 1 gates
(schema validation, both CONFLICT gate types, fact-equality, structural
PROVEN sweep) passed clean. 253 tests pass, unchanged.

---

## Resolved — Finding 3: severity/control conflation (full record)

**Resolved 2026-07-15 — Option 3 (hybrid) chosen.** Kept below for full
context (the option comparison and the TR Table 4 calibration
reference remain relevant to the next step, scoring each hazard); see
the brief record above for a one-paragraph summary.

**The plan's §4.1 defines severity by evidence strength** (S1: "Dafny-
proven... no harm pathway is open"; S4: "unproven failure mode") rather
than by consequence magnitude. ISO 14971:2019 §3.27 defines severity as
the measure of a hazard's possible consequences — independent of
control status. **ISO/TR 24971 §5.5.4 confirms this directly**:
severity levels should be descriptive and should not include any
element of probability. That's textual confirmation from the
referenced guidance document itself, not just an inference from the
standard.

**Consequence, as originally illustrated (pre-resolution context, not a
scored value — that illustration held even before R3 was resolved):**
a Dafny proof of unreachability is a probability claim wearing a
severity label. Re-scoring `HAZ-GIP-1.14` (reverse delivery) by
consequence alone *might plausibly* land S3–S4 (IEC 601-2-24's "shall
not be possible" mandate, GIP's own physical-sensor mitigation) — this
was, and remains, an illustration of why the old model mattered, not a
prediction of what Steven's actual scoring will produce. §4.1 now
carries `GAP` for this hazard's severity, not a number; this paragraph
is preserved as the reasoning that motivated fixing the model, not as
a stand-in for the still-outstanding clinical determination.

### R3 options — Steven chose Option 3, 2026-07-15 (`AskUserQuestion`)

**Option 1 — Adopt the standard's model.** Severity by consequence
alone; proofs/bounds move probability, not severity. Buildable
mechanically; the actual consequence values need Steven's clinical
input — most severity cells become explicit `GAP`s, which is arguably
correct rather than a regression.

**Option 2 — Keep the current model, justify per hazard under §7.1
NOTE 2.** That clause permits a control to reduce severity, but only
when it shrinks the harm's *magnitude if it occurs* — not when it
eliminates whether it occurs. A proof does the latter. **Eliminated
before Steven was asked to choose** — not defensible for the
proof-reliant hazards (`HAZ-GIP-1.14` especially), and TR §5.5.4
states the exclusion directly, leaving no textual room for this option.

**Option 3 — Hybrid. Chosen.** Consequence-only severity, plus an
explicit "which evidence artifact drives this probability" column.
Preserves the current model's real strength (traceability from a risk
cell to a `raw_dafny_output.txt`) without asking severity to silently
encode it. Built into `RISK_MANAGEMENT_PLAN.md` §4.1 and
`HAZARD_REGISTER.md` 2026-07-15.

**Then decided — the actual scoring, 2026-07-15 (later).** TR 24971's
Table 4 (five consequence-only severity descriptors: Catastrophic/
Fatal, Critical, Serious/Major, Minor, Negligible) was the real,
source-backed calibration reference `RISK_MANAGEMENT_PLAN.md` §4.1
already cited for the clinical work this required. Direct instruction:
"start on the severity values for the 5 hazards." Recorded via
`AskUserQuestion`, one hazard at a time, against §4.1's real
consequence-only bands and each hazard's own documented `Potential
harm` text (not against evidence strength — the exact conflation this
finding exists to prevent). **Result: `S3 — Serious`, all five
hazards** (`HAZ-GIP-1.14`, `HAZ-GIP-1.2`, `HAZ-GIP-1.3`,
`HAZ-GIP-1.2b`, `HAZ-DOSE-003`) — notably including `HAZ-GIP-1.14`
despite it carrying this register's strongest probability-side
evidence (a full Dafny proof), confirming in practice the point this
finding's own illustration above predicted: severity and proof strength
are genuinely independent axes, not correlated ones.

Applying `RISK_MANAGEMENT_PLAN.md` §4.3's already-specified matrix to
these real values (a mechanical lookup, not a new judgment call) gives
`HAZ-GIP-1.14`/`HAZ-GIP-1.2`/`HAZ-GIP-1.3`/`HAZ-DOSE-003` →
`Unacceptable` (P5 × S3); `HAZ-GIP-1.2b` stays `GAP` at the evaluation
step, since its Probability, not its now-known Severity, is what
Finding 5 below leaves open. Per Section 5's already-specified
combination method, this device's **overall residual risk is now
`Unacceptable`** — a real, computed result, replacing the `GAP` status
this finding's model-only resolution left standing. Full detail:
`RISK_MANAGEMENT_PLAN.md` §4.1, §4.3, Section 5, and its "Path to
sign-off" section, all updated 2026-07-15 (later) alongside this entry.

---

## Resolved — Finding 5: inestimable-probability hazards and the matrix

**Resolved 2026-07-22 — Steven chose Option C (two-track).** Recorded
via direct decision during the `HAZ-GIP-1.14b` ALARP-determination
sitting (`ALARP_DETERMINATION.md` §0 required this closure before its
Sections 1–4 could be written). In Steven's framing: **severity-alone
for the zero-evidence hazards; the full P×S matrix stays for hazards
with genuinely estimable probability.** The two zero-evidence hazards
in this register — `HAZ-GIP-1.2b` and `HAZ-GIP-1.14b` (neither has any
Dafny/CrossHair/concrete-test evidence bearing on clinician
notification) — are the ones this moves onto the severity-alone track;
the proof-driven and matrix-evaluated hazards (`HAZ-GIP-1.14`, `1.2`,
`1.3`, `HAZ-DOSE-003`) are untouched.

**What this does and does not settle.** It settles the *procedure*: a
zero-evidence hazard is no longer parked at evaluation-`GAP` waiting on
a probability band it can never get; it is evaluated on severity alone,
via a recorded severity-alone acceptability determination. It does
**not** by itself produce an acceptability verdict for either hazard —
that determination is per-hazard and is where the real judgment lives.
`HAZ-GIP-1.14b`'s is `ALARP_DETERMINATION.md` (Sections 1–4, in
progress); `HAZ-GIP-1.2b`'s is a separate determination not yet
authored (its evaluation cell now reads "severity-alone track,
determination pending," replacing "blocked by Finding 5's open
question"). Option C's cost, accepted with the choice: a second
acceptability procedure now exists alongside the matrix, and both must
be documented — the severity-alone track is not a shortcut around the
matrix, it is a parallel, source-grounded (TR §5.5.3) route for the
specific class of hazard the matrix cannot honestly evaluate.

Prior write-up, preserved (the options as they stood before the
decision):

**Full write-up:** see the standalone finding document (same content,
reproduced in summary here for a single-file reference).

TR §5.5.3 covers exactly `HAZ-GIP-1.2b`'s situation — a hazard with no
evidence of any kind — and its actual recommendation is to evaluate
such risks **on severity alone**, not to assume worst-case probability
and run the full S×P matrix, which is what §4.4's current policy does.
These are procedurally different and can disagree on outcomes; which
is more conservative depends on where a severity-only threshold would
be set, a threshold that doesn't currently exist in this plan.

**Open interpretive question underneath this:** are hazards like
`system_scope`'s gap genuinely *inestimable* (TR's target case —
software failure, novel hazards) or merely *unmeasured* (the
integration work needed to measure it was simply never built, per
`RISK_MANAGEMENT_PLAN.md` Section 1's own scope boundary)? If the
latter, §5.5.3 may not even be the operative clause — the honest
statement might instead be "no risk control measure currently exists,"
a §7-territory statement, not a §5.5 estimation question. Not resolved
here.

### Options

**Option A — Adopt §5.5.3 literally.** Define a severity-only
acceptability rule for hazards judged genuinely inestimable. Most
textually faithful; requires both the threshold and the interpretive
call above before it can be applied to `HAZ-GIP-1.2b`.

**Option B — Keep P5-plus-matrix, justified explicitly as a deliberate
departure.** No new mechanism needed. Cannot honestly claim TR-24971
alignment without stating the departure and arguing (not assuming) it
is at least as conservative.

**Option C — Two-track.** Severity-alone for hazards with zero
evidence (`HAZ-GIP-1.2b`, and `HAZ-DOSE-003`'s masking mechanism if not
folded into it); full matrix retained for hazards with genuinely
estimable probability, including the proof-driven ones — a Dafny proof
is arguably a stronger probability basis than most of TR's own
"estimable" examples. Closest fit to the source; costs a second
acceptability procedure to maintain and document.

**Decided 2026-07-22 — Option C** (see the resolution note at the top of
this section). The interpretive question above (genuinely *inestimable*
vs. merely *unmeasured*) is answered implicitly by that choice: the
zero-evidence notification hazards are treated as inestimable and
routed to severity-alone evaluation, not as merely-unmeasured §7 cases.
Finding 3/R3 (the severity *model*) remains resolved and separate; this
was the last-open procedural question of the two.

---

## Open — matrix region naming

TR Annex C.4/Figure C.1's actual three-region matrix names its regions
**"unacceptable risk / investigate further risk control / insignificant
or negligible risk."** This plan's matrix uses "Unacceptable / ALARP /
Acceptable" — ALARP is a real TR 24971 concept, but it names a
risk-control-*policy* approach (clause 4.2 NOTE 1 / TR §C.2), not the
matrix's own middle-region label. The three-tier *structure* is
validated by the source; the *labels* conflated two adjacent concepts.

**Not decided:** rename the middle region to track TR's own wording, or
keep "ALARP" as a stated, deliberate departure from the source's
terminology. Either is defensible once stated explicitly; what isn't
defensible is the current unstated conflation.

---

## Resolved — R5: equivalence gap (`dosage.py` / `dosage.dfy`) (full record)

**Resolved 2026-07-15 — Option 2 (differential-testing harness)
chosen and built.** Kept below for full context; see the brief record
above for a one-paragraph summary.

`dosage.dfy`'s header comment asserts it is a "Dafny translation of
dosage.py's clamping kernel." Before proposing options, verified this
directly rather than trusting it: for every input where `raw_dose` is
finite, both implementations' branch logic is identical
(`raw_dose < 0` → 0; `raw_dose > max` → max; else → `raw_dose`). This
was structurally unique to `dosage_calculator`; the other two worked
examples are Dafny-only.

**Real finding surfaced during that verification, not previously
flagged:** the two files' *documented* postconditions had already
drifted. `dosage.dfy`'s `ensures` clause was tightened to strict
`infusionRateMlPerHr > 0.0` on 2026-07-07 (Gate C5 mutation-testing
finding: `>=` wasn't independently load-bearing at `rate == 0.0`
exactly). That fix was never back-ported to `dosage.py`'s docstring
`post:` line, which still said `>= 0`. Behavior was unaffected (dose is
0.0 at rate 0.0 either way), but the two contracts' stated strength had
silently diverged — a live instance of exactly what R5 warns about, in
this repo's own committed artifacts, found by direct comparison.

**Matters for:** any probability credit a Dafny proof would extend to
the Python artifact — concretely live, not conditional, since Finding
3/R3 resolved to Option 3 (2026-07-15): probability-from-proof is
load-bearing in `RISK_MANAGEMENT_PLAN.md` §4.1's evidence-artifact
column, no longer hidden inside a severity label.

### R5 options — Steven chose Option 2, 2026-07-15 (`AskUserQuestion`)

1. **Dafny-to-Python extraction/codegen.** Highest assurance, highest
   cost — not supported by the current toolchain without new tooling.
   Disproportionate for a POC. Not chosen.
2. **Differential-testing harness. Chosen.** Confirmed feasible before
   asking Steven to choose, not just assumed: `dafny run` actually
   executes concrete inputs in this environment (Dafny 4.11.0
   installed), and its `real`-typed output prints as clean decimals
   matching Python's float format — de-risking this option from
   "moderate effort, not attempted" to "concretely buildable now." 9
   shared vectors (`dosage_differential_vectors.py`) run through both
   `dosage.dfy::CalculateHourlyDose` (via a generated driver,
   `dosage_differential_driver.dfy`, calling the real function through
   Dafny's own `include`, not reimplementing it) and `dosage.py`'s real
   `calculate_hourly_dose`. **All 9 vectors matched**
   (`differential_test_results.json`). One vector deliberately mirrors
   `tests/test_dosage_concrete.py`'s own overflow case — agrees, but
   via genuinely different reasoning (documented explicitly in the
   vector's own `note` field and checked by a dedicated test), not a
   REQ-DOSE-003 equivalence claim, which stays structurally impossible
   in Dafny's `real` type.
3. **Explicit scoping statement.** Not needed as a standalone step —
   Option 2's harness and its documented scope caveats serve the same
   purpose with mechanical backing instead of prose alone. The caveat
   Option 3 would have stated (no REQ-DOSE-003 equivalence claimed) is
   the same caveat Option 2's own vector documentation states, checked
   by `tests/test_dosage_differential.py::test_overflow_vector_is_explicitly_documented_as_coincidental`.

**Postcondition drift, fixed in the same pass (Steven confirmed via
`AskUserQuestion`):** `dosage.py`'s `post:` line tightened to `> 0`,
matching `dosage.dfy`. Re-verified — `post:`/`pre:` are CrossHair-
enforced contracts, not comments, so this needed a real CrossHair
re-run (`raw_crosshair_output.txt`, `run_manifest.json`), not a silent
edit — clean, no new violations. `traceability_matrix.a.*` and
siblings regenerated via `generate_artifacts.py` to propagate the
capture's new content.

251 tests pass (5 new — `tests/test_dosage_differential.py`).

---

## Summary — what actually needs Steven, listed once

- **A real decision on this device's `Unacceptable` overall residual
  risk** (computed 2026-07-15, from Steven's own real severity scoring
  — see Finding 3 above): either real field/usage probability data
  (doesn't exist for a pre-market POC), or a genuine ALARP
  determination from a qualified clinical/regulatory SME (Steven /
  PayloadGuard Research *prepares* it — `ALARP_DETERMINATION.md`, SME
  sign-off `_PENDING_` — but is not the SME; Section 2, corrected
  2026-07-22), per
  `RISK_MANAGEMENT_PLAN.md`'s "Path to sign-off" section. This is now
  the concrete blocking item, replacing the severity-scoring item this
  list previously led with.
- ~~Finding 5: which evaluation procedure for inestimable-probability
  hazards~~ — **resolved 2026-07-22, Option C (two-track)**; the
  zero-evidence hazards go to severity-alone. What this leaves open is
  downstream, not Finding 5 itself: each zero-evidence hazard now needs
  its own severity-alone acceptability determination — `HAZ-GIP-1.14b`'s
  is `ALARP_DETERMINATION.md` (in progress), `HAZ-GIP-1.2b`'s is not yet
  authored
- Matrix region naming: reconcile to TR's wording or keep ALARP as a
  stated departure
- `HAZ-DOSE-003`: fold into `HAZ-GIP-1.2b` or keep separate

R5 (equivalence gap) is resolved as of 2026-07-15 — removed from this
list, kept in the ledger above for the record. Real severity scoring
(the item this list used to lead with) is likewise resolved as of
2026-07-15 (later) — see Finding 3 above; the `Unacceptable` result it
produced is what the new first bullet above is actually about.

None of these are resolved by this document. It exists so they're
findable in one place, not scattered across a chat session and an
external audit file.
