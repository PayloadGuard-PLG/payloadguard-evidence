# DEVLOG — payloadguard-evidence

Append-only session log. Every session adds one dated entry (UTC), newest
first, citing commit SHAs. Timestamps below are taken from the git history
and run manifests, not reconstructed from memory.

---

## 2026-07-09 — Rewrote README.md for a non-expert audience; added OPERATIONS_MANUAL.md

`README.md` had accumulated a full gate-by-gate build history (every
Gate C1-C6 finding, every mutation-testing operator count, every
extension) directly in the repository's front door — accurate, but
unreadable by someone evaluating whether to use the system rather than
already deep in its build log. Rewrote it as a plain-English overview:
what problem this solves, the core vocabulary (requirement / evidence /
strength / traceability matrix) explained without jargon, what's in the
repository, a quick start, and a status summary — no emojis, no gate
history, technical depth pushed out to linked documents instead of
inlined.

Added `OPERATIONS_MANUAL.md` as the "definitive manual... at a high
technical level" - the destination for that technical depth. Covers:
architecture and data flow, the Strength vocabulary and its enforced
invariants, the full evidence pipeline (author/capture/generate), all
six Dafny verification gates (C1-C6) explained by mechanism and purpose
rather than by chronological finding, a complete command reference, a
worked "how to add a new example" section distilled from the
renal-adjustment build (including the honest note that extending the
system to a second example found and fixed two real gaps in shared
tooling - not glossed over as if everything generalized cleanly on the
first try), testing discipline, the review protocol summary, and a
troubleshooting section.

Both documents cross-reference the existing detailed records
(`SYSTEM_BLUEPRINT.md`, `DEVLOG.md`, `KNOWN_LIMITATIONS.md`,
`REVIEW_PROTOCOL.md`) rather than duplicating them - the new manual
synthesizes current-state understanding; the existing docs remain the
dated, append-only record of how it got there. 142 tests unaffected
(documentation only).

---

## 2026-07-09 — Built Gate C4 for real: both predictions confirmed, both real gaps fixed properly

Instructed explicitly: solve any real problems found, don't skip or
apply a flimsy workaround. Built `renal_adjustment_stp_suite.dfy`
(44 lemmas: ACCEPT, REJECT, uniqueness, and totality checks across all
five functions, using the 16-row test-vector table from
`PHASE1_PLAN.md`) and ran it against the spec exactly as it stood,
before touching anything.

Both `gate_c4_stp_plan.md` predictions confirmed empirically, not just
by inspection: the four REJECT lemmas assuming a wrong candidate value
for `ComposedCeiling` (0.0 instead of the correct minimum) and
`AssessRenalFunction` (wrong G-stage / wrong CrCl value) genuinely
**failed to verify** - `0 verified, 4 errors`, a real Dafny run, not a
hypothetical. `RoundHalfUp`, `GStage`, and `SelectFormula`'s
ACCEPT/uniqueness/totality lemmas all passed on the same first run - the
predicted "these three are already tight" also confirmed for real.

Preserved the pre-fix state as an honesty exhibit before fixing anything,
mirroring `dosage_underconstrained.dfy`'s exact pattern: copied the
current file to `renal_adjustment_underconstrained.dfy`, and split the
four failing REJECT lemmas into their own file,
`renal_adjustment_stp_suite_against_underconstrained.dfy`, confirmed to
fail against the preserved original for real (`0 verified, 4 errors`,
captured verbatim, not smoothed over).

Fixed `renal_adjustment.dfy` itself with proper pinning `ensures`
clauses, not a workaround: `ComposedCeiling` gained
`ensures ComposedCeiling(...) == existingCeiling || ComposedCeiling(...) == renalCeiling`,
which combined with the existing two `<=` bounds forces the result to
equal `min(existingCeiling, renalCeiling)` exactly (if it equals
existingCeiling, the renalCeiling bound forces existingCeiling to BE the
minimum, and symmetrically). `AssessRenalFunction` gained two clauses
referencing its own composition directly
(`== EGFRAssessment(GStage(RoundHalfUp(renalFunctionValue)))` and the
CrCl-path equivalent) - the same self-referential pattern `ExpectedDose`
uses in `dosage.dfy`, not an ad hoc constraint chosen to make Dafny
happy without genuinely narrowing the postcondition.

Re-verified `renal_adjustment.dfy`: still `5 verified, 0 errors` -
neither function's body needed to change, only its stated contract.
Discovered on the first re-run of the STP suite that the REJECT lemmas
still failed even after the fix - not because the fix was wrong, but
because the lemmas' own `requires` clauses were manually restating the
OLD two/two-clause postconditions and hadn't picked up the new pinning
clauses automatically. Fixed the lemmas to restate all of each
function's CURRENT ensures clauses (a real, separate small mistake,
caught before reporting success) - re-ran, and the full suite passed:
`44 verified, 0 errors`.

Wrote `run_verify_dafny_stp_suite_renal.py` and
`run_verify_dafny_stp_suite_against_underconstrained_renal.py`,
mirroring `dosage.dfy`'s exact capture-runner pattern; ran both for
real, plus re-ran `run_verify_renal.py` since the main file changed.
All three captures match predictions exactly: main spec exit 0 (5
verified), STP suite exit 0 (44 verified), against-underconstrained
exit 4 (0 verified, 4 errors, preserved as the honest negative result).

Amended `nl_confirmation_renal_adjustment_dfy.md` with the two changed
functions' re-generated, re-cited postconditions, since this touched
functions already presented for Gate C6 sign-off - reported as an
amendment, not a silent edit, per `dosage.dfy`'s own amendment
precedent. 142 tests still passing; the new Dafny files aren't
Python-tested (matching `dosage_stp_suite.dfy`'s own precedent - real
Dafny captures are the evidence, not a pytest wrapper around them).

---

## 2026-07-09 — Scoped Gate C4 (STPs) for renal_adjustment.dfy; two real gaps predicted before building

Asked to plan the next phase after Gate C6. Wrote
`examples/renal_adjustment/gate_c4_stp_plan.md` — a scoping document,
not a build, per this repo's standing "scope first" discipline.

Read all five functions' `ensures` clauses specifically asking whether
each pins its exact output or only bounds/shapes it, before writing any
STP lemma (same hand-derivation discipline the LVR extension used).
Two real, predictable gaps stood out, both the same defect class as
`dosage.dfy`'s own original Gate C4 finding:

- `ComposedCeiling`'s two `<=` bounds don't force the result to equal
  `min(existingCeiling, renalCeiling)` — a wrong candidate value (e.g.
  always returning `0.0`) isn't excluded by the spec as written.
- `AssessRenalFunction` pins which constructor the result uses
  (`EGFRAssessment` vs. `CrClAssessment`, Gate 1c Finding 2's actual
  target) but not the value inside it — a wrong G-stage or wrong
  rounded CrCl value isn't excluded either.

Both are predictions, not yet confirmed by a real Dafny run - recorded
as hypotheses before building, per the LVR extension's own precedent,
so if either turns out wrong that gets reported honestly rather than
silently reconciled. The other three functions (`RoundHalfUp`, `GStage`,
`SelectFormula`) look genuinely tight by inspection - also a prediction,
not yet confirmed. The plan lays out the full per-function STP lemma
table (using the 16-row test-vector table already in `PHASE1_PLAN.md`
for ACCEPT lemmas) and the predicted pinning-clause fixes for the two
gaps, mirroring `ExpectedDose`'s role in `dosage.dfy`'s own fix.

No code changed - `renal_adjustment.dfy` is untouched, this is scoping
only. 142 tests still passing.

---

## 2026-07-09 — Caught and corrected a self-contradictory sourcing overclaim in RoundHalfUp's tie-break rule

Reviewing the Gate C6 sign-off, asked three direct questions: where
REQ-RENAL-3/4/6 live (answer: prose only, not yet Dafny signatures - no
correction needed, already accurately stated); what `RoundHalfUp`'s NL
summary cites as its source for the tie-break rule specifically, not
just the base rounding requirement; and to see Gate 1c Finding 2's text
verbatim (answer: quoted directly from `GATE_1C_AUDIT.md`, no issue
found).

The second question surfaced a real problem. `gate_c1_sketch.md` and
`renal_adjustment.dfy`'s header comment both described round-half-up as
"exactly KDIGO's own convention" in the same paragraph that also said
"KDIGO's cited text says 'rounded to the nearest whole number' with no
even/odd tie-breaking rule stated" — a direct self-contradiction that
had gone unnoticed since these were written. The base rounding
requirement (round to nearest whole number before staging) is genuinely
KDIGO-sourced; the specific tie-break direction (round-half-up vs.
round-half-even) was never sourced to anything and had been dressed in
citation-adjacent language ("clinical dose-staging conventions...
consistently read as round-half-up in practice") that named no actual
authority.

Searched for a real citation rather than just softening the claim.
Found one, and it corrects the assumption rather than rescuing it:
Miller WG, Kaufman HW, Levey AS, et al. "National Kidney Foundation
Laboratory Engagement Working Group Recommendations for Implementing
the CKD-EPI 2021 Race-Free Equations..." *Clinical Chemistry*.
2022;68(4):511-520. PMID 34918062, DOI 10.1093/clinchem/hvab278 -
confirmed via PubMed citation lookup, then fetched directly. States
plainly: "the reported result should be rounded to the closest whole
number based on the rounding logic of a laboratory information system"
- explicitly deferring the tie-break rule to each lab's own software,
confirming there is no single clinical standard for this specific
question at all.

Corrected in place across `sources/kdigo-2024-gfr-staging.md` (dated
amendment, not a silent rewrite), `gate_c1_sketch.md`,
`renal_adjustment.dfy`'s header comment, `PHASE1_PLAN.md`'s
requirements table, `sources/README.md`'s Contents entry,
`KNOWN_LIMITATIONS.md`, and this roadmap doc. No code changed -
`RoundHalfUp`'s body is unchanged (round-half-up remains a reasonable,
defensible design choice) and still verifies: `5 verified, 0 errors`,
re-captured. Only the sourcing claim was wrong, and only because it was
challenged directly rather than re-reviewed by the same process that
wrote it.

---

## 2026-07-08 — Renal-adjustment Gate C6 built; found and fixed two real bugs in shared tooling

Next step in the build order after Gate C1: Gate C6 (NL-dialogue
confirmation), moved earlier per its own recommendation. Attempted to
run `evidence/dafny_nl_summary.py::summarize_method` against
`renal_adjustment.dfy`'s five functions — the infrastructure plan had
predicted this "generalizes for free" since it's parameterized by
`method_name`. Checked empirically rather than trusted, and the
prediction was wrong in one respect.

**Real bug 1:** `_find_method_header` (`evidence/dafny_spec_lint.py`,
shared with `dafny_mutate.py` and `dafny_nl_summary.py`) only matched
Dafny's `method` keyword via `\bmethod\s+`, never `function`.
`renal_adjustment.dfy` is the first spec in this repo consisting
entirely of `function`s — every earlier spec (`dosage.dfy`) paired a
function with a method, and the method was always what got passed to
this extractor, so the function-only case was untested until now. Fixed
by widening the regex to `\b(?:method|function)\s+` in both
`_find_method_header` and the duplicate lookup in
`dafny_mutate.py::_method_header_span`. Two regression tests added
(`test_dafny_nl_summary.py::test_summarizes_a_function_not_just_a_method`,
`test_dafny_spec_lint.py::test_requires_clause_extraction_matches_a_function_not_just_a_method`).

**Real bug 2, found in the same pass:** `_REQ_ID_RE`'s character class
(`[A-Z0-9-]`) excluded lowercase letters, so `REQ-RENAL-1a` (this spec's
own citation for `RoundHalfUp`'s rounding postcondition) was silently
truncated to `REQ-RENAL-1` in generated summaries — a real citation-
accuracy defect misattributing the postcondition to a related but wrong
requirement ID, not a dropped citation that would have been obvious.
`dosage.dfy`'s REQ-IDs (`REQ-GIP-1-4-12`, `REQ-GIP-1-8-1`) never had a
lowercase suffix, so this never fired before. Fixed
(`[A-Za-z0-9-]`), regression-tested.

Also added missing `// REQ-RENAL-*` trailing citations to every
`ensures` clause in `renal_adjustment.dfy` itself (they were absent
entirely, which would have made every postcondition read "no
requirement cited" — understating real traceability, not reflecting an
actual gap) and reformatted `SelectFormula`'s two `ensures` clauses onto
single physical lines each (Gate C6's summarizer only supports
single-line clauses, matching `dosage.dfy`'s own convention — a correct
refusal on the first attempt, not a bug, fixed by reformatting rather
than working around the tool). Re-verified after both changes: `dafny
verify` still `5 verified, 0 errors`; re-captured the real Gate C1
output since the file changed.

Generated and committed the actual sign-off document,
`nl_confirmation_renal_adjustment_dfy.md`, presenting all five
functions' summaries with correct citations. Left the "Decision" section
explicitly pending Steven's confirmation rather than self-signing —
Gate C6's whole purpose is a human check against intent, the same
standard `dosage.dfy`'s own sign-off was held to.

142 tests passing (up from 138 - four new regression tests, two real
bugs fixed).

---

## 2026-07-08 — Renal-adjustment Gate 1 closed under named fallbacks; Phase 2 started

Asked what to suggest for an "easy fallback" so Phase 2 could start
without waiting on Gate 1c's two remaining items. Recommended treating
both as provisional defaults rather than resolved decisions: CrCl/eGFR
computation defaults to caller-supplied for both formulas in Phase 2 v1
(not a design change — `AssessRenalFunction` already takes
`renalFunctionValue: real` as a parameter); classification-flag
provenance (`REQ-RENAL-8`) is reclassified as a Phase 3 integration
concern rather than a Phase 2 blocker, since `SelectFormula`'s flags
were always caller-supplied parameters and the proof doesn't need to
know who populates them. Steven approved ("Ok continue while I keep
digging").

Updated `PHASE1_PLAN.md` and `GATE_1C_AUDIT.md` to record both as named,
dated, reversible defaults — not silently resolved. Gate 1 is now
closed under these two documented assumptions.

**Phase 2 started for real:** wrote `examples/renal_adjustment/renal_adjustment.dfy`,
composing all five functions verified individually during Gate 1c's
audit (`RoundHalfUp`, `GStage`, `SelectFormula`, `ComposedCeiling`,
`AssessRenalFunction`) into one committed file — same bodies as the
scratch checks, verbatim. Verified directly: `dafny verify` reports
`5 verified, 0 errors`. Wrote `run_verify_renal.py`, mirroring
`run_verify_dafny.py`'s capture discipline exactly (verbatim
stdout+stderr, exact command argv, exit code, ISO-8601 timestamp); ran
it for real, producing `raw_dafny_output_renal.txt` and
`run_manifest_dafny_renal.json`. Confirmed
`evidence/dafny_adapter.py::parse_dafny_capture` works unmodified
against this new capture — not assumed from the infrastructure plan's
prediction, actually run: `strength=PROVEN`,
`verifier_completion_status='completed'`. This is the first real,
empirical confirmation that the existing Gate C1/C2 machinery
generalizes to a second spec, the whole point of this POC.

138 tests still passing (no existing code touched); this is the first
commit that adds real, verified Dafny code for the renal-adjustment
POC rather than planning/sketch documents.

---

## 2026-07-08 — Verified Steven's CKD-EPI 2021 research brief; caught one fabricated citation

Steven asked for a precise, portable research prompt to close Gate 1c's
Finding 1 (no function computes the actual CrCl/eGFR numeric value) and
supplied it to an external research tool himself. He returned with a
"research findings" document — explicitly flagged by him as unverified
external knowledge — proposing the exact 2021 CKD-EPI creatinine-only
and creatinine-cystatin C equations, a UK-vs-US practice comparison, a
Cockcroft-Gault 1976 historical derivation, and a Dafny/Z3 lookup-table
architecture strategy.

Verified every checkable claim independently before accepting any of it:

- Both CKD-EPI 2021 equations checked against the National Kidney
  Foundation's own published equations directly (not just the supplied
  document) — matched exactly, all constants confirmed.
- The original 1976 Cockcroft-Gault formula confirmed via PubMed (PMID
  1244564, the correct paper) plus an independent secondary source; the
  88.4/72 unit-conversion arithmetic behind MHRA's rounded 1.23/1.04
  constants checks out.
- **Caught a fabricated citation:** the document claimed NICE NG203
  "Recommendation 1.1.2 mandates the 2009 equation" and "1.1.4 states
  do not use ethnicity to adjust eGFR." Fetched NICE NG203's actual
  recommendations list directly — neither claim is real. The real 1.1.4
  is about not eating meat before a blood test; the real
  ethnicity-related recommendation (1.1.24) is about screening risk
  factors, not equation selection; 1.1.2 doesn't specify an equation
  version at all. An independent, directly on-point 2024 UK study (Roy
  et al., *Nephron*, PMID 39342928, PMC11878410) confirmed the real
  picture: UK lab practice is heterogeneous and in transition (one major
  NHS hospital's own standard result was still MDRD), not settled on any
  single equation — a plausible-sounding but incorrect synthesis, caught
  by fetching the primary source rather than trusting the summary.
- Evaluated the proposed Dafny/Z3 lookup-table architecture on its own
  technical merits: the core diagnosis (Dafny/Z3 can't natively handle
  CKD-EPI's fractional-exponent real power terms — an expressiveness
  gap, not a performance/timeout issue) is correct and reinforces the
  existing recommendation to keep CKD-EPI caller-supplied. But the LUT
  proposal doesn't eliminate the trust boundary, it relocates it — the
  LUT itself would need independent verification against the formula,
  an unaddressed gap in the supplied strategy.

Committed `sources/ckd-epi-2021-and-cockcroft-gault-verification.md`
(full verification record) and folded the confirmed data plus the
corrected UK-practice picture into `PHASE1_PLAN.md`'s Finding 1 entry,
`GATE_1C_AUDIT.md` (addendum), `KNOWN_LIMITATIONS.md`, and this roadmap
doc's status section. Finding 1's actual scope decision (build
Cockcroft-Gault in Phase 2, keep CKD-EPI caller-supplied) remains
Steven's call — not decided here, now backed by verified data instead of
an open question mark. 138 tests still passing; no code touched.

---

## 2026-07-08 — Renal-adjustment Gate 1c Finding 2 resolved by redesign; Finding 1 deferred

Steven's direction: defer Gate 1c's Finding 1 (CrCl/eGFR value
computation scope) and instead design Gate 1b's skeleton to resolve
Finding 2 (the two-downstream-paths gap — `GStage` misapplied to a
Cockcroft-Gault CrCl value), then verify.

Added a dispatcher function, `AssessRenalFunction(formula: Formula,
renalFunctionValue: real): RenalAssessment`, where `RenalAssessment` is
a tagged union (`EGFRAssessment(stage: GStageCategory) |
CrClAssessment(roundedCrClMlPerMin: int)`). This makes the bug Finding 2
described — a KDIGO G-stage label ending up on a raw CrCl number, or
vice versa — a type-level impossibility rather than a convention a
future caller has to remember: `GStage` can only be reached inside the
`EGFRFormula` branch. Verified against the real, installed Dafny 4.11.0
toolchain: 11 verified, 0 errors, including two explicit lemmas
(`EgfrPathNeverProducesCrClAssessment`,
`CrClPathNeverProducesEGFRAssessment`) proving the impossibility
directly rather than relying on the `ensures` clauses' shape alone. The
NHS SPS worked example was re-derived through the new dispatcher and
matches Gate 1c's original hand-trace exactly (eGFR 53 → `G3a`; CrCl
36.9 → rounds to 37).

Folded into `gate_c1_sketch.md` (new section 5), `PHASE1_PLAN.md` (Gate
1b's staging postconditions, "Still open" list — item 3 struck through
and marked resolved), `GATE_1C_AUDIT.md` (dated addendum, not a silent
rewrite of the original findings), `KNOWN_LIMITATIONS.md`, and this
roadmap doc's status section.

**Gate 1 is still not formally closed** — Finding 1 (CrCl/eGFR
computation scope) remains open by explicit choice, and
classification-flag provenance (`REQ-RENAL-8`) is still unscoped. Both
block Phase 2. 138 tests still passing; no code touched (all Dafny
checks were scratch files, not committed artifacts).

---

## 2026-07-08 — Renal-adjustment Gate 1c performed: two real gaps found, Gate 1 not yet closed

Wrote `examples/renal_adjustment/GATE_1C_AUDIT.md`, the hand-trace audit
using the 16-row test-vector table as raw material, per Gate 1c's stated
purpose (catch conceptual gaps at the cheapest possible point, before
any Dafny code exists).

Confirmed total coverage for all four sketched functions, then went
further than a prose argument: wrote the composition
`GStage(RoundHalfUp(x))` as eleven Dafny lemmas (the ten boundary-tie/
just-under pairs plus the NHS SPS eGFR value) and verified them against
the real, installed Dafny 4.11.0 toolchain — 24 verified, 0 errors.
Hand-traced the NHS SPS worked example end to end, including the raw
Cockcroft-Gault arithmetic by hand: `(140-80) x 60 x 1.23 / 120 = 36.9`,
rounds to 37 — matches the published 37 mL/min exactly, cross-checked
with Python before trusting the mental arithmetic.

The audit found two real gaps, not zero — an audit that always finds
nothing is not doing its job:

1. **No function computes the actual CrCl/eGFR numeric value.** The
   skeleton's four functions stage/select/compose an already-computed
   value; nothing calculates it from raw inputs. This fell out silently
   from decomposing the skeleton into separate functions and was never
   an explicit scope decision until this audit surfaced it.
2. **`GStage` is eGFR-specific and must not be applied to a
   Cockcroft-Gault CrCl value** — found concretely while hand-tracing
   NHS SPS: `SelectFormula` correctly picks Cockcroft-Gault (age 80),
   but running its output (37) through `GStage` would report "G3a,"
   an eGFR-scale label on a CrCl-scale number, when the real eGFR (53)
   is what should be staged. The eventual top-level method needs two
   distinct downstream paths, not one unconditional `GStage` call.

Both are named in the audit document and folded into `PHASE1_PLAN.md`'s
"Still open" list, `KNOWN_LIMITATIONS.md`, and the roadmap doc's status
section, with a recommendation (not a decision) on gap 1: build
Cockcroft-Gault's own compute function in Phase 2 (small, fully
specified, low proof risk), treat CKD-EPI eGFR as caller-supplied like
the classification flags (too large a proof undertaking to justify for
this POC's actual purpose). **Gate 1 is not yet formally closed** — per
its own exit criteria, finding and naming real gaps is Gate 1c working
correctly, not a failure to complete it. 138 tests still passing; no
code touched (all Dafny checks were scratch files).

---

## 2026-07-08 — Renal Function Dose Adjustment POC: Gate 1a/1b closed, four proof functions verified against real Dafny

Steven uploaded a "research findings" document proposing to resolve
Phase 1's remaining open items: a BMI-boundary citation (NHS Tayside
ADTC + two ClinicalTrials.gov PK studies), paediatric/cystatin-C
decisions, a 16-row seed test-vector table, a decision that
`SelectFormula`'s drug-classification flags are caller-supplied
(proposed as `REQ-RENAL-7`), and a new `ComposedCeiling` function
resolving `REQ-RENAL-5`'s bound-composition question against
`dosage.dfy`'s actual (checked) signature.

Verified every checkable factual claim independently rather than
accepting the document on its word, per this repo's standing discipline:

- `dosage.dfy`'s quoted signature matched the real file exactly.
- MHRA's BMI threshold ("BMI <18 kg/m2 or >40 kg/m2," strict inequality)
  confirmed by direct WebFetch of the primary MHRA page itself — a
  stronger, simpler citation than the document proposed (NHS Tayside was
  offered as the source; Tayside turned out to be a secondary
  restatement of the same MHRA text, itself confirmed by pulling and
  reading the actual Tayside PDF page image after WebFetch's
  text-summarization pass initially missed the content inside a
  bulleted table graphic — a real tool-reliability gap worth
  remembering). The two ClinicalTrials.gov NCT citations (NCT02942810,
  NCT02039817) checked via the Clinical Trials MCP: both real, both use
  a similar BMI range, but as general PK-study eligibility screening,
  not as validation of MHRA's specific rule — downgraded from "confirms"
  to "corroborates" in the committed record.
- Inker et al.'s 2021 NEJM cystatin-C equation citation (PMID 34554658)
  checked via PubMed: exact title, journal, volume/issue/pages, and DOI
  match.
- `ComposedCeiling`, and (going further than the document itself did)
  `RoundHalfUp`, `GStage`, and `SelectFormula` were each written to a
  scratch `.dfy` file and run through the real, installed Dafny 4.11.0
  toolchain (`dafny verify`) rather than accepted as hand-reasoned
  contract shapes. All four verify cleanly, 1 verified / 0 errors each.

One real conflict caught, not silently merged: the document's proposed
`REQ-RENAL-7` (classification-flag provenance) collided with the
`REQ-RENAL-7` already committed in this repo (BSA de-normalization, from
KDIGO Practice Point 4.2.4, committed before the document arrived).
Renumbered the new one to `REQ-RENAL-8` and recorded the collision and
the fix explicitly in `PHASE1_PLAN.md` rather than overwriting silently.

Folded all of this into `examples/renal_adjustment/PHASE1_PLAN.md`
(closed requirements table through `REQ-RENAL-8`, settled the
paediatric/cystatin-C/rounding decisions, added the 16-row Gate 1c
test-vector table, the verified `ComposedCeiling` interaction contract)
and `examples/renal_adjustment/gate_c1_sketch.md` (all four functions
now marked verified with their checked candidate bodies), plus a new
source file `sources/mhra-renal-formula-selection-2019.md`. Updated
`sources/README.md`, `KNOWN_LIMITATIONS.md`, and this roadmap doc's
status section to match.

**Gate 1c's hand-trace write-up remains the one open item to formally
close Gate 1** — the test-vector table it needs now exists, but the
audit document itself hasn't been written. One new open item,
`REQ-RENAL-8`'s classification-flag provenance (who sets the flags, by
what process), needs its own scoping pass before Phase 2 can start.
138 tests still passing; no code touched (Dafny checks were scratch
files, not committed artifacts).

## 2026-07-08 — Renal Function Dose Adjustment POC: Phase 1 Gate 1a/1b, corrected against primary sources (dab4b29 and this commit)

Steven proposed a second, independent proof-of-concept (renal-function
dose adjustment) as a final POC for submission consideration, uploading
a detailed Phase 1 scoping document. Division of labor: Steven sources
external documents, Claude plans/builds infrastructure.

Verified three concrete unknowns against the actual primary sources
rather than trusting the scoping document's summary:

- MHRA Drug Safety Update (vol. 13, issue 3, Oct 2019): reachable, mostly
  corroborated; one correction — "extremes of muscle mass" is an exact
  BMI <18/>40 threshold, not a fuzzy judgment call.
- NICE NG203: reachable, fully corroborated.
- KDIGO 2024 CKD Guideline: initially blocked (HTTP 403 from this
  environment on both listed URLs). Steven committed the PDF directly to
  the repo (`908dca5`). No PDF-rendering tool was installed here, so a
  stdlib-only (`re`+`zlib`) content-stream text extractor was written to
  recover the text without installing anything. Found: the GFR category
  table confirmed exactly as scoped; a genuinely new nuance — KDIGO's
  Table 11 rounds eGFR to the nearest whole number *before* staging,
  shifting the effective continuous G1/G2 boundary to 89.5, not the
  naive 90.0 (and similarly at every other boundary); partial resolution
  of `REQ-RENAL-3`'s citation gap (obesity/oedema corroborated by KDIGO,
  not MHRA as originally attributed; "unstable renal function" half
  never corroborated by any source, merged into `REQ-RENAL-6` instead);
  and a new candidate requirement, `REQ-RENAL-7`, from Practice Point
  4.2.4 (BSA de-normalization for narrow-therapeutic-index drugs).

Committed `sources/KDIGO-2024-CKD-Guideline.pdf`,
`sources/kdigo-2024-gfr-staging.md` (focused citation-extraction,
following the `req-gip-1-4-12` template rather than a full reformatting,
since only specific sections of a ~200-page guideline are relevant), and
updated `sources/README.md`'s Contents list (`dab4b29`).

This session: wrote `examples/renal_adjustment/PHASE1_PLAN.md`, the
formal Gate 1a/1b document — full corrected requirements table
(`REQ-RENAL-1` through `REQ-RENAL-7`), the Gate 1b spec skeleton
(preconditions, formula-selection proof target, staging/monotonicity/
fail-safe postconditions, `dosage.dfy` interaction contract), and a
decision on the rounding-then-staging design question (accept real-valued
input, prove the rounding step explicitly — not accept pre-rounded
integer input, since the former is more faithful and is exactly what
Gate C4's STPs exist to pin down). Gate 1c (internal consistency audit)
not yet run — blocked on checking Gate 1b against `dosage.dfy`'s actual
precondition structure and on Steven's answers to the still-open
questions (paediatric scope, combined creatinine-cystatin C eGFR, seed
test cases beyond the NHS SPS worked example). Updated
`KNOWN_LIMITATIONS.md` with the per-drug-factors/paediatric/cystatin-C/
REQ-RENAL-3 exclusions. No Dafny code exists yet; Phase 2 remains blocked
on Phase 1 (Gate 1c) closing, per the infrastructure plan already scoped
in `/root/.claude/plans/stateless-weaving-firefly.md`. 138 tests still
passing — no code changed, only source/doc/planning files added.

## 2026-07-07 — Gate C6 next-phase adaptation work: scoped as far as possible, then blocked and asked

Requested directly: "scope out Gate C6's next phase adaptation work."

Checked first whether the trigger condition Steven set at Gate C6
sign-off ("once there is a defensible artifact to build it on top of")
is now met: yes — `dosage.dfy` now carries a full evidence chain (Gate
C1 proof, Gate C4 STP fix, Gate C5's exhaustive mutation testing across
all five operator classes with zero survivors, Gate C6's NL sign-off).

Then tried to scope the actual work the way Gate C5's LVR extension was
scoped (real audit, real prediction, real build order) and could not:
the only description anywhere in the repo is the single sentence
recorded at Gate C6 sign-off, repeated verbatim (never elaborated) in
`nl_confirmation_dosage_dfy.md`, `DEVLOG.md`, `README.md`,
`SYSTEM_BLUEPRINT.md`, and `KNOWN_LIMITATIONS.md`. Grepped the whole
repo, including `PayloadGuard-Evidence-Blueprint-1.md`'s already-cited
FDA premarket-guidance URLs, for anything more specific - found nothing.

Rather than invent a concrete plan from one sentence, wrote the honest
scope this session could reach into
`payloadguard-evidence-roadmap-phaseB-to-C.md`'s new "Gate C6 next-phase
adaptation work" section: the trigger condition is confirmed met, and
three specific unknowns are named as blocking real scoping (what
"adapting the spec" means; what "different downstream software" refers
to; which regulatory pathway - 510(k)/De Novo/PMA/other - this targets).
This mirrors Gate C3 vector 4's own precedent in this exact repo
(specification stripping stayed BLOCKED, named, rather than guessed from
its name alone, since its source material was never available).

`KNOWN_LIMITATIONS.md` gained a pointer row. Asked Steven the three
questions directly, same turn.

## 2026-07-07 — Gate C5 LVR extension built: matched its own prediction exactly

Requested directly: "go" - following through on the scoping session
from the previous entry.

- **`evidence/dafny_mutate.py`**: `generate_lvr_mutants` (+ the
  function-body companion `_generate_function_body_lvr_mutants`).
  `_locate_clause_numeric_literal_sites` finds every `NUM`-kind token in
  a clause and pairs it with its adjacent comparison operator and which
  side it's on (refuses, Tier 1, if a literal is ever found NOT adjacent
  to a comparison - doesn't arise in this repo's real clauses, tested).
  `_locate_function_body_numeric_literal_sites` reuses a new shared
  `_function_body_tokens` helper (factored out of the existing AOR
  function-body locator, so the `//`-comment safety check lives in
  exactly one place for both AOR and LVR).
- **`_lvr_trivial`** generalizes ROR's requires/ensures polarity
  principle from operator-implication (a fixed lookup table) to
  magnitude-implication (a numeric comparison between original and
  mutant literal values): normalizes every comparison to whether
  increasing the literal narrows or widens the constraint, then applies
  the same requires-widens-informative / ensures-narrows-informative
  rule ROR already established. EQ/NE literals have no such
  relationship at all (changing an equality's target is neither a
  superset nor subset of the original in either direction) - always
  sent to verification. Function-body literals have no requires/ensures
  role to apply the principle to at all - sent straight to verification
  unfiltered too, mirroring the AOR function-body precedent.
- **Real run matched the scoping session's hand-derived prediction
  exactly, before verification even confirmed it:** generation alone
  produced 14 raw mutants, 4 filtered (`filtered_magnitude_implied`) -
  matching the predicted count and, checked individually, the predicted
  direction at every one of the 4 sites.
- **Real re-verification: all 10 real-verified candidates genuinely
  killed, zero survivors** - confirmed examples: widening
  `concentrationMgPerMl > 0.0` to `> -0.01` is killed via
  `ExpectedDose`'s own unchanged `requires > 0.0` at the pinning
  clause's call site (a precondition-call violation, not a
  postcondition failure - still a correct, real kill, worth naming
  since it's a different failure shape than most of this repo's other
  kills); both function-body literal mutants (the `< 0.0` threshold and
  the bare `then 0.0` return value) are killed because any mismatch
  between `ExpectedDose`'s mutated definition and the method body's
  unchanged, actual computation breaks the pinning clause for some input
  in the perturbed range.
- **The one named, unresolved tension from scoping** (whether the
  clinical-precision floor is the right test for REQ-GIP-1-8-1's
  exact-zero safety requirement specifically) didn't need resolving to
  get a clean result here - the function-body zero-literal mutant was
  killed at the ±0.01 granularity regardless - but the underlying
  judgment call is still open, not silently closed by this result.
- **Combined final state across all five Gate C5 operator classes: 56
  mutants - 41 killed, 6 filtered_static, 4
  filtered_chain_incompatible, 1 filtered_ar_group_incompatible, 4
  filtered_magnitude_implied - zero survived, zero unclassifiable.**
- **Tests:** `tests/test_dafny_mutate.py` grew from 19 to 25 (literal-
  site location with correct operand/side tracking on the real spec, a
  refusal test for a hypothetical non-adjacent literal, function-body
  literal-site location, a direct unit test of `_lvr_trivial` against
  hand-derived cases independent of the real spec, a check that the
  generation-time half of the prediction matches, a byte-level check on
  the targeted-literal splice). `tests/test_mutation_report.py` grew
  from 7 to 8 (locks in the real-verification half of the prediction -
  all 10 real-verified LVR candidates killed - against the committed
  capture). Full suite: **138 passed** (131 prior + 7 new). No leftover
  temp files (verified).
- Full documentation set updated to match (`KNOWN_LIMITATIONS.md`,
  `SYSTEM_BLUEPRINT.md`, the roadmap doc, this entry, README.md, the
  example's own README). `generate_artifacts.py` re-run as a sanity
  check: no observable change beyond timestamps, as expected.

## 2026-07-07 — Gate C5 LVR extension scoped (not built)

Requested directly: "scope out Gate C5's LVR extension." Full sub-plan
written into `payloadguard-evidence-roadmap-phaseB-to-C.md`, mirroring
the discipline used for Gate C5's own original scoping session and its
chain-direction/function-body-AOR extension.

- **Literal-site audit, checked empirically, not assumed:** ran the real
  tokenizer against `dosage.dfy` to enumerate every numeric literal in
  scope (5 in `CalculateHourlyDose`'s requires/ensures clauses, 2 in
  `ExpectedDose`'s function body). All 7 are exactly `0.0` — no other
  numeric constant exists anywhere in this spec.
- **Value-selection strategy:** exactly `original ± 0.01` per site (the
  clinical-precision floor sourced in the prior research session) —
  this is the first place that guidance has an actual application,
  since it was named as bounding literal/constant perturbation
  specifically, a mutation class Gate C5 hadn't built until now.
- **Static filter, reusing ROR's polarity principle:** generalized from
  operator-implication (a fixed lookup table) to magnitude-implication
  (numeric comparison between original and mutant literal values) for
  LE/LT/GE/GT-adjacent sites. Two real design points named rather than
  glossed over: EQ-literal mutation has no such filter at all (changing
  an equality target is neither a superset nor subset of the original in
  either direction); function-body literals (2 of the 7 sites) have no
  requires/ensures role to apply the principle to, so v1 would send them
  straight to real verification unfiltered, mirroring the AOR
  function-body precedent.
- **Predicted outcome recorded as a hypothesis, not a promise:** 14 raw
  mutants, 4 filtered as statically trivial, 10 sent to real
  verification, all 10 hand-predicted killed (worked through by hand for
  each site, e.g. why widening a requires clause's `> 0.0` to `> -0.01`
  should fail via `ExpectedDose`'s own unchanged precondition at the
  pinning clause's call site) — explicit that disagreement with this
  prediction at build time would itself be the finding worth reporting.
- **One named, unresolved tension:** whether the clinical-precision
  floor (sourced from dosage-*threshold* rounding practice) is the right
  test for REQ-GIP-1-8-1's *exact-zero* safety requirement specifically
  — a regulator could reasonably view any nonzero delivery on reverse
  flow as a real hazard, not clinically negligible noise. Left as an
  open judgment call for whoever builds this, not decided here.
- Reuses all existing extraction machinery
  (`_locate_clause_sites`/`_tokenize_with_spans`/`_find_function_body_span`/
  `check_precondition_satisfiability`) — the build order only needs a new
  filter rule and a new `LVR` operator label, no new extraction code.

Not built. `KNOWN_LIMITATIONS.md` gained a SCOPED table row pointing to
the full sub-plan.

## 2026-07-07 — Gate C5 extended: chain-direction-aware ROR + function-body AOR

Requested directly: "build both" - the two follow-ups named at the end
of the previous entry's research findings.

- **Chain-direction-aware ROR.** New helpers in `evidence/dafny_mutate.py`:
  `_chain_group_ids` partitions a clause's tokens into groups that never
  cross a boolean-connective or parenthesis boundary (a conservative,
  tested approximation of Dafny's actual chain-scoping rule);
  `_chain_incompatible` checks whether a candidate operator would mix an
  ascending relation with a descending one against its chain siblings
  (`==`/`!=` always compatible). Wired into `_generate_token_mutants` via
  a new `chain_aware` parameter, used only by `generate_ror_mutants`
  (`&&`/`||`/arithmetic have no analogous rule). Result: the 4 mutants
  that used to reach real Dafny invocation and come back
  `unclassifiable` are now filtered before generation ever reaches
  verification - a new `filtered_chain_incompatible` outcome, kept
  distinct from pass 1's `filtered_static` since the reason (syntactic
  invalidity vs. semantic redundancy) is genuinely different.
- **Function-body AOR, MutDafny-restricted.** `generate_aor_mutants`
  gained an optional `function_name` parameter. New helpers:
  `_find_function_body_span` (brace-matched, mirroring
  `dafny_spec_lint._find_method_header`'s depth-tracking but returning
  the body content, not the header); `_locate_function_body_arithmetic_sites`
  (refuses outright - rather than risk a misaligned offset - if the body
  contains a `//` comment; none does today, checked).
  `_TOKEN_SPAN_RE` gained `ASSIGN` (`:=`) and `SEMI` (`;`) token kinds,
  needed for body statements but never present in requires/ensures
  clauses. `_ar_group_incompatible` applies MutDafny's own restriction
  directly: `+`/`-`/`*` freely interchange, `/` only with `%` (absent
  from this spec) - a mutation can never introduce `/` where the
  original had none, closing the division-by-zero false-kill risk by
  construction. `generate_mutants` gained the same parameter; the real
  caller (`run_mutation_suite.py`) now passes `"ExpectedDose"`.
- **Real re-run, both extensions active: 42 mutants - 31 killed, 6
  filtered_static, 4 filtered_chain_incompatible, 1
  filtered_ar_group_incompatible, zero survived, zero unclassifiable.**
  The 2 new function-body mutants (`* -> +`, `* -> -`) are both
  genuinely killed - confirming `*` is load-bearing, since the method
  body's own unmutated computation then diverges from the mutated
  `ExpectedDose`'s pinning clause. No leftover temp files (verified).
- **Tests:** `tests/test_dafny_mutate.py` grew from 11 to 19 - new
  chain-direction filtering test on the real spec, direct unit tests of
  `_chain_incompatible`/`_ar_group_incompatible` against hand-derived
  cases independent of the real spec, function-body AOR generation and
  its division-free restriction, a tokenizer test for `:=`/`;`, and a
  direct test that `_locate_function_body_arithmetic_sites` finds
  exactly the one `*`. `tests/test_mutation_report.py` grew from 5 to 7
  - replaced the "4 unclassifiable, all chain-direction" regression with
  "zero survivors AND zero unclassifiable," added a direct check on the
  function-body AOR outcomes. Full suite: **131 passed** (121 prior +
  10 new).
- Full documentation set updated to match (`KNOWN_LIMITATIONS.md`,
  `SYSTEM_BLUEPRINT.md`, the roadmap doc, this entry, README.md, the
  example's own README, and the research-findings doc itself - both
  follow-ups marked BUILT rather than not-yet-built).
  `generate_artifacts.py` re-run as a sanity check: no observable change
  beyond timestamps, as expected (Gate C5 still isn't wired into the
  matrix pipeline).

## 2026-07-07 — Gate C5 research findings recorded; one mischaracterization corrected

Steven sent the external research prompt drafted earlier this session
(`gate-c5-research-prompt.md`) out and brought back a thorough,
well-sourced response covering the three open Gate C5 questions.
Recorded in full at
`examples/dosage_calculator/gate_c5_mutation_testing_research_findings.md`.

- **Correction made:** Gate C5 was labeled "MutDafny/IronSpec-style" in
  `evidence/dafny_mutate.py`'s module docstring and the roadmap doc. The
  research found this wrong - IronSpec's actual mutation-testing
  technique (Goldweber et al., OSDI'24) is a directional,
  implication-lemma-based approach (`S'(p) ⟹ S(p)`), not the brute
  verify/observe approach this module actually implements, which
  matches MutDafny (Amaral, Mendes & Campos, 2025) instead. Corrected
  the docstring and the roadmap doc's separate, also-unconfirmed
  "IronSpec's three-pass framework" attribution for the filter pipeline.
  Gate C4's own IronSpec attribution (Spec-Testing Proofs) is a
  different, correct part of IronSpec's toolkit and is unaffected.
- **Problem A (the `>=` survivor, already fixed last entry) got a name
  and real precedent:** *masking*, the MC/DC term (DO-178B/C,
  Chilenski 1994) for a sibling condition making a boundary's operator
  choice unobservable - an FAA/DO-178C-accepted pattern in the adjacent
  aerospace safety-critical field. Recorded for the historical record;
  Steven's tightening decision already resolved the underlying finding
  before this research came back.
- **Problem B (chain-direction stillborn mutants) confirmed as expected,
  not a gap:** Dafny's chaining rule is now citable directly from the
  Reference Manual (§5.2.1-5.2.2) rather than only empirically observed;
  `run_mutation_suite.py`'s comment updated to cite it.
  `dafny_mutate.py`'s `unclassifiable` bucketing strategy was
  independently confirmed to match MutDafny's own published `Invalid`-
  mutant handling - not behind the state of the art. A genuine,
  not-yet-built improvement was identified (restrict each chain link's
  mutation candidates to direction-compatible operators, eliminating
  the 4 unclassifiable mutants by construction - MutDafny itself doesn't
  do this).
- **Problem C (deferred AOR/floating-point precision) got a concrete
  plan, not just deferred:** MutDafny's own `/`↔`%`-only AOR restriction
  directly resolves the division-by-zero attribution risk named when
  AOR was originally deferred; a sourced ≥0.01 mL/hr clinical-precision
  floor (pharmacy/nursing device-rounding practice, not a formal
  regulatory standard - the research is explicit about that distinction)
  gives a concrete cutoff for real-valued mutant magnitude, whenever
  that work is picked up.
- No code changes beyond the docstring/comment corrections named above;
  no rebuild triggered by this research since the one thing it bore on
  directly (the Problem A survivor) was already fixed in the prior
  entry. Full suite unaffected: **121 passed**, unchanged.

## 2026-07-07 — Gate C5 survivors fixed: REQ-GIP-1-8-1 tightened to `>`

Requested directly, following an out-of-band status message that
falsely claimed the repo was in an early, mostly-empty state (no Phase
B, DEVLOG last dated 2026-07-04) - verified directly against git (local
`main` matched `origin/main` exactly at the real HEAD) and file content
(README/DEVLOG both showed the real, current state) before responding;
flagged the discrepancy rather than acting on it. The user's actual
prior request - interrupted mid-response before this - was "go ahead and
tighten REQ-GIP-1-8-1 to >"; confirmed and executed once the false
status claim was cleared up.

- **`dosage.dfy`:** `ensures infusionRateMlPerHr >= 0.0 || dose == 0.0`
  → `ensures infusionRateMlPerHr > 0.0 || dose == 0.0`. Header comment
  gained an inline note (alongside the existing Gate C4 fix note)
  explaining the Gate C5 finding and fix. Re-verified clean: `2
  verified, 0 errors`, unchanged from before the tightening.
- **STP suites re-verified for real, not assumed unaffected:**
  `dosage_stp_suite.dfy` (includes the changed `dosage.dfy`) still
  verifies clean, `10 verified, 0 errors`, unchanged.
  `dosage_stp_suite_against_underconstrained.dfy` (includes the
  untouched, preserved `dosage_underconstrained.dfy`) still correctly
  fails, `0 verified, 2 errors`, unchanged - both re-captured via their
  existing runner scripts; only the manifests' timestamps changed.
- **Mutation suite re-run in full** (`run_mutation_suite.py`, real
  Dafny invocations, ~45s): **zero survivors remain.** The two former
  survivor mutations (`> -> >=`, `> -> !=`, previously `>= -> !=`,
  `>= -> >`) are now correctly recognized by the pass-1 static filter as
  trivially uninteresting *before* Dafny is even invoked - a proof of
  `x > 0` universally implies both `x >= 0` and `x != 0` - which is
  itself a clean, mechanical confirmation that the boundary is now
  tight, not just an assertion. New counts: killed=29 (unchanged),
  filtered_static=6 (up from 4), unclassifiable=4 (unchanged, unrelated
  chain-direction parse-error gap), survived=0 (down from 2).
  `mutation_report.json`/`.md` and `run_manifest_mutation.json`
  regenerated to reflect the real re-run.
- **Gate C6 sign-off amended, not overwritten:** the original
  2026-07-07 sign-off record
  (`examples/dosage_calculator/nl_confirmation_dosage_dfy.md`) stays
  intact as history; a new "Amendment" section records the Gate C5
  finding, Steven's tightening decision, the regenerated plain-English
  summary (only postcondition 3's gloss changed, `is at least` → `is
  greater than`), and treats it as re-confirmed on the same basis as the
  original sign-off.
- **Tests updated to match the new real reality, not just made to
  pass:** `tests/test_dafny_nl_summary.py` (the reverse-flow-clause
  citation test now matches on `> 0.0`), `tests/test_dafny_mutate.py`
  (filtered-mutant count 4→6, LOR's expected mutated clause text,
  renamed/expanded the equality-clause-filter test to also cover the
  now-tightened reverse-flow clause's own filtered mutations),
  `tests/test_mutation_report.py` (replaced the "2 named survivors"
  regression test with a "zero survivors, and the two former survivor
  mutations are now filtered_static" regression test - so a future
  regeneration can't let a survivor quietly reappear without a test
  failing). Full suite: **121 passed**, same count as before (no tests
  added or removed, only updated).
- Full documentation set updated to match (`KNOWN_LIMITATIONS.md`,
  `SYSTEM_BLUEPRINT.md`, the roadmap doc, this entry, README.md, the
  example's own README). `generate_artifacts.py` re-run as a sanity
  check: no observable change beyond timestamps, as expected (Gate C5
  still isn't wired into the matrix pipeline).

## 2026-07-07 — Gate C5: built for v1 scope, 2 real survivors found

Requested directly, same day as the scoping session: "build it and be
careful with Dafny. just. we can consider floating points later..it's a
known but solvable issue." Read as: build the core (ROR/LOR/COI on
requires/ensures clauses) now, defer the AOR/division-by-zero risk named
in the scoping doc. A later message added guidance for that follow-up:
"we can consider bounding floating points within the terms of accuracy.
if we're dealing with an integer 1*10^10, then we don't have to be any
more accurate that accuracy requires" — recorded, not acted on in this
build.

- **`evidence/dafny_mutate.py`** — `generate_ror/lor/aor/coi_mutants()` +
  `generate_mutants()`. Reuses `dafny_nl_summary._CLAUSE_LINE_RE` (Gate
  C6's single-line clause convention) and `dafny_spec_lint._find_method_header`.
  A local span-preserving tokenizer extends `dafny_spec_lint`'s token
  grammar with one addition (a COMMA token, needed for the pinning
  clause's `ExpectedDose(a, b, c)` function-call syntax) - safe here
  specifically because mutation only relocates operator TEXT, it never
  needs to understand what an expression means the way Z3 translation
  does, so tolerating syntax the Z3 translator correctly refuses can't
  mistranslate anything.
- **Pass-1 static filter, the design point most likely to be silently
  wrong in one direction:** a mutant is skipped when a fixed relational-
  implication table proves it's guaranteed uninteresting - but the
  trivial DIRECTION flips by clause role. Weakening is trivial for
  `ensures` (whatever satisfies the original satisfies a logically
  weaker consequence too); *strengthening* is trivial for `requires`
  (the original proof still applies under a narrower hypothesis) - the
  informative direction for `requires` is weakening it. Verified against
  a synthetic spec independent of `dosage.dfy`'s specific content
  (`test_ror_polarity_flips_between_requires_and_ensures`), since this
  is the one place getting the direction backwards would silently filter
  out exactly the mutants worth testing.
- **Passes 2-3 reused directly, as scoped:** pass 2 (vacuity filtering
  for `requires` mutants) calls `dafny_spec_lint.check_precondition_satisfiability`
  against the mutated source with no new Z3 code. Pass 3
  (`examples/dosage_calculator/run_mutation_suite.py`) mirrors
  `run_verify_dafny.py`'s capture discipline and reuses `dafny_adapter`'s
  `_SUMMARY_RE`/`_INCOMPLETE_MARKERS` per mutant.
- **Real run: 39 mutants against `dosage.dfy::CalculateHourlyDose`** - 29
  killed, 4 filtered as statically trivial, **2 survived**, **4
  unclassifiable**. Mutant `.dfy` files are not committed individually
  (mechanically derived, unlike the STP suites' hand-authored artifacts);
  the real per-mutant outcome is `mutation_report.json`/`.md` +
  `run_manifest_mutation.json`.
- **The 2 survivors - a real finding, reported not silently fixed.**
  `infusionRateMlPerHr >= 0.0 || dose == 0.0` with the first disjunct's
  `>=` mutated to `!=` or `>` both still verify (`2 verified, 0 errors`,
  confirmed by direct re-run). Root cause worked out and checked: at
  `infusionRateMlPerHr == 0.0` exactly, real multiplication makes
  `rawDose == 0.0` exactly, so `dose == 0.0` already holds at that
  boundary independent of the first disjunct's operator - a real
  looseness in REQ-GIP-1-8-1's postcondition. **`dosage.dfy` is the spec
  Steven signed off on in Gate C6 the same day** - this finding is
  reported for his decision (tighten vs. accept-and-document), not
  unilaterally changed.
- **The 4 unclassifiable results - a real mutation-engine gap, not a
  spec finding.** All 4 come from mutating one side of the chained
  `0.0 <= dose <= maxSafeDoseMgPerHr` clause to a descending operator
  (e.g. `0.0 >= dose <= maxSafeDoseMgPerHr`); confirmed by direct re-run
  that Dafny's own PARSER rejects this (`this operator chain cannot
  continue with an ascending/descending operator`, exit code 2) - a real
  Dafny language rule the engine doesn't yet model. Correctly refused
  (Tier 1) rather than misclassified: `_classify` only accepts exit
  codes 0/4, relays Dafny's own error line (temp filename scrubbed for
  report determinism) as detail. Named as a real, scoped follow-up, not
  fixed in this pass.
- **AOR/SOR/HOR out of v1 scope, checked not assumed.** SOR/HOR aren't
  implemented at all - `test_sor_and_hor_not_applicable_confirmed_by_absence_of_syntax`
  greps `dosage.dfy` for set/heap syntax and asserts none present. AOR
  is implemented and exercised (asserted `== []` against the real spec,
  not just left untested) - its one site lives in `ExpectedDose`'s
  function body, out of clause-mutation scope, deferred with the
  division-by-zero risk per the guidance above.
- **Tests:** `tests/test_dafny_mutate.py` (11, pure generation/filter
  logic, no Dafny invocations) + `tests/test_mutation_report.py` (5,
  validates the committed real capture rather than re-running 39 Dafny
  invocations per test pass - the two survivors and four unclassifiable
  entries are pinned by exact description so a regeneration can't
  silently lose or gain one). Full suite: **121 passed** (105 prior +
  16 new).

## 2026-07-07 — Gate C5: mutation testing, scoped (not built)

Requested directly: "scope out C5 please."

Per this repo's build discipline (Gate 2's CONFLICT rule, Gate C4's STPs)
a piece this size gets a written sub-plan and explicit go-ahead before
code — the roadmap's own original note already called Gate C5 "the
largest single piece" and recommended treating it as its own multi-step
sub-plan. Full sub-plan written into
`payloadguard-evidence-roadmap-phaseB-to-C.md`'s Gate C5 section,
replacing the prior one-paragraph sketch. Key content:

- **Operator applicability audited against the real spec**, not assumed
  generically: ROR (~8 comparison sites) and AOR (the single `*`) apply
  directly; LOR applies to exactly one explicit `||`
  (`infusionRateMlPerHr >= 0.0 || dose == 0.0`); COI applies to all 3
  `ensures` clauses via a negate-and-reverify check (a coarser "does this
  clause constrain anything at all" question, distinct from the other
  four's "is this specific boundary load-bearing"). SOR and HOR are
  explicitly NOT APPLICABLE — `dosage.dfy` has no sets and no heap state
  anywhere — named as a checked exclusion (same treatment as REQ-DOSE-003's
  exclusion from this same spec), not silently skipped.
- **A named risk:** AOR's `/` mutant may fail verification for an
  unrelated reason (Dafny's own division-by-zero check, confirmed real
  during Gate C1) rather than because the postcondition caught the
  weakening — the harness must attribute *why* a mutant failed, not just
  pattern-match "verification failed" as a correct kill, or it risks
  reporting a false-confidence finding.
- **Architecture reuses existing infrastructure** rather than building
  fresh: `dafny_spec_lint.py`'s tokenizer/parser as the mutation target
  grammar (needs a small, named, span-preserving extension - the existing
  tokenizer discards character positions since it only ever needed to
  build Z3 expressions, not reconstruct source text);
  `check_precondition_satisfiability` reused directly for IronSpec's pass
  2 (vacuity filtering); re-verification (pass 3) mirrors
  `run_verify_dafny.py`'s capture pattern and `dafny_adapter.py`'s
  false-zero-guarded parser.
- **Six-step build order specified**, ending in a committed report
  enumerating every mutant, its operator class, target clause, and
  outcome — same "real capture, not smoothed over" discipline as the STP
  suites.

Not built. `KNOWN_LIMITATIONS.md` gained a SCOPED table row pointing to
the full sub-plan.

## 2026-07-07 — Gate C6: NL-dialogue confirmation, built and signed off

Requested directly: "gate C6 first please" (choosing it over Gate C5,
which was not requested).

- **Built.** `evidence/dafny_nl_summary.py::summarize_method(source,
  method_name)` — deliberately not a natural-language generator. Extracts
  each requires/ensures clause verbatim (ground truth) plus any `REQ-ID`
  cited in a trailing `//` comment, exactly as authored, alongside a
  best-effort English gloss via a small fixed operator-substitution table
  (`&&`/`||`/`==>`/`<==>`/comparisons → words) — explicitly a template,
  not comprehension; the raw clause is always shown first. Reuses
  `evidence/dafny_spec_lint.py`'s Gate C3 parsing surface
  (`_find_method_header`, `_parse_params`, `extract_requires_clauses`,
  `extract_ensures_clauses`) rather than reimplementing Dafny parsing.
  Citation extraction needed a separate, comment-preserving line-based
  scan (`_extract_annotated_clauses`), since the existing extractors
  strip comments before this module sees the text.
- **Scope boundary, checked not assumed.** Only single-line clauses are
  supported. `summarize_method()` cross-checks its own line-based
  extraction against `dafny_spec_lint`'s canonical, multi-line-capable
  extractor and refuses (`SystemExit`, Tier 1) on any mismatch.
- **Self-caught bug.** The first draft of that refusal check compared
  clause *counts*, not content. Manual testing against a synthetic
  multi-line `requires x > 0\n  && x < 100` clause found it didn't raise —
  both extractors returned the same count (1) even though the line-based
  scan had silently truncated to just `x > 0`, dropping the continuation,
  while the canonical extractor correctly joined the whole clause. Same
  count, silently wrong content. Fixed by comparing whitespace-normalized
  clause text instead of counts; caught and corrected before the test
  suite was even written, matching this repo's "verify empirically,
  don't assume" discipline (e.g. Gate C4's self-caught 500.0-vs-50.0
  wrong-value mistake).
- **Tests.** 7 new tests in `tests/test_dafny_nl_summary.py`: real
  `dosage.dfy` parameters/preconditions listed correctly; each
  postcondition cites the right requirement, or explicitly "no
  requirement cited" for the pinning clause (the load-bearing property —
  a wrong citation is the exact defect class this gate exists to catch);
  operator gloss; the multi-line refusal regression; a no-clauses method
  still summarizes; output is byte-identical across repeated calls. Full
  suite: **105 passed** (98 prior + 7 new).
- **The sign-off itself — the gate's actual deliverable.** The generated
  summary for `dosage.dfy::CalculateHourlyDose` was presented; the
  `AskUserQuestion` tool failed with a stream error (this session turned
  out to be non-interactive), so the question was asked as plain text
  instead. Steven replied via a separate screenshot: "it's good for the
  spec as is," confirming the summary matches intent, and flagged a
  next-phase item (adapting the spec and explaining, for a regulatory
  submission, how results get analyzed by downstream software) as
  separate follow-up work, explicitly scoped out until "a defensible
  artifact" exists. Recorded in
  `examples/dosage_calculator/nl_confirmation_dosage_dfy.md`, mirroring
  `sources/req-gip-1-4-12-alarm-scope-decision.md`'s pattern.
- **Explicitly not done.** Not wired into `build_matrix()` or any
  generator — matches the roadmap's own framing of Gate C6 as a process
  habit, not an automated check. The next-phase adaptation/regulatory-
  analysis work Steven flagged is not started.

Commits: `b6a5810` (generator + tests, pushed before sign-off arrived,
since the code itself was fully verified and didn't need to wait on the
human decision it feeds).

## 2026-07-07 — Gate 2/C2-C4 wiring extended to variants A and B

Requested directly, same day as the variant-C-only wiring: "go ahead and
extend variant A and B now."

- **Declarations.** `metadata.a.yaml` gained `- method: dafny,
  spec_target: "dosage.dfy", dafny_method: "CalculateHourlyDose"` in
  REQ-GIP-1-4-12/REQ-GIP-1-8-1's `evidence` lists - the same declaration
  style Gate 4/5 already established. `evidence/schema/metadata.schema.a.json`
  gained the matching `dafny` enum value + `spec_target`/`dafny_method`
  conditional (identical fix to schema.c.json's). `metadata.b.yaml`
  gained two new shadow pseudo-requirements, `REQ-GIP-1-4-12.formal-1`
  and `REQ-GIP-1-8-1.formal-1`, `implementation: "dosage.dfy::CalculateHourlyDose"`
  - the same shadow pattern concrete evidence uses, distinguished as a
  dafny shadow by the `.dfy` file extension, no new declared field.
  `evidence/schema/metadata.schema.b.json`'s shadow-id pattern extended
  from `\.concrete-[0-9]+` to `\.(concrete|formal)-[0-9]+` to allow it.
- **Binders.** `_bind_declared` (A) and `_bind_shadow` (B) both gained
  an optional `dafny_store` parameter - but unlike variant C's
  symbolic/concrete sub-views, a requirement declaring dafny evidence
  with no `dafny_store` provided at all is refused outright
  (`SystemExit`), not silently skipped: A/B have no "legitimately
  excludes dafny" concept, since their single artifact renders every
  declared evidence type together. `_bind_shadow` distinguishes a dafny
  shadow from a concrete one by checking whether the implementation
  file ends in `.dfy`. `_shape_flattened_shadow` gained the same
  `verifier_completion_status` field `_shape_method_partitioned` already
  carried, load-bearing for ruling R3's row-level check.
- **CONFLICT Type 1 generalized, and a real bug fixed along the way.**
  `_declared_concrete_bindings` previously treated every shadow row's
  implementation suffix as a concrete test_id unconditionally - a dafny
  shadow's `dafny_method` would have been mis-parsed as a bogus test_id
  and crashed with a false "declared test_id not found" error. Fixed to
  skip `.dfy`-suffixed shadow rows. A new `_declared_dafny_bindings`
  generator unifies dafny's two declaration shapes (A/C's evidence list,
  B's `.dfy` shadow rows) the same way concrete evidence's own generator
  already does; `dafny_binding_conflicts` was rewritten to use it.
- **Intent parity required extending dafny_store beyond "c-formal".**
  `generate_matrix_c.py` now passes `dafny_store` to ALL THREE of its
  `build_matrix()` calls, not just `"c-formal"` - `derive_intent()` runs
  inside each call using that call's own bound records, so
  `c-symbolic`/`c-concrete` would otherwise keep computing
  `intent_ok = False` for the two now-proven requirements while A/B/
  formal say `True`, genuinely breaking the fact-equality gate. Their
  RENDERED rows are unaffected either way - only internal intent
  computation changes. Only `"c-formal"`'s header advertises the dafny
  tool version.
- **The fact-equality gate required two real changes.**
  `evidence/reconcile.py::VARIANT_ARTIFACTS` now includes
  `traceability_matrix.formal.json` as a full fifth member.
  `facts_c` is now the union of symbolic, concrete, AND formal. The
  intent comparison changed from strict dict equality to **subset
  comparison**: `formal.json` will *permanently* lack an opinion about
  REQ-DOSE-003 (`dosage.dfy`'s own header comment explicitly excludes
  it - a durable scope boundary, not a temporary gap), so requiring
  identical dicts was never going to hold once C was folded in for
  real. New rule: every requirement a view has an opinion about must
  match the reference exactly; a view may have no opinion about a
  requirement it doesn't cover; a completely unknown requirement id is
  still a hard failure (in practice caught even earlier, by the facts
  check). The temporary `run_formal_check`/`KNOWN_FORMAL_INTENT_DIVERGENCE`
  carve-out built for the C-only phase is retired - deleted from
  `evidence/reconcile.py`, its call removed from `regenerate_all.py`.
- **The CLI needed `--dafny-captures`, and this was not optional.** Once
  metadata.a.yaml/b.yaml declared dafny evidence,
  `python -m evidence.cli build --variant a ...` genuinely broke - a
  real regression this extension would otherwise have introduced.
  `evidence/cli.py` gained `--dafny-captures <index.json>`: a small JSON
  file mapping `"{spec_target}::{dafny_method}"` keys to *paths*
  (relative to the index file's own directory), not inlined file
  content - keeps the index small and hand-readable.
  `examples/dosage_calculator/dafny_captures_index.json` is the real,
  committed index. `"c-formal"` was also added to the CLI's variant
  choices (deferred in the C-only build, needed now).
- **The result:** every variant artifact - A, B, C-symbolic, C-concrete,
  C-formal - now reports `intent_ok: true` for both REQ-GIP-1-4-12 and
  REQ-GIP-1-8-1. `run_gate()`'s facts count is **9**, not 7.
- **Tests:** `tests/test_dafny_wiring.py` rewritten substantially (real
  A/B PROVEN records checked directly; the full fact-equality gate
  checked to pass with intent True everywhere; the subset-vs-strict-
  equality fix exercised directly with both a legitimate-absence case
  and a real-mismatch case; CLI `--dafny-captures` round-trips for a/b
  and the CLI's refusal without it confirmed real, not hypothetical).
  `tests/test_cli.py` and `tests/test_fact_equality.py` updated for the
  new committed reality (5 CLI variants now, including "c-formal"; facts
  9 not 7; intent True not False). Full suite: **98 passed**. Full
  `generate_artifacts.py` pipeline re-run end to end: PASS.
- **Docs:** `examples/dosage_calculator/README.md` gained a 2026-07-07
  amendment (the prior claim that Dafny "is not wired in this phase" was
  specific to the frozen base matrix, which is still accurate and
  unchanged - clarified rather than deleted); `RECONCILIATION.md` gained
  a pointer note that its historical facts/intent figures (7 facts,
  REQ-GIP-1-4-12/1-8-1 false) describe the Phase A/B state, preserved
  unedited as the record of what ruling R1 verified at the time.

## 2026-07-07 — Gate 2/C2-C4 wiring: first real Dafny-sourced PROVEN row ever rendered

Requested directly: "we need z3 integration and invocation in order to
reach PROVEN status, in concurrence with gate 5 extension." The single
highest-stakes change to this repository's structural guarantees since
ruling R1 - the first time PROVEN would ever appear in a live rendered
row, something R1->R2->R2c->R3 has guarded since Phase A. Three design
decisions were confirmed with Steven before building, not guessed at:

- **Scope: variant C only, for now.** "hmm. can we post hoc verify A and
  B after C variant is proven?" - variants A and B are deliberately,
  explicitly deferred. This creates a real, temporary cross-variant
  intent divergence, named and tracked below, not silently permitted.
- **The Z3 gate lives inside the binder itself** (`dafny_record()`),
  mirroring how `symbolic_record`/`concrete_record` already refuse on
  failed captures internally - not a separate pipeline stage.
- **Metadata declares the dafny evidence explicitly**
  (`evidence: [{method: dafny, spec_target: ..., dafny_method: ...}]`),
  consistent with Gate 4/5's existing declaration pattern, cross-checked
  by a new Gate 2 CONFLICT Type 1 sub-check rather than bound
  unconditionally.

**What was built:**

- **`evidence/schema/metadata.schema.c.json`** - `method: dafny` added
  to the evidence enum, requiring `spec_target`/`dafny_method` together
  via a new `allOf` conditional (alongside the existing `concrete_test`/
  `test_id` one).
- **`examples/dosage_calculator/metadata.c.yaml`** - `evidence:
  [{method: dafny, spec_target: "dosage.dfy", dafny_method:
  "CalculateHourlyDose"}]` added to REQ-GIP-1-4-12 and REQ-GIP-1-8-1 -
  exactly the two requirements `intended_method: "PROVEN"` has named
  since Phase A/B, and exactly the two `dosage.dfy`'s own header comment
  scopes itself to.
- **`evidence/conflict.py::dafny_binding_conflicts`** - the new Type 1
  identity check: does the declared `spec_target` match the file the
  captured Dafny manifest actually verified? Deliberately a no-op when
  `dafny_store is None` (not merely falsy) - the symbolic/concrete
  variant-C sub-views, which never intend to bind dafny evidence, must
  not be penalized for metadata that also declares it for the third
  view. `run_conflict_gate` gained an optional `dafny_store` parameter.
- **`evidence/render/matrix_variants.py::dafny_record()`** - the wiring
  itself. Gates PROVEN on two independent, real checks before ever
  constructing a record: (1) Z3 precondition satisfiability
  (`evidence.dafny_spec_lint.check_precondition_satisfiability`, Gate
  C3) - refuses if unsat; (2) `parse_dafny_capture` (Gate C1) - refuses
  on any non-clean signal, already covering false-zero and the Gate C3
  vector 3 hardening. `assert_no_realized_proven`'s ruling R3 still
  independently re-checks `method`/`verifier_completion_status` at the
  matrix boundary regardless - this function satisfying both today
  doesn't change that.
- **`_bind_self_describing`** gained an optional `dafny_store` parameter:
  `None` means "this call doesn't bind dafny evidence at all" (declared
  entries silently ignored), vs. an explicit dict (even empty) meaning
  "this call does bind dafny evidence, and an unresolved declared entry
  is a real refusal." This `is not None` vs. truthiness distinction is
  what keeps `c-symbolic`/`c-concrete` behaviorally unchanged (aside from
  one new, always-null `verifier_completion_status` field added to every
  variant-C row, load-bearing for R3's row-level check) while enabling
  the new `"c-formal"` variant.
- **`generate_matrix_c.py`** now renders THREE artifacts
  (`traceability_matrix.formal.json/.md` alongside symbolic/concrete),
  assembling `dafny_store` from the real, already-committed Gate C1
  capture (`dosage.dfy`, `raw_dafny_output.txt`, `run_manifest_dafny.json`)
  - no re-running evidence inside the generation pipeline. Only the
  formal call's `tool_versions` gains a `"dafny"` key; symbolic/concrete
  stays exactly as before (confirmed by diff).
- **`evidence/reconcile.py::run_formal_check`** - a new, separate,
  narrowly-scoped check for the formal view. The existing fact-equality
  gate (`run_gate`, `VARIANT_ARTIFACTS`) is deliberately **unchanged** -
  the formal artifact isn't in that tuple, so the strict
  A==B==symbolic==concrete check keeps passing exactly as before
  (`intent {'REQ-GIP-1-4-12': False, 'REQ-GIP-1-8-1': False,
  'REQ-DOSE-003': True}`, byte-identical to before this wiring).
  `run_formal_check` instead verifies the formal view's intent_ok
  matches that reference EXCEPT a named, tracked set,
  `KNOWN_FORMAL_INTENT_DIVERGENCE = {"REQ-GIP-1-4-12", "REQ-GIP-1-8-1"}`,
  which must specifically be `True` - any other requirement diverging,
  or either named one diverging in the wrong direction, is still a hard
  failure. Wired into `regenerate_all.py` right after the main gate.
- **`generate_artifacts.py`** - the structural PROVEN sweep (stage 6)
  now explicitly sweeps `traceability_matrix.formal.json` too, proving
  ruling R3 accepts this real row inside the actual pipeline, not just
  when `generate_matrix_c.py` runs standalone. `dosage.dfy`,
  `raw_dafny_output.txt`, `run_manifest_dafny.json` added to `INPUTS`;
  the new formal artifacts added to `OUTPUTS`.

**The result:** `traceability_matrix.formal.json` - 3 rows: two real
PROVEN rows (REQ-GIP-1-4-12, REQ-GIP-1-8-1; `method: "dafny"`;
`verifier_completion_status: "completed"`; `intent_ok: true`) and the
pre-existing `system_scope` GAP row for REQ-GIP-1-4-12 (unchanged in
kind). `intent_ok` flips from `False` to `True` for both requirements in
this view - the first time since Phase A that `intended_method:
"PROVEN"` has actually been realized, not just declared.

**Tests:** `tests/test_dafny_wiring.py`, 15 tests - the real formal
artifact has exactly the two expected PROVEN rows, each satisfying R3;
passes `assert_no_realized_proven` for real; symbolic/concrete/A/B
confirmed completely unaffected (regression); `dafny_record` refuses an
unsatisfiable precondition and a broken capture (both gates
independently exercised) and accepts the real committed capture;
`dafny_binding_conflicts` catches a spec_target mismatch and a missing
capture, correctly no-ops when `dafny_store is None`; the real metadata
+ dafny store combination has zero conflicts; `run_formal_check` passes
on the real committed artifacts and correctly rejects both an unnamed
divergence and a wrong-direction divergence of a named one; an
end-to-end `build_matrix("c-formal", ...)` call matches the committed
artifact byte-for-byte. Full suite: **93 passed** (78 prior + 15 new).
Full `generate_artifacts.py` pipeline re-run end to end: PASS, including
the new formal-view check.

**Explicitly not done, and not this build's job:** variants A and B
don't bind dafny evidence at all - deliberately deferred, per the
ratified scope decision, confirmed unaffected by test rather than
assumed. The CLI (`evidence/cli.py`) was not extended with a
`"c-formal"` variant choice or a way to supply a `dafny_store` from the
command line - a separate design question that wasn't part of this ask.
No generic "wire any future Dafny spec into the matrix" tooling was
built - this wired the one path for the one spec that exists.

## 2026-07-07 — Phase C Gate C4 built: Spec-Testing Proofs found and fixed a real gap in dosage.dfy

Requested directly: "start gate C4." Applied IronSpec's methodology -
prove a specific input/output pair is accepted or rejected by the
SPECIFICATION itself, independent of any implementation - to the one
Dafny spec that exists in this repo (`dosage.dfy`, Gate C1). It found a
real gap on the first attempt, not a synthetic demonstration.

- **The finding, confirmed mechanically:** `CalculateHourlyDose`'s
  original two ensures clauses (`0.0 <= dose <= maxSafeDoseMgPerHr` and
  `infusionRateMlPerHr >= 0.0 || dose == 0.0`) bound `dose` and force it
  to 0 on reverse flow, but never relate it to the actual product of
  rate and concentration otherwise. A Dafny lemma stating "for these
  fixed inputs, if dose satisfies both ensures clauses, dose must equal
  the one correct clamped value" **failed to verify** - Dafny could not
  prove it, because the postcondition genuinely doesn't force it. A
  method that always returned `0.0` for any non-negative-rate input
  would have satisfied the exact spec Gate C1 verified clean. The same
  bug class Gate 1 found by hand for REQ-GIP-1-4-12 (spec/evidence not
  matching the requirement text), recurring independently in this
  session's own new Dafny spec - caught mechanically this time.
- **Fixed for real:** `examples/dosage_calculator/dosage.dfy` gained
  `function ExpectedDose(concentrationMgPerMl, infusionRateMlPerHr,
  maxSafeDoseMgPerHr): real` (the same three-way clamping logic as the
  method body) and a new `ensures dose == ExpectedDose(...)` clause
  pinning the output exactly. The two original ensures clauses stay,
  unchanged, for direct per-requirement traceability. Re-verified clean:
  `2 verified, 0 errors` (the function plus the method - up from `1
  verified`). **The real committed capture was re-run honestly, not
  patched:** `raw_dafny_output.txt` / `run_manifest_dafny.json` now
  reflect the fixed spec; `tests/test_dafny_adapter.py`'s exact
  `raw_status` assertion was updated to match, with a comment.
- **Preserved exhibit:** `examples/dosage_calculator/dosage_underconstrained.dfy`
  keeps the original weak spec byte-for-byte (same rationale as
  `dosage_naive_widening.py`) - it still verifies cleanly on its own (`1
  verified, 0 errors`); the bug is a spec weakness, not a verification
  failure.
- **Two STP suites, mechanically proving both directions, each
  `include`-ing the relevant spec rather than duplicating it:**
  - `dosage_stp_suite.dfy` (`include "dosage.dfy"`): six lemmas across
    the three logical branches of `CalculateHourlyDose` - normal
    in-range, ceiling-clamped, reverse-flow. ACCEPT + REJECT pairs for
    the first two; ACCEPT-only for reverse-flow (never a gap -
    `infusionRateMlPerHr >= 0.0 || dose == 0.0` already pins dose to 0
    there, even in the weak spec). All six verify: `10 verified, 0
    errors`, exit 0.
  - `dosage_stp_suite_against_underconstrained.dfy` (`include
    "dosage_underconstrained.dfy"`): the same two REJECT lemmas, run
    against the weak spec instead. Both **genuinely fail**: `0
    verified, 2 errors`, exit 4 - a real negative capture, not smoothed
    over, same discipline as `dosage_broken.dfy`.
- **A mistake caught during this build, before committing:** an early
  draft of the ceiling-clamped REJECT lemma used the raw unclamped
  product (`500.0`) as the "wrong" value. That lemma verified even
  against the weak spec - not because the weak spec pins the correct
  value, but because `500.0` already violates the weak spec's own
  `0.0 <= dose <= maxSafeDoseMgPerHr` bound directly, so excluding it
  proved nothing about the real gap. Caught by checking the lemma's
  actual behavior against the weak spec directly rather than assuming
  the chosen value was a good test; corrected to `50.0` (in-bounds,
  still wrong) in both suites, re-verified, and a regression test added
  (`test_reject_lemmas_target_in_bounds_wrong_values_not_out_of_bounds_ones`)
  guarding against silently reintroducing the weaker value.
- **New capture runners:** `run_verify_dafny_underconstrained.py`,
  `run_verify_dafny_stp_suite.py`,
  `run_verify_dafny_stp_suite_against_underconstrained.py` - all
  mirroring `run_verify_dafny.py`'s discipline, producing genuine
  committed captures, no fabricated output.
- **Tests:** `tests/test_dafny_stp_suite.py`, 6 tests, checking the real
  committed captures directly (not via `evidence.dafny_adapter.py`,
  since an STP suite's capture is a proof about the spec's tightness,
  not itself a requirement's verification evidence). Full suite: **78
  passed** (72 prior + 6 new). Full `generate_artifacts.py` pipeline
  re-run: zero observable change beyond `generated_utc` timestamps.
- **Explicitly not done, and not this gate's job:** neither STP suite is
  wired into `build_matrix()` or any generator, and no automated
  mechanism runs STPs against future Dafny specs as a matter of course -
  this gate authored one STP suite for the one spec that exists, per
  its stated scope, not a generic STP-generation tool.

## 2026-07-07 — Phase C Gate C3 built (vectors 1-3): Z3 precondition check, weak-postcondition heuristic, timeout/resource-limit masking hardened

Requested directly: "start gate c3." Four vectors were named in the
roadmap; three were scopeable and are built here, the fourth stays
blocked exactly as before.

- **Vector 1 (vacuous preconditions) - BUILT.** New module
  `evidence/dafny_spec_lint.py::check_precondition_satisfiability`:
  extracts a method's `requires` clauses (`_find_method_header` tracks
  paren depth to find the body's opening brace; `_extract_clauses`
  splits on clause keywords) and hands their conjunction to Z3 for a
  real satisfiability check. A small hand-written recursive-descent
  translator (`_tokenize` + `_Parser`) covers the boolean/comparison/
  arithmetic subset this repo's specs actually use - `&&`, `||`, `!`,
  `==>`, `<==>`, chained comparisons, `+-*/`, real/int/nat/bool
  identifiers and literals (`nat` gets its implicit `>= 0` Dafny
  semantics). Quantifiers, `old(...)`, unknown parameter types, and any
  unparseable syntax raise `SystemExit` outright - refused, never
  mistranslated.
- **Proven against a real committed fixture, not a synthetic string
  only:** new `examples/dosage_calculator/vacuous_precondition_probe.dfy`
  - a tiny, dedicated Dafny file with `requires x > 0 && x < 0` and
  `ensures r == 999999`. Verified for real against Dafny 4.11.0: **`1
  verified, 0 errors`, exit 0** - a genuine clean pass on a method whose
  precondition can never hold. The Z3 checker correctly reports `unsat`
  on the same method - catching mechanically what the verifier's own
  clean-pass report missed. A true-negative companion confirms the real
  dosage.dfy kernel's actual precondition is `sat`.
- **Vector 2 (weak postconditions) - BUILT, heuristic, best-effort, as
  the roadmap scoped it.** `scan_weak_postconditions` flags `ensures`
  clauses using `==>` without a matching `<==>`. Tested against a
  synthetic weak clause (flagged, clause text quoted verbatim), the real
  dosage.dfy spec (zero warnings - its clauses use `<=`/`==`/`||`, never
  `==>`, a true negative), and a `<==>` clause (not flagged, another
  true negative). Explicitly not a proof: it cannot decide whether a
  bi-implication was actually needed for a given spec.
- **Vector 3 (timeout/resource-limit masking) - BUILT, with a real
  empirical finding.** `dafny verify --resource-limit=1` on the real,
  committed `dosage.dfy` spec produces
  `Dafny program verifier finished with 0 verified, 0 errors, 1 out of resource`
  - an errors count of 0 on a run that did not complete. Committed for
  real via new `run_verify_dafny_resource_limited.py`, producing genuine
  `raw_dafny_output_resource_limited.txt` /
  `run_manifest_dafny_resource_limited.json`.
- **Checked whether this is actually exploitable via exit_code alone -
  it is not, on this Dafny version.** The real captured `exit_code` is
  **4** (nonzero), so Gate C1's existing exit-code check already refuses
  this capture before the summary line is parsed. An earlier suspicion
  in this same session that the exit code was 0 here turned out to be a
  shell-scripting artifact - a piped command (`... | tail -20; echo
  "EXIT:$?"`) whose `$?` captured `tail`'s exit status, not `dafny`'s.
  Caught and corrected by re-running the same command without the pipe
  before reporting it as a finding - the "verify empirically, don't
  assume" discipline applied to my own probing, not just the tool under
  test.
- **Hardened `evidence/dafny_adapter.py` anyway, as real defense in
  depth:** the summary-line regex now captures the tail after the error
  count and refuses if it contains `"out of resource"`, `"out of
  memory"`, or `"timed out"` (case-insensitive), independent of the
  exit-code check. Of these, only `"out of resource"` was independently
  reproduced end-to-end; the other two are the confirmed sibling
  vocabulary from the same Boogie/Dafny summary-formatting code path
  (verified by extracting UTF-16 string literals directly from the
  installed `Boogie.ExecutionEngine.dll` / `DafnyDriver.dll`) but not
  independently forced to reproduce this session - named as such. Also
  hardened: the parser now refuses if a capture contains more than one
  summary-line match (checked empirically that a normal multi-file
  `dafny verify` still emits exactly one aggregate summary line, so this
  closes a theoretical ambiguity without changing real-capture behavior).
- **Vector 4 (specification stripping) - still BLOCKED, named.** No new
  source material surfaced this session either.
- **Tests:** `tests/test_dafny_spec_lint.py` (11, vectors 1-2) and
  `tests/test_dafny_timeout_masking.py` (6, vector 3) - 17 new tests.
  Full suite: **72 passed** (55 prior + 17 new). Full
  `generate_artifacts.py` pipeline re-run: zero observable change beyond
  `generated_utc` timestamps.
- **Explicitly not done, and not this gate's job:** neither the Z3 check
  nor the weak-postcondition heuristic is invoked automatically anywhere
  in the capture or generation pipeline - standalone, tested
  capabilities, matching Gate C1's own scope. Wiring them into the
  capture workflow is a natural follow-up but wasn't asked for.

## 2026-07-07 — Phase C Gate C2 built: ruling R3, PROVEN's exclusivity migration

Requested directly: "start gate C2." The design was already fully
specified in `payloadguard-evidence-roadmap-phaseB-to-C.md`'s Gate C2
section from the prior planning session - this session implemented that
ratified design rather than inventing a new one.

- **`evidence/render/matrix_variants.py::assert_no_realized_proven`** -
  previously hard-failed if ANY record anywhere claimed PROVEN, full
  stop (ruling R2). Now implements ruling **R3**: PROVEN may appear as a
  realized strength only when a record's `method == "dafny"` **and**
  its `verifier_completion_status == "completed"` - both conditions
  required, not just a matching method label. Every other method -
  `crosshair`, `concrete_test`, or a record with no method at all (e.g.
  a scope-GAP row) - remains permanently, unconditionally excluded,
  exactly as under R2. Refactored into a shared `_assert_proven_gate`
  helper checked against both each row's `evidence` list (variant A's
  shape) and the row itself (variant B/C's flat shape).
- **Why both conditions, not just the method label:**
  `evidence/dafny_adapter.py::parse_dafny_capture` (Gate C1) is already
  structurally incapable of returning PROVEN unless its own exit-code,
  summary-line, and false-zero checks all passed - so in the adapter's
  own output the two conditions are always true together. R3 checks
  both anyway, at the matrix boundary, as defense in depth against a
  future binder assembling a Dafny-shaped record by hand instead of
  through the adapter, rather than trusting the method label alone.
- **`tests/test_proven_exclusivity.py`** - 8 new tests. The roadmap
  named two required cases; this build has both plus more:
  1. Positive - a real Dafny PROVEN record, produced via
     `parse_dafny_capture` against the real committed clean capture (the
     same one Gate C1 verified), is accepted.
  2. Negative, crosshair - a `method="crosshair"` record with
     `strength="PROVEN"` and a completed status is refused, checked
     explicitly with a real fixture, not inferred from the absence of a
     binder that would produce one.
  3. Negative, concrete_test - same property, the other permanently-
     excluded method.
  4. Negative, missing method - a record with no `method` key at all is
     refused, not silently accepted because there's nothing to compare
     against `"dafny"`.
  5-6. Negative, dafny method without a completed status (`None` and an
     explicit `"incomplete"` value) - the method label alone is not
     trusted; defense-in-depth, not redundant paranoia.
  7. Row-level shape - variant B/C's rows carry `strength`/`method`
     directly, not nested in an `evidence` list; confirmed the same
     rule applies there too.
  8. Regression - all four committed matrix artifacts (none of which
     contain a dafny record today) still pass unchanged.
- **Existing structural tests needed no changes:**
  `tests/test_structural_proven_check.py`'s corruption cases (a
  `crosshair`-method record forced to `PROVEN`) still raise under R3
  with the identical error-message substring - confirming R3 is a
  strict, narrow relaxation for one specific checked case, not a
  broadening of the rule in general.
- Full suite re-run: **55 passed** (47 prior + 8 new). Full
  `generate_artifacts.py` pipeline re-run: zero observable change to any
  committed matrix artifact beyond `generated_utc` timestamps - R3 has
  no effect on the live pipeline today, since no binder yet produces a
  dafny-method record.
- **Explicitly not done, and not this gate's job:** no binder
  (`_bind_declared`, `_bind_shadow`, `_bind_self_describing`) was
  changed to actually assemble a Dafny-sourced record into a live matrix
  row. R3 makes that *possible* without violating the structural gate;
  it does not make it *happen*. Per the roadmap's suggested build order,
  that wiring belongs alongside Gate C4 (STPs, "alongside the first real
  spec"); trusting a live PROVEN claim in earnest still waits on Gate C3.

## 2026-07-07 — Phase C Gate C1 built: real Dafny spec, capture runner, false-zero-guard adapter

Requested directly: "I need the C1 local build implementation" - not
just the toolchain research from the day before, the actual gate build.

- **`examples/dosage_calculator/dosage.dfy`** - a real Dafny method,
  `CalculateHourlyDose`, translated from `dosage.py`'s contracts
  (mirrors the clamping shape: `requires concentrationMgPerMl > 0.0`,
  `requires maxSafeDoseMgPerHr > 0.0`, `ensures 0.0 <= dose <=
  maxSafeDoseMgPerHr`, `ensures infusionRateMlPerHr >= 0.0 || dose ==
  0.0`). Verified for real against Dafny 4.11.0: `Dafny program
  verifier finished with 1 verified, 0 errors`, exit 0.
- **REQ-DOSE-003 explicitly scoped out of the Dafny spec** - checked,
  not assumed: `y := x / 0.0` on Dafny's `real` type is itself a
  flagged verification error, not a silent `inf`. Dafny reals are
  exact/arbitrary-precision with no IEEE overflow/infinity/NaN concept
  at all, so "finite result under overflow" cannot be faithfully stated
  as a Dafny postcondition. Named here as a deliberate exclusion rather
  than silently dropped or wrongly claimed proven. `weight_kg` also
  intentionally omitted (unused precondition-only guard in the Python
  original).
- **`dosage_broken.dfy`** - the Sample-B-equivalent broken variant
  (clamp removed). Fails for real: `0 verified, 2 errors`, exit code 4
  (not 1 - confirms the exit-code finding from the prior day's
  toolchain research, now exercised on the actual dosage spec).
- **`run_verify_dafny.py` / `run_verify_dafny_broken.py`** - capture
  runners mirroring `run_verify.py` exactly: subprocess `dafny verify`,
  commit verbatim stdout+stderr and a run manifest (tool, tool_version,
  command, exit_code, started_utc, target). Both run for real, producing
  genuine committed captures - `raw_dafny_output.txt`,
  `run_manifest_dafny.json`, `raw_dafny_output_broken.txt`,
  `run_manifest_dafny_broken.json`. No fabricated output anywhere.
- **`evidence/dafny_adapter.py::parse_dafny_capture`** - the false-zero
  guard, sharpened beyond the originally-planned substring floor.
  Parses the verifier's own summary line via regex (`Dafny program
  verifier finished with (\d+) verified, (\d+) errors?`) and checks the
  parsed error count - never a blind `"0 errors" in raw_output`
  substring match, which a printed error message could coincidentally
  contain. Refuses, in order: nonzero exit code (cheapest, checked
  first); no summary line found (a crash, timeout, or a `dafny audit`-
  style "did not attempt verification" message must not be silently
  treated as success just because exit_code happens to be 0); nonzero
  parsed error count. `evidence/model.py` gained
  `verifier_completion_status: Optional[str] = None` on
  `VerificationResult` (purely additive).
- **`tests/test_dafny_adapter.py`** - six tests, all passing. One found
  and fixed an incorrect test expectation during writing: the real
  broken capture's `exit_code=4` triggers the exit-code refusal before
  the summary line is ever parsed, so
  `test_refuses_real_committed_broken_capture` was corrected to expect
  `"does not report a clean pass"` (not a summary-line error match).
  The load-bearing regression,
  `test_false_zero_guard_is_not_fooled_by_a_substring_trap`, constructs
  raw output containing the literal substring `"0 errors"` in an
  unrelated sentence plus a real summary line reporting `3 verified, 2
  errors`, and confirms the parser correctly refuses where a blind
  substring check would have wrongly passed. A sixth test,
  `test_producing_a_proven_result_does_not_reopen_the_matrix_gate`,
  builds a fake matrix row from this adapter's real `Strength.PROVEN`
  output and confirms `assert_no_realized_proven`
  (`evidence/render/matrix_variants.py`) still hard-blocks it.
- **Explicitly not done, and not this module's job:** `dafny_adapter.py`
  is not called from `build_matrix()`, any `generate_matrix_*.py`
  script, or the CLI. Wiring a Dafny-sourced PROVEN result into the
  matrix pipeline is Gate C2's job by name (the PROVEN-exclusivity
  migration), still unbuilt.
- Full suite re-run after the build (47 passed) and the full
  `generate_artifacts.py` pipeline re-run, confirming zero observable
  change to existing committed matrix artifacts beyond `generated_utc`
  timestamps.

## 2026-07-06 — SessionStart hook: make the Dafny/Python toolchain reproducible

The toolchain research below only held for this session's container.
Requested directly: set it up so a future session doesn't have to redo
it from scratch.

- Added `.claude/hooks/session-start.sh` (registered in
  `.claude/settings.json`, synchronous mode): installs the Python deps
  (`crosshair-tool`, `jsonschema`, `pyyaml`, `pytest` - per README's
  "Running it") and the .NET/Dafny toolchain (`dotnet-sdk-8.0` via apt,
  then `dotnet tool install --global dafny --version 4.11.0` via NuGet).
- **Dafny is pinned explicitly to 4.11.0**, not "latest" - the exact
  version this session verified the false-zero note, exit-code
  behavior, and the vacuous-precondition risk against. An unpinned
  install could silently pick up a different Dafny version with
  different output conventions in a future session, undermining
  everything just verified. Matches the `crosshair-tool 0.0.107`
  pinning discipline already established for CrossHair.
- Idempotent: checks `command -v dotnet` / the installed Dafny version
  before doing any apt or dotnet work, so a warm container (already
  provisioned) skips straight through.
- **Validated, not assumed:** ran the hook directly
  (`CLAUDE_CODE_REMOTE=true ./.claude/hooks/session-start.sh`) - exit 0,
  ~1.4s on the already-provisioned path (this session), correctly
  skipped reinstalling. Confirmed `dafny --version` resolves to
  `4.11.0` via the hook's `$CLAUDE_ENV_FILE` PATH export, then ran the
  full test suite (41 passed) and one targeted test file individually,
  both immediately after sourcing that same env file - the same PATH a
  fresh session would inherit.
- No linter is configured in this repository (no `.flake8` / `ruff.toml`
  / CI workflow found) - that validation step from the skill's workflow
  doesn't apply here; noted rather than skipped silently.
- Not yet re-validated from a genuinely cold container (this session
  already had dotnet/Dafny installed from the prior research) - the
  from-scratch apt+dotnet-tool install path was exercised manually
  earlier this session and confirmed to work; the hook runs the
  identical commands.

## 2026-07-06 — Phase C Gate C1: Dafny toolchain blocker resolved (modern Dafny obtained)

Requested directly: research whether a modern Dafny is obtainable rather
than settling for the ancient apt package or asking for an
under-informed decision.

- **GitHub confirmed genuinely blocked, not assumed.** The proxy's own
  status endpoint (`curl $HTTPS_PROXY/__agentproxy/status`) and its
  README are explicit: 403/407 is an organization egress-policy denial -
  "do not retry or route around it." No workaround attempted.
- **Two already-permitted channels turned out to be enough.**
  `api.nuget.org` -> 200. `dot.net` / `dotnet.microsoft.com` -> normal
  redirects. apt has `dotnet-sdk-8.0` directly (Ubuntu's own package,
  not a Microsoft add-on repo) - installed cleanly as 8.0.128 after
  `apt-get update` refreshed a stale index (it had been pointing at a
  version no longer on the mirror).
- **`dotnet tool install --global dafny`** pulled from NuGet - zero
  GitHub involvement anywhere in the chain. Result: **Dafny 4.11.0**
  (full version `4.11.0+fcb2042d6d043a2634f0854338c08feeaaaf4ae2`), a
  real current release, not the `2.3.0+dfsg-0.1` Mono-based package apt
  offers directly.
- **Verified against the running binary, three real checks, not
  documentation:**
  1. Clean pass on a valid clamping method: `Dafny program verifier
     finished with 1 verified, 0 errors`, exit 0 - exact match to the
     false-zero note already in `evidence/model.py`.
  2. Broken method: per-line error blocks + `0 verified, 2 errors`,
     **exit code 4** - new finding, Dafny's exit codes aren't a simple
     0/1 pair the way CrossHair's are.
  3. An unsatisfiable precondition (`x > 0 && x < 0`) against an
     obviously-false postcondition verified clean - confirms Gate C3's
     vacuous-precondition vulnerability is real and reproducible on this
     binary, not speculative.
- **Checked whether `dafny audit` (new in 4.x) makes the Z3-based
  mitigation unnecessary - it doesn't.** Ran it against the vacuous
  case: `0 findings`. Its actual scope (per its own help text) is
  un-annotated assumes/axioms/non-determinism/unverified externs, not
  general precondition satisfiability. Confirmed the originally-planned
  mitigation is still necessary and technically feasible:
  `z3.Solver()` correctly returns `unsat` for the contradictory
  precondition and `sat` for a real one.
- **Net effect: no alteration to the Gate C1-C3 plan.** If anything it's
  on firmer ground than when written. One concrete addition carried
  into Gate C1: capture the exit code as-is, don't assume a specific
  nonzero value on failure.
- **Not done:** no capture runner, no real Dafny spec for `dosage.py`,
  nothing committed to the repository - this was toolchain research
  only, per what was asked. The probe `.dfy` files live only in the
  scratch directory.
- Documentation updated: `KNOWN_LIMITATIONS.md` (Gate C1 row + full
  detail section), roadmap doc (environment-check section + closing
  summary), `SYSTEM_BLUEPRINT.md`, `README.md`.

## 2026-07-06 — Phase C planning: gate-sequenced plan, real environment check

Requested directly ("Move on to Phase C planning") right after Phase
B's gate ledger closed. Planning only - no Phase C code written.

- **Environment check done first**, same discipline as every prior
  toolchain decision in this repo: `z3 --version` -> 4.16.0, and
  `python3 -c "import z3"` succeeds - usable directly. `dafny` is not on
  PATH. `apt-cache show dafny` finds a package, but it's
  `2.3.0+dfsg-0.1` - Ubuntu universe, roughly 2015-era, depending on
  Mono (`mono-mcs`, `mono-runtime`), not the modern .NET-based Dafny
  (4.x) the false-zero note in `evidence/model.py` is written against.
  `dotnet` isn't installed; a direct GitHub release fetch 403'd through
  the environment's proxy. Recorded as a real, named blocker
  (`KNOWN_LIMITATIONS.md`) rather than assumed away or silently deferred
  - mirrors the `crosshair-tool 0.0.107` pinning precedent from Gate 3.
- **Restructured** `payloadguard-evidence-roadmap-phaseB-to-C.md`'s
  Phase C section from a flat two-mechanism sketch into six sequenced
  gates (C1-C6), each with scope, dependencies, and a suggested build
  order:
  - C1: Dafny adapter capture + minimal false-zero guard (foundation).
  - C2: PROVEN's exclusivity migration - sequenced immediately after C1,
    before any real spec exists, since this is the highest-consequence
    change in Phase C (a bug here would let PROVEN leak onto un-proven
    evidence). Recommended it get ratified-ruling-level review, like
    R1/R2 did.
  - C3: output-parsing hardening - three of four vulnerability vectors
    scoped (vacuous preconditions via Z3 satisfiability check, weak
    postconditions as a best-effort pattern check, timeout/resource
    masking via `verifier_completion_status`); the fourth
    (specification stripping) named BLOCKED - the source material
    describing it was cut off before this session had it in full, so
    it's recorded as needing a follow-up read, not guessed at.
  - C4: Spec-Testing Proofs, alongside whichever spec C1 produces first.
  - C5: mutation testing (MutDafny-style, six operators) - flagged as
    the largest single piece, recommended as its own sub-plan once C1-C2
    are stable rather than attempted in one pass.
  - C6: NL-dialogue confirmation - a process control with no technical
    dependency on the others, recommended adopted immediately rather
    than deferred.
- **Also recorded in `KNOWN_LIMITATIONS.md`** as two new blocked/named
  rows (Dafny toolchain decision; C3's fourth vector) so the live gate
  ledger surfaces them, not just the roadmap doc.
- `SYSTEM_BLUEPRINT.md` and `README.md` updated: Phase B marked
  COMPLETE (gate ledger fully closed); Phase C marked "planning," with
  the environment findings summarized.
- No code changes this session - planning only, as requested.

## 2026-07-06 — Gate 5 fully resolved: concrete-only fixture now constructible

Closed the last open item from the original six-gate ledger. Requested
directly ("concrete fix gate 5") right after Gate 2 completed.

- **Root cause:** `_bind_self_describing` (variant C's binding strategy,
  `evidence/render/matrix_variants.py`) bound a symbolic record to
  *every* requirement unconditionally, regardless of what it declared -
  a leftover from before metadata.c.yaml carried `evidence` declarations
  at all. This made a concrete-only requirement structurally impossible:
  it would always show up in the symbolic artifact too.
- **Fix:** `_bind_self_describing` now checks each requirement's
  declared `evidence` list before binding symbolic evidence - a
  requirement declaring only `concrete_test` entries (no `crosshair`
  entry) gets no symbolic record. When `evidence` is absent entirely,
  the original unconditional behavior is preserved for backward
  compatibility - the existing symbolic-only fixture relies on exactly
  this fallback path and needed no changes. Concrete binding is
  untouched either way - stays fully self-describing via
  `concrete_results.json`'s own `requirement_id`, per Gate 4's decision.
- **No effect on committed data:** every real requirement in
  `metadata.c.yaml` declares `crosshair` (added when Gate 4's asymmetry
  was closed), so this changes nothing observable - confirmed by
  regenerating and diffing (differs only by `generated_utc`).
- **Proven, not assumed:** `tests/test_single_evidence_type.py` gained a
  concrete-only fixture (a requirement declaring
  `evidence: [{method: concrete_test, test_id: ...}]`, no `crosshair`
  entry) alongside the existing symbolic-only one - confirmed to appear
  in exactly the concrete artifact and not at all in the symbolic one,
  the property that was previously impossible. 4 tests total (2
  fixtures × schema validation + binding behavior). Full suite: 41
  passed (39 prior + 2 new). Full pipeline re-run independently.
- Documentation updated: `KNOWN_LIMITATIONS.md` (new dedicated Gate 5
  section, ledger table updated to FULLY RESOLVED), `SYSTEM_BLUEPRINT.md`,
  `README.md`, roadmap doc (new Gate 5 section, Gate 4's stale
  "constructibility note still holds" corrected, closing summary fixed).
- **Gate 5 is now fully resolved.** Combined with Gate 2's completion,
  every gate in the original ledger is closed, decided, or resolved -
  nothing structural remains open in Phase B's gate work; only Phase C
  (Dafny/Z3 adapters) is ahead.

## 2026-07-06 — Gate 2 build, Phase 7: Step 4 (delete the fallback) — Gate 2 COMPLETE

Requested explicitly, now that the CLI had landed and the cutover had
run stable through multiple independent verification passes.

- **Deleted:** `build_matrix_variant_a`, `build_matrix_variant_b`,
  `build_matrix_variant_c` from `evidence/render/matrix_variants.py`.
  Their shared markdown renderers (`_markdown_variant_a/b/c`) and other
  helpers stayed - `build_matrix()` already used those, not the deleted
  top-level functions.
- **Deleted:** `tests/test_binder_equivalence.py`. Its entire purpose
  was proving the old functions' output equals `build_matrix()`'s
  output - moot once the old functions don't exist.
- **Migrated, not deleted:** `tests/test_single_evidence_type.py` (Gate
  5's fixture test) was the one other place in the suite calling
  `build_matrix_variant_c` directly - updated to call
  `build_matrix("c-symbolic"/"c-concrete", ...)` instead. Confirmed
  still passing (2/2) before moving on.
- **Comments updated, not left stale:** the module-level banner in
  `matrix_variants.py` and the header comments in `generate_matrix_a/b/c.py`
  that described the now-gone fallback were rewritten to stop
  referencing it, rather than left describing something that no longer
  exists.
- **Verified after deletion, not just before it:** full suite (39
  passed - 44 minus the 5 deleted equivalence tests), full pipeline
  re-run (every regenerated artifact still differs only by
  `generated_utc`), and the CLI independently re-checked against a
  committed artifact post-deletion.
- **Corrected an overclaim while updating the roadmap doc:** a first
  draft of the "what's done" summary said Gate 5's concrete-only-fixture
  limitation was now closed by Gate 2's completion. Checked before
  committing: `build_matrix()`'s `_bind_self_describing` strategy for
  variant C is a literal extraction of the original C builder's
  logic - it still binds a symbolic record to every requirement
  unconditionally, unchanged by the refactor. Gate 5 stays resolved for
  the constructible half only; fixed before it went in the doc.
- Documentation updated: `KNOWN_LIMITATIONS.md` (Gate 2 marked
  COMPLETE), `SYSTEM_BLUEPRINT.md`, `README.md`, roadmap doc (Gate 2's
  heading, Gate 4's status, the closing summary).
- **Gate 2 is now structurally complete** - CONFLICT rule (both types),
  the vocabulary-agnostic binder, and the CLI are all built, verified,
  and documented. The only open item in Gate 2's scope was ever its own
  definition, and that's ratified. Git history holds the deleted
  fallback and test if ever needed again.

## 2026-07-06 — Gate 2 build, Phase 6: CLI (built ahead of Step 4, at Steven's direction)

Steven asked to hold off deleting the Step 2 fallback functions and get
the CLI done first - so the fallback stays available while new
capability is still landing, rather than being removed before anything
else changes.

- **Built:** `evidence/cli.py` - `python -m evidence.cli build --variant
  {a|b|c-symbolic|c-concrete} --metadata PATH --manifest PATH --concrete
  PATH [--schema PATH] [--out-json PATH] [--out-md PATH]`. Wraps
  `build_matrix()` with every input as an argument instead of the
  hardcoded `examples/dosage_calculator` paths the generator scripts use
  - the genuinely vocabulary-agnostic surface Gate 2 was named for: this
  can build a matrix for a different device's evidence set matching one
  of the four schema shapes, not just the worked example.
  `tool_versions` is now keyed by the manifest's own declared `tool`
  field rather than a hardcoded `"crosshair"` string, so a future
  Dafny/Z3 manifest won't need this CLI changed.
- **Two real bugs caught and fixed while building it, not left in:**
  1. An uncaught `jsonschema.ValidationError` printed via `str(e)` dumps
     the *entire schema* on every validation failure - useless noise for
     a CLI user. Fixed to use `ValidationError.message`, the short
     human-readable line.
  2. Omitting both `--out-json` and `--out-md` printed the JSON *and*
     the markdown concatenated to stdout, producing invalid combined
     output (caught by `test_cli_prints_to_stdout_when_no_output_path_given`
     failing with a `JSONDecodeError`). Fixed: markdown only ever goes
     where `--out-md` explicitly says to, never to stdout.
- **Proven, not assumed:** `tests/test_cli.py` (10 tests) drives the CLI
  via subprocess (the way a real user would invoke it) for all four
  variants and asserts byte-identical output (timestamp aside) to the
  corresponding committed artifact, plus both Tier-1 error paths (schema
  validation, CONFLICT Type 1 - confirmed to fire through the CLI path
  too) and both output modes (file, stdout). Full pipeline independently
  re-run to confirm the CLI's addition changed nothing about the
  existing generator scripts. Suite: 44 passed (34 prior + 10 new).
- Documentation updated: `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`,
  `README.md` (including a new CLI usage example in "Running it"),
  roadmap doc. Only Step 4 (delete the Step 2 fallback once stable)
  remains for Gate 2's binder work.

## 2026-07-06 — Gate 2 build, Phase 5: vocabulary-agnostic binder, Step 3 (fold in Type 1; confirm Type 2 stays standalone)

Continuing the phased binder build. Re-examined the plan before
implementing rather than mechanically following the earlier wording
("fold Types 1/2 into the binder") - Type 2 doesn't actually fit inside
a per-variant builder call, and forcing it in would have been worse
design, not better.

- **Analysis:** Type 1 (identity mismatch) is inherently per-variant -
  it checks one metadata file's declared bindings against the evidence
  store - so it belongs inside `build_matrix()`. Type 2 (outcome
  mismatch) compares raw manifests across the WHOLE dataset regardless
  of which variant is being built; folding it into `build_matrix()`
  would mean re-running the identical whole-dataset check redundantly on
  every one of the four variant calls, for no benefit. It stays a
  standalone `generate_artifacts.py` stage, the same way the
  fact-equality gate does (both are properties of the artifact/input
  set, not of a single generation call).
- **Folded in:** `build_matrix()` now calls `run_conflict_gate(metadata,
  concrete_store, manifest)` as its first step, before assembling any
  record - Tier 1. This closes a real gap: Type 1 previously only ran
  inside the `generate_artifacts.py` pipeline stage, so running e.g.
  `generate_matrix_a.py` alone would have bypassed it entirely (the
  individual generators are documented to bypass fact-equality the same
  way - Type 1 had identical exposure until now).
- **Base matrix's check narrowed, not removed:** `metadata.yaml` never
  calls `build_matrix()` (frozen `manual_matrix.py` path, ruling R2c), so
  it keeps its own explicit check. Renamed `stage_conflict_check` to
  `stage_base_conflict_check`, scoped to just the base file (3 symbolic
  bindings - base declares no concrete evidence at all). Stage 5's
  comment updated to note a/b/c-symbolic/c-concrete are now
  self-checking via `build_matrix()`.
- **Proven, not assumed:** added
  `test_build_matrix_folds_in_type1_check` to
  `tests/test_conflict_check.py` - drives `build_matrix()` directly with
  a conflicting in-memory fixture and confirms it raises before
  assembling a single record, proving the fold-in itself rather than
  just the underlying check function. Full pipeline re-run end to end;
  every regenerated artifact still differs only by `generated_utc`.
  Suite: 34 passed (33 prior + 1 new).
- **Documented tradeoff:** `build_matrix_variant_a/b/c` (the Step 2
  fallback) do NOT have Type 1 folded in. If the fallback is ever used
  in an emergency, Type 1's per-call check is temporarily lost along
  with it - an accepted tradeoff of restoring known-good behavior
  quickly, recorded rather than silently true.
- Documentation updated: `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`,
  `README.md`, roadmap doc. Gate 2's binder work is now Steps 1-3 done;
  Step 4 (delete the fallback once stable) and the CLI remain.

## 2026-07-06 — Gate 2 build, Phase 4: vocabulary-agnostic binder, Step 2 (cutover)

Steven approved proceeding with an explicit request to keep a fallback
available ("ensure we can fallback if necessary"). Cutover done with
that constraint built in, not bolted on afterward.

- **Cut over:** `generate_matrix_a.py` / `_b.py` / `_c.py` now import
  and call `build_matrix("a"/"b"/"c-symbolic"/"c-concrete", ...)` from
  `evidence/render/matrix_variants.py` instead of the original
  `build_matrix_variant_a/b/c` functions directly.
- **Fallback, by design:** the three original functions are deliberately
  left in place, fully intact and unused. If a problem with
  `build_matrix()` ever surfaces, each generator's import + call can be
  reverted to the corresponding original function in one line, or this
  commit can be `git revert`ed outright. Deleting them is scoped as its
  own later cleanup step (Step 4), gated on the cutover proving stable —
  not bundled into the cutover itself.
- **Verified, not assumed:** ran the full `generate_artifacts.py`
  pipeline post-cutover (all 7 stages clean) and diffed every
  regenerated artifact against the pre-cutover committed versions -
  differs only by `generated_utc`, exactly as the Step 1 equivalence
  proof predicted. Full suite: 33 passed, unchanged from Step 1 (this
  step changed which function each generator calls, not any logic).
- Updated the module-level comment in `matrix_variants.py` to mark
  `build_matrix()` as authoritative and the three original functions as
  an explicit, intentional fallback rather than dead code.
- Documentation updated: `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`,
  `README.md`, roadmap doc - Gate 2's binder work now tracked as Steps
  1-2 done, Step 3 (fold CONFLICT Types 1/2 into the binder) and Step 4
  (delete the fallback functions once stable) still open, plus the CLI.

## 2026-07-06 — Gate 2 build, Phase 3: vocabulary-agnostic binder, Step 1

Steven confirmed the phased plan and set the working principle for the
rest of Phase B->C: correctness over speed, one step at a time, always
with the end of Phase C in view. This step is scoped narrowly on
purpose - it is a genuine architectural refactor (unlike Types 1/2,
which extended an existing pattern), so it gets its own proof before
anything currently authoritative is touched.

- **Built:** `build_matrix(variant_key, metadata, manifest,
  concrete_store, tool_versions=None)` in
  `evidence/render/matrix_variants.py` - one entry point replacing
  `build_matrix_variant_a/b/c`. Literal extraction, not new logic: each
  variant's record-assembly ("binder": `_bind_declared`, `_bind_shadow`,
  `_bind_self_describing`) and row-rendering ("shape":
  `_shape_evidence_array`, `_shape_flattened_shadow`,
  `_shape_method_partitioned`) lifted verbatim into named functions,
  dispatched through a declarative table (`_VARIANT_SPECS`) instead of
  three separate top-level functions. Binding strategy and row shape
  split as the two real axes of variation, so a future fifth shape can
  reuse an existing piece instead of requiring a whole new function.
- **Correctness proof:** `tests/test_binder_equivalence.py` (5 tests)
  runs the old function and `build_matrix()` against identical real
  committed inputs for all four variant keys and asserts equality two
  ways - dict equality and `json.dumps()` string equality (the second
  catches key-order drift dict equality alone would miss). All pass.
- **Nothing cut over.** `generate_matrix_a.py` / `_b.py` / `_c.py` and
  `regenerate_all.py` still call the original functions, untouched.
  Pipeline re-run end to end; every regenerated artifact differs only by
  `generated_utc` - zero observable change from this step. Suite: 33
  passed (28 prior + 5 new).
- Documentation updated to record Step 1 as done and Step 2 (the actual
  cutover - retiring the three old functions and generator scripts,
  folding Types 1/2 into the binder) as the next, deliberately separate,
  higher-risk step: `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`,
  `README.md`, roadmap doc.

## 2026-07-06 — Gate 2 build, Phase 2: Type 2, variant C asymmetry closed

Continuation of the phased Gate 2 build, addressing the two remaining
well-scoped gaps flagged at the end of Phase 1 (Type 2, variant C's
binding asymmetry). The third — the vocabulary-agnostic binder + CLI
unification — is deliberately left for its own phase: it's a real
architectural refactor (consolidating four separate generator scripts),
not an extension of the existing Type 1 pattern, and carries meaningfully
more regression risk.

- **Variant C asymmetry closed (Gate 4).** `metadata.schema.c.json`
  gained an optional `evidence` property (identical shape to variant
  A's); `metadata.c.yaml` now declares it on all three requirements,
  matching the real bindings already in `concrete_results.json`
  (`kernel_detects_bolus_limit_exceeded` -> REQ-GIP-1-4-12, etc.). This
  is cross-checking-only: `build_matrix_variant_c` never reads
  `evidence` — C's binding stays evidence-store-carried, unchanged.
  Confirmed by regenerating: C's artifacts diff only by `generated_utc`.
  Bindings checked by the Type 1 gate rose from 20 to 24 (C now
  contributes 7 instead of 0).
- **Type 2 (outcome mismatch) built.** `evidence/conflict.py` gained
  `outcome_conflicts()` / `run_outcome_gate()`: manifests are grouped by
  identity (tool, target, enforced `per_condition_timeout_s` —
  deliberately excluding the raw argv's environment-specific absolute
  path and `started_utc`); a group with more than one distinct
  `exit_code` is a conflict. Wired into `generate_artifacts.py` as stage
  4, run against all four committed manifests: 4 manifests, 4 distinct
  identities, 0 conflicts — real, honest, and currently vacuous, since no
  two committed manifests share a target. Tested with two synthetic
  cases (positive mismatch; same-outcome-different-target confirming no
  over-firing).
- `tests/test_conflict_check.py`: 11 tests total (up from 7) — added
  variant C's clean-pass case and three Type 2 cases.
- Full pipeline re-run end to end (7 stages now); regenerated artifacts
  confirmed byte-identical except timestamps. Suite: 28 passed (24 prior
  + 4 new).
- Documentation updated: `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`,
  `README.md`, roadmap doc.
- **Still open, its own phase:** the vocabulary-agnostic binder (one
  implementation driving all four schema variants, replacing
  `generate_matrix_a/b/c.py`) and the CLI. Both CONFLICT types run today
  as standalone pipeline stages alongside the existing separate
  generators.

## 2026-07-06 — Gate 2 build, Phase 1: CONFLICT rule Type 1 (identity mismatch)

First build increment against the roadmap, taken in a small, self-
contained phase per Steven's direction (small phases, stop for input or
new issues). Scoped to what was already fully specified and ratified —
no new decisions required.

- **`evidence/conflict.py`:** implements Type 1 for real, over real data.
  `concrete_binding_conflicts()` cross-checks metadata's top-down
  concrete bindings (variant A's `evidence` list; variant B's shadow
  `parent_requirement` + implementation-suffix form) against
  `concrete_results.json`'s self-declared `requirement_id`.
  `symbolic_binding_conflicts()` cross-checks each requirement's declared
  `implementation` file against the crosshair manifest's actual
  `target`. `run_conflict_gate()` combines both, Tier 1 (raises on any
  mismatch, matching fact-equality/structural-PROVEN's behavior).
- **Wired into `generate_artifacts.py`** as stage 3 (after capture
  integrity, before regeneration) — checked against all four metadata
  files: 20 bindings checked, 0 conflicts. Pipeline re-run end to end;
  regenerated artifacts differ only by `generated_utc` timestamp
  (deterministic regeneration confirmed).
- **`tests/test_conflict_check.py`** (7 tests): both ratified positive
  cases (variant A's `evidence` shape and variant B's shadow shape) as
  in-memory mutated fixtures reproducing the failure; the ratified
  negative case (REQ-GIP-1-4-12's kernel_scope/system_scope split) run
  against the real committed data, confirmed clean; a symbolic-file
  mismatch case; and a distinct-failure-mode check (a declared test_id
  that doesn't exist in the evidence store at all is a hard error, not a
  silently-passing conflict check, since there's no second claim to
  compare against).
- Variant C is untouched — it declares no top-down concrete binding, so
  Type 1 has nothing to compare there yet (Gate 4's known asymmetry,
  unchanged by this phase).
- Suite: 24 passed (17 prior + 7 new).
- Documentation updated to reflect BUILT status:
  `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md` (component map + Phase
  boundary), `README.md`, roadmap doc.
- **Not done this phase, staying open per the small-phases plan:** Type
  2 (outcome mismatch — needs a cross-manifest comparison mechanism that
  doesn't exist yet), the vocabulary-agnostic binder itself, and the CLI.

## 2026-07-06 — Gate 2 CONFLICT rule defined and ratified

Working session with Steven to define CONFLICT against the two candidate
test cases already on file, refine the definition, and lock it in.

- **Definition drafted:** CONFLICT requires two claims about the *same*
  `(requirement, scope)` and the same underlying verification act — never
  triggered by two legitimately different evidence types bound to one
  requirement, and never triggered by an `intent_ok` mismatch (that's a
  binding compared to its own stated intent, not two competing claims;
  already has its own mechanism, R1). Two sub-types identified:
  - Type 1 (identity mismatch): top-down and bottom-up claims about one
    binding disagree on target file/method — Gate 4's exact trigger.
  - Type 2 (outcome mismatch), added during review: two claims agree on
    target identity but disagree on what that identical run produced.
    Not hypothetical — motivated directly by this repo's own documented
    CrossHair model-fidelity non-determinism (Sample C / overflow-probe
    exhibits, Gate 3's caveat) that a same-invocation result can vary.
- **Tested against three cases:** positive Type 1 (dual-authorship
  file/method mismatch), negative (REQ-GIP-1-4-12 kernel_scope/
  system_scope split — a GAP, not a conflict, since there's no second
  claim to disagree with), positive Type 2 (a future duplicate manifest
  for an identical target reporting a different exit code).
- **Ratified by Steven** ("yep agree. lock in") — status moves from
  BLOCKED to DEFINED. Not yet built: Type 1 reuses Gate 4's intersection
  check directly; Type 2 needs a new cross-manifest comparison mechanism
  that doesn't exist yet. Building either into Gate 2's generalized
  binder is still open.
- `KNOWN_LIMITATIONS.md` rewritten fresh to reflect the current state of
  all six gates in one pass, rather than accumulating further patches.
  `payloadguard-evidence-roadmap-phaseB-to-C.md`, `SYSTEM_BLUEPRINT.md`,
  and `README.md` updated to match.
- Suite: 17 passed (unchanged — documentation only, no capture or
  generator touched).

## 2026-07-06 — Gate 3 closed by real test; Gate 6 (FRN) resolved; Gate 4 decision recorded; roadmap v2

Verification-first session, per the standing discipline: claims were
checked against actual repo/tool state before being written down,
including claims in the prompts supplied this session.

- **Pre-check on Defects 1/2 (mechanical-fixes prompt):** the prompt
  assumed these were possibly unpushed local commits. Checked for real:
  `5564fdf`/`1d9a260` exist on `main` locally and on `origin/main`
  (fetched and compared — identical, no divergence); DEVLOG already
  documented both under the 2026-07-05 "Gate 1 remediation" entry below.
  Rendered output verified directly (not just commit messages): all four
  variants show the scoped Notes fix and the REQ-GIP-1-4-12 kernel/system
  scope split correctly; suite 17 passed. No remediation needed — the
  prompt's premise didn't hold, and the mismatch was reported before
  proceeding rather than silently skipped or silently actioned.
- **Same-pattern discrepancy found in the roadmap-v2 prompt:** its "read
  first" section claimed FRN was "now closed." It was not — every
  in-repo reference (`KNOWN_LIMITATIONS.md`, `sources/README.md`,
  top-level `README.md`, `examples/dosage_calculator/README.md`) still
  read UNRESOLVED/BLOCKED. Flagged to Steven before proceeding; the
  roadmap v2 document (supplied afterward) carried the actual resolution
  to apply.
- **Gate 6 (FRN) — resolved and written up.** `FRN` = FDA Product Code
  for "Infusion Pump" (21 CFR 880.5725); within GIP's taxonomy, general-
  purpose volumetric infusion pumps (peristaltic, cassette-based),
  distinct from `All`. Source: NotebookLM extraction of the full source
  PDF, cross-checked against independent FDA-registry research. Caveat
  carried forward, not dropped: not yet independently re-verified against
  the raw Sec 2.4.1 text. Updated `sources/README.md` (open question →
  resolved question), `examples/dosage_calculator/README.md`,
  top-level `README.md`, `KNOWN_LIMITATIONS.md`.
- **Gate 3 — decided stay-CLI, by actually running the supplied
  verification script, not by trusting its writeup.** The roadmap's
  corrected seed-override technique (patch `make_default_solver`,
  hyphenated Z3 params) still had three bugs that only running it
  surfaced: (1) the roadmap's own claimed constructor,
  `AnalysisOptions(max_iterations=..., per_condition_timeout=...)`,
  raises `TypeError` on the installed 0.0.107 — `analyze_function` takes
  `AnalysisOptionSet`, not `AnalysisOptions`; (2) `crosshair.core` alone
  raises `CrossHairInternal("Opcode patches haven't been loaded yet.")`
  on `.analyze()` — must import from `crosshair.core_and_libs`; (3)
  `analyze_function` only returns parsed `Checkable`s, it doesn't run the
  solver — `.analyze()` must be called on each to get a real result. The
  uncorrected script "completed" in under a second and would have looked
  like a clean pass without ever invoking CrossHair's solver. After all
  three fixes, ran it for real, twice per target, seed 1 vs seed 2:
  `dosage.py::calculate_hourly_dose` gave byte-identical "Not confirmed"
  results both times; `dosage_broken.py::calculate_hourly_dose` (a
  stronger discriminator — it has real counterexamples) gave the exact
  same two counterexamples both times, matching the values already on
  file in `raw_crosshair_output_broken.txt`. No observed effect from the
  patch on either target tested. Decision: stay-CLI; `seed` documented as
  a tool-version limitation (tool-fixed at 42, hard-coded in
  `make_default_solver()`, not `StateSpace.__init__`, with hyphenated
  param names); `max_iterations` confirmed enforceable via
  `AnalysisOptionSet` independent of the seed question. Verification
  script committed at
  `examples/dosage_calculator/gate3_seed_patch_test.py`; nothing
  re-captured, Gate 1's committed evidence is untouched. Also closed as a
  non-issue: installed/pinned crosshair-tool is 0.0.107 in this
  environment (`pip show` confirmed), consistent with the toolchain pin;
  GitHub's latest *tag* trailing at 0.0.106 doesn't indicate a real
  discrepancy here.
- **Gate 4 — decision recorded (not built).** Option 3 (both binding-
  authorship models, cross-checked, Tier-1 failure on disagreement) is
  now the decision on record, with the dual-authorship top-down/bottom-up
  code-location-match mechanism specified. Building it is Gate 2's binder
  work.
- **Gate 2 — still blocked**, now with two candidate test cases on file
  for whatever CONFLICT definition eventually lands: a positive case
  (top-down/bottom-up binding disagreement under Gate 4's mechanism) and
  a negative case (REQ-GIP-1-4-12's kernel/system scope split, which is a
  documented absence, not a conflict).
- `payloadguard-evidence-roadmap-phaseB-to-C.md` replaced in place with
  the roadmap-v2 content (supersedes the 2026-07-05 morning version per
  its own text) plus the real Gate 3 result folded in.
- Suite: 17 passed (unchanged — no capture or generator touched this
  session).

## 2026-07-05 — Gate 1 remediation (two items from Steven's review)

Gate 1 review verdict received: fact-equality doing its job; two issues to
fix before Gate 2. Both fixed in generators/metadata — no generated file
hand-edited.

- **Item 2 (Tier 1 renderer defect):** variant C's method-filtered views
  were leaking the cross-evidence-type intent summary into their Notes,
  and the aggregate Notes section emitted once per table row (duplicate
  REQ-GIP-1-8-1 line in concrete.md). Fixed: `_view_notes()` scopes note
  text to the rendering view's evidence contribution (the intent_ok VALUE
  stays requirement-scoped per R1, never re-derived); `_md_notes()`
  de-duplicates by (requirement, note).
- **Item 1 (REQ-GIP-1-4-12 alarm scope):** evidence didn't match the
  requirement text — clamped output was verified, alarm emission never
  was. Steven's design decision (sources/req-gip-1-4-12-alarm-scope-
  decision.md, IEC 60601-1-8 ALARM CONDITION vs ALARM SIGNAL) implemented:
  metadata.yaml gains kernel_scope/system_scope on 1-4-12 (all four
  schemas extended with the optional fields; positive+negative
  revalidated for every variant); concrete test renamed
  over_max_clamps_exactly_to_max → kernel_detects_bolus_limit_exceeded
  and re-captured for real (4 passed); variant metadata re-derived;
  evidence rows for 1-4-12 reference the kernel_scope text; system_scope
  renders as an explicit named GAP in every view. GAPs are excluded from
  normalize_facts by rule (absence is not a fact) — fact-equality gate
  still PASS at 7 facts. Suite: 17 passed.
- Gates 2/3/4/6 untouched per the remediation prompt's "still open" list;
  the CONFLICT-vs-scope-GAP test question recorded in KNOWN_LIMITATIONS.

## 2026-07-05 — Deferred-gate work while Gate 1 output under review

Performed the deferrable gate processes without touching Gate 1's ground
truth (no re-capture, no artifact regeneration).

- **Gate 2 / CONFLICT rule — BLOCKED, named.** Retrieved
  PayloadGuard-Evidence-Blueprint-1 from Drive in full (committed to the
  repo with provenance header; Drive doc remains authoritative). The term
  CONFLICT appears nowhere in it (0 occurrences) nor in
  SYSTEM_BLUEPRINT.md (single to-do mention, no definition). Per roadmap:
  stopped, named, asking Steven. Closest neighbouring concept: Blueprint
  Phase 2 acceptance (b), intent mismatch "raises a GAP/flag".
- **Gate 3 — investigated, decision pending.** Verified against the
  installed package: per_condition_timeout CLI-enforceable (done in B1);
  max_iterations exposed by the Python API only
  (AnalysisOptions.max_iterations, default sys.maxsize); seed hard-coded
  to 42 in crosshair/statespace.py:750-751 — declared seed:1 is
  unenforceable at any interface on 0.0.107. Two wiring options recorded
  in KNOWN_LIMITATIONS; either requires re-capture, so the decision waits
  until Gate 1 review completes.
- **Gate 4 — options prepared** (metadata-authored / store-carried /
  both-with-cross-check, recommendation noted) for slotting into the Gate
  2 binder design. Design input recorded: the current C builder binds
  symbolic evidence to every requirement without verifying implementation
  against the capture target; the Gate 2 binder must bind by verified
  code-location match.
- **Gate 5 — resolved for the constructible half.**
  tests/test_single_evidence_type.py: in-memory symbolic-only fixture
  through the real variant C builder — appears in exactly one artifact;
  schema-c-validated; committed data untouched. Concrete-only fixture
  impossible pre-Gate-2 (see Gate 4 input). Suite: 17 passed.
- **Gate 6 — remains blocked** on a one-line FRN definition from Steven.

## 2026-07-05 (Turn B4) — Phase B Gate 1: end-to-end artifact generation

Phase B v3 prompt + roadmap received; roadmap committed verbatim as
`payloadguard-evidence-roadmap-phaseB-to-C.md`. Note for the record: the
prompt's B4/B5 spec bodies arrived as placeholders; B4 scope taken from
roadmap Gate 1 (minimal pipeline, four real variant artifacts as ground
truth, Steven review before Gate 2).

- `generate_artifacts.py`: five-stage end-to-end pipeline — (1) all four
  metadata files schema-validated, (2) capture integrity verified without
  re-running evidence (Sample A exit 0 + effective_bounds present, Sample
  B exit 1, concrete store clean), (3) regeneration + fact-equality gate
  via the B2 path (PASS, 7 facts), (4) structural PROVEN sweep over four
  variants plus frozen base, (5) `artifact_index.json` — SHA-256
  provenance binding 12 inputs to 8 outputs plus 10 frozen evidence files,
  with per-gate results. Any stage failure is a Tier 1 stop.
- `KNOWN_LIMITATIONS.md` created as the standing gate ledger: Gate 3
  (CrossHair API bounds) deferred — not hit in B4; Gate 4 (binding
  authorship) deferred to Gate 2's binder design; Gate 5 (single-evidence
  fixture) deferred as a Gate 2 test prerequisite; Gate 6 (FRN) blocked on
  a one-line definition from Steven; Phase C `verifier_completion_status`
  schema consideration noted for the Gate 2 binder.
- Suite: 15 passed. Gate 2 (vocabulary-agnostic binder + CONFLICT rule)
  not started — gated on Steven's review of the four real artifacts.

## 2026-07-05 09:46 UTC — Turn 2.0: bounds reconciliation, fact-equality gate, review protocol (678a3a5, 6347645, B3: this commit)

Three ratified rulings from the Q1–Q3 design review, executed in strict
order B1 → B2 → B3. Kernels untouched; exhibits frozen.

- **B1 (678a3a5, bounds):** `run_verify.py`/`run_verify_broken.py` now pass
  `--per_condition_timeout 30` (the one declared bound the 0.0.107 CLI can
  enforce) and record `effective_bounds` in the manifest — the single
  source of truth for what a run demonstrated. Samples A and B re-captured
  for real; raw outputs byte-identical to the previous captures. Generation
  gained a model-level `{declared, effective, enforcement_note}` bounds
  block, derived once (`derive_bounds_block`) and verified uniform across
  all four views. Exhibit captures/pins/runners byte-unchanged (frozen
  measurements). Ratified: metadata's declared triple kept — declared
  bounds are the bounds analogue of `intended_method`.
- **B2 (6347645, gate):** same-facts check mechanized.
  `evidence/reconcile.py` normalizes any matrix shape to fact tuples;
  `run_gate` asserts A/B/C fact equality, base-matrix = symbolic subset
  (frozen legacy view, ratified), intent uniformity, bounds-block
  uniformity. Enforced at generation time by `regenerate_all.py` (the
  sanctioned entrypoint; ratified that individual generators stay
  unchanged — a cross-artifact property cannot live inside one generator)
  and in the suite by `tests/test_fact_equality.py` (corruption cases
  mutate tmp copies only). Gate on real artifacts: PASS, 7 facts. Suite:
  15 passed.
- **B3 (this commit, protocol):** `REVIEW_PROTOCOL.md` codifies two-tier
  review: Tier 1 machine gates (fact-equality + structural PROVEN) stop
  defects and are never resolved by editing generated artifacts; Tier 2
  human review is per-reason over six structured finding classes.
  "Review only on validator disagreement" documented as void by
  construction. README pointer, BLUEPRINT invariants 8–9 and timestamp
  updated.

## 2026-07-04 18:52 UTC — Documentation pass: README, SYSTEM_BLUEPRINT, DEVLOG

- Root `README.md` populated (was an empty scaffold placeholder): purpose,
  non-goals, claims-discipline table including EXAMPLE_CHECKED, end-to-end
  flow, worked-example walkthrough, honesty exhibits, run instructions,
  known limitations.
- `SYSTEM_BLUEPRINT.md` created: component map, data-flow diagram,
  invariants (R1/R2 encoded), evidence inventory, Phase A/B boundary.
- `DEVLOG.md` created with the full dated history of the repository to date.
- No code, schema, kernel, or evidence changes in this session.

## 2026-07-04 16:40–16:42 UTC — Phase A closeout rulings (f5977d0, 96eaeee, d23689a)

Implemented the three rulings ratified after the Phase A audit. Kernels
untouched; one commit per ruling.

- **R1 (f5977d0):** `intent_ok` made requirement-scoped and derived exactly
  once at bind time (`derive_intent` in `matrix_variants.py`); all variant
  views carry it read-only, variant C assembles the full two-method model
  before filtering, variant B shadows project the parent value. Verified
  uniform across A / B parents / both C views (1-4-12 false, 1-8-1 false,
  DOSE-003 true). Same-facts check re-run: 7 facts, set-equal.
  RECONCILIATION asymmetry (1) closed; asymmetry (2) annotated deferred to
  Phase B.
- **R2 (96eaeee):** PROVEN rule made structural, not textual. Inline
  `intended PROVEN, realized …` notes restored (quoting authored metadata is
  fidelity). `assert_no_realized_proven()` fails generation if any realized
  strength equals PROVEN; committed as pytest over the four real artifacts
  plus in-memory corruption cases. Grep audit retired. Base Option A
  matrices untouched. Suite: 11 passed.
- **R3 (d23689a):** class-(2) incompleteness reframed: the IEEE-faithful
  channel exists but is unreliably sampled and sharply complexity-dependent
  (confirmed on the one-operation probe, silent on the four-parameter kernel
  under identical invocation; recorded bounds do not disclose the regime).
  Both exhibit pins' `mechanism_attribution` updated to match the README —
  verified identical modulo self-reference. Old "invisible" phrasing gone.

## 2026-07-04 16:15–16:26 UTC — Phase A completion T1–T4-C (0894da2…274115d)

- **T1 (0894da2):** BOUNDED_CHECKED incompleteness split into search-budget
  vs model-fidelity classes; CrossHair changelog cited (v0.0.72 real-valued
  float modelling, v0.0.58 nan/±inf as arguments only).
- **T2 (82a18a0):** naive-widening exhibit pinned
  (`exhibit_pin_naive_widening.json`): crosshair-tool 0.0.107, Python
  3.11.15, platform, exact invocation, mechanism attribution,
  version-contingency note.
- **T3 (d66162f):** domain-free `overflow_probe.py`. Expected a miss;
  CrossHair **confirmed** the violation (`double_it(8.98846567431158e+307)`
  → inf, exit 1). Recorded as-is, not re-rolled — paired with Sample C it
  measures the FP channel's width. Deterministic pytest companion added.
- **T4-0 (88bf755):** concrete evidence foundation — four requirement-mapped
  cases in `tests/test_dosage_concrete.py` (single CASES source), captured
  verbatim (pytest 4 passed) plus structured `concrete_results.json`.
  `Strength.EXAMPLE_CHECKED` added to the model.
- **T4-A/B/C (c2768da, 5745e0b, 274115d):** three parallel schema variants
  generated from identical evidence — A: evidence array per requirement
  (3 rows / 7 records); B: shadow pseudo-requirements with machine-enforced
  `parent_requirement` (7 rows); C: dual matrices partitioned by method
  (3 symbolic / 4 concrete rows), one filter-parametrised renderer.
  `RECONCILIATION.md`: programmatic same-facts confirmation (7 fact tuples)
  plus four recorded asymmetries. All schemas validated positive + negative.

## 2026-07-04 15:34 UTC — Option A amendment (b090d54)

Post-ship review found REQ-GIP-1-8-1's verification vacuous: the
`infusion_rate_ml_per_hr >= 0` precondition made the negative-dose clamp
dead code, so the postcondition's lower bound held by algebra. Applied
Option A: precondition widened to any finite rate (negative models the GIP
SR 1.8.1 single-fault reverse flow), directional postcondition added
(negative rate ⇒ return exactly 0.0), and the negative check reordered
before the finiteness check — a naive widening would have returned the
MAXIMUM dose on a −inf overflow. The naive variant and its real CrossHair
capture (exit 0 — the violation was NOT found) were committed deliberately
as the honesty exhibit. Sample B re-capture now shows a second, negative
counterexample, proving the widened domain is genuinely explored. Matrices
regenerated; 2× intent_ok false / 1× true preserved.

## 2026-07-04 14:47 UTC — Phase A initial build (9ca085a)

Repository scaffolded (empty skeleton, then populated per the Phase A
prompt) and pushed to `PayloadGuard-PLG/payloadguard-evidence`:

- `evidence/model.py` (Strength enum, CAVEAT map, dataclasses; Dafny
  false-zero parser note carried for Phase B), `evidence/schema/
  metadata.schema.json` (draft 2020-12, unknown-key rejection,
  crosshair_bounds required), `evidence/render/manual_matrix.py`
  (hand-reviewed binder/renderer).
- `examples/dosage_calculator/`: dose-clamping kernel with PEP316 contracts;
  Sample A (clean, exit 0) and Sample B (broken, exit 1 with concrete
  counterexample) captured by real CrossHair 0.0.107 runs;
  `metadata.yaml` sourced from GIP v1.0 with three requirements;
  matrices generated (not hand-typed) showing intended-PROVEN vs realized-
  BOUNDED_CHECKED mismatches honestly.
- `sources/`: GIP v1.0 hazard analysis archived verbatim + standing rule for
  future source documents. FRN pump-type tag left explicitly unresolved
  after a failed resolution attempt (web search; UPenn pages unreachable).
- Known bounds divergence (declared vs effective CrossHair bounds) flagged,
  not smoothed over. Nothing in the repo asserts PROVEN as realized.
