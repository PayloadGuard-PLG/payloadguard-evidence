# Handoff — read this first

For a new session picking this repo up cold. Answers "what is this,
what's actually done, and what's the very next thing to do" without
requiring you to reconstruct it from `DEVLOG.md`'s full history.
Updated at the end of a work session, not continuously — check its own
"Last updated" line against `DEVLOG.md`'s top entry; if `DEVLOG.md` has
newer entries this file doesn't reflect, trust `DEVLOG.md` and update
this file to match before relying on it further.

**Last updated:** 2026-07-11 — `renal_adjustment.dfy`'s Gate C6 sign-off
is now confirmed and closed. Steven reviewed the six checkpoints from
`nl_confirmation_renal_adjustment_dfy.md` (RoundHalfUp's tie-break
framing, GStage's boundaries, SelectFormula's BMI thresholds, the Gate
C4 pinning fixes, and the eGFR/CrCl split's forced asymmetry) against
the raw KDIGO/MHRA sources directly — every checkable claim
independently re-verified against the real committed source files and
live Dafny re-runs (both Pow-expressiveness probes re-run: still fail /
still verify exactly as established; the STP suite re-run: `52 verified,
0 errors`, unchanged) before being recorded. **One citation flagged, not
silently absorbed**: a supporting claim about "Sheffield and BSW"
clinical calculator sources corroborating the 88.4 conversion factor
could not be verified — no such source exists anywhere in this
repository. Not treated as confirmed; the underlying claim it was
attached to didn't depend on it and was already independently
established via a direct MHRA source re-fetch in an earlier session. See
`nl_confirmation_renal_adjustment_dfy.md`'s Decision section for the
full account. **`renal_adjustment` now has all six Gate C1–C6 pipeline
steps both built and confirmed** — the only remaining items are the
named, deliberately unbuilt requirements (`REQ-RENAL-3`, `REQ-RENAL-4`,
`REQ-RENAL-6`, `REQ-RENAL-7`; `REQ-RENAL-8`'s classification-flag
provenance question, reclassified as a Phase 3 concern).

**Prior update, preserved: 2026-07-10**, while walking through Gate C6's
actual sign-off review with Steven. Before confirming, he pushed on
whether the
closing claim for Gate 1c Finding 1 ("eGFR caller-supplied because
Dafny/Z3 can't express it") was actually earned by the evidence, not
just asserted — it wasn't: the prior "confirmed" was circular between
`GATE_1C_AUDIT.md` and a sources doc, neither containing a real test.
Tested for the first time with two committed probes
(`examples/renal_adjustment/run_verify_pow_probes.py`): Dafny has no
real-exponentiation primitive at all, and the obvious axiom workaround
verifies trivially even for an absurd, wrong claim about it — see
`GATE_1C_AUDIT.md`'s 2026-07-10 addendum. **This is the pattern to
repeat: before signing off Gate C6 on any spec, check whether every
claim the spec's comments make was actually tested, not just carried
forward as reasoning that sounded right the first time.** Gate C6
sign-off itself is still open pending Steven's read-through of
`nl_confirmation_renal_adjustment_dfy.md` — this strengthened the
evidence behind one of its closing claims, it didn't close the gate.

**Same-day addendum:** two follow-up items closed. `SYSTEM_BLUEPRINT.md`
and `KNOWN_LIMITATIONS.md` had themselves drifted behind this exact
2026-07-10 entry (still said 2026-07-09) — fixed with a real content
review, plus a new mechanical test
(`tests/test_docs_current_with_devlog.py`) so that specific drift can't
recur silently. A pytest CI job (`.github/workflows/tests.yml`) was also
added, alongside the existing PayloadGuard scan — see the "Working
conventions" section below, which was itself corrected at the same time
(it still said "no CI is configured on this repo").

**Second same-day addendum: a third worked example started.**
`examples/drug_interaction_checker/` (NHS SPS DOAC-interaction
guidance, testing whether the pipeline generalizes to set/list-
membership logic) went through Gate 1a (sourced), Gate 1c (three real
findings — a dropped risk-direction axis, a `CheckInteraction` function
non-total over its own declared `Agent` type, two genuinely ambiguous
source cells — all resolved by explicit decision, none deferred), and
Gate C1 (spec + capture, verifies clean). **Gate C1 caught a real
false-clean result before it was committed:** an early draft with no
`ensures` clauses reported "0 verified, 0 errors" — not a pass, a sign
Dafny had nothing to actually prove (match-exhaustiveness is a
resolve-time syntax check, not an SMT proof). Fixed by adding three
real `ensures` clauses before committing anything. See
`examples/drug_interaction_checker/PHASE1_PLAN.md`,
`GATE_1C_AUDIT.md`, and `KNOWN_LIMITATIONS.md`'s "Phase E Gate C1"
section for the full account.

**Third same-day addendum: Gate C4 found the Gate C1 fix was itself
only a stopgap, then Gate C3 required real engineering, not just
application.** Gate C4 (STPs): a real IronSpec ACCEPT lemma restating
just the 3 `ensures` clauses Gate C1 added failed to prove the correct
value for cells they didn't directly mention — confirmed with a real
failing capture (`0 verified, 3 errors`), preserved as a proper honesty
exhibit before fixing anything. Fixed with 60 comprehensive pinning
`ensures` clauses plus a real 11-lemma ACCEPT/REJECT STP suite (Dafny's
own capture reads `22 verified, 0 errors` — ~2 verification tasks per
lemma, not a 1:1 lemma count, corrected 2026-07-10 after this line and
several other docs previously misread it as "22 lemmas"). Gate
C3: `CheckInteraction`'s precondition compares `doac`/`agent` directly
against datatype constructors — `evidence/dafny_spec_lint.py`'s Z3
translator genuinely refused this (a real gap, not renal_adjustment's
narrower "unreferenced parameter" one) until extended to model simple
Dafny datatypes as a Z3 `EnumSort`. Caught a second, independent,
generally-applicable bug while testing the extension: Z3 registers
`EnumSort` names globally per process, so two callers modeling a
same-named type collide — fixed with a per-call disambiguating tag.
Full accounts: `KNOWN_LIMITATIONS.md`'s "Phase E Gate C4"/"Phase E Gate
C3" sections.

**Fourth same-day addendum: Gate C2 confirmed, no new gap.** Unlike
C3/C4, this one found nothing broken — it confirmed
`evidence/render/matrix_variants.py::dafny_record()`/
`assert_no_realized_proven` (built 2026-07-07, tested thoroughly
against `dosage_calculator`) actually works against an independently-
authored spec's real capture, the first time since `dosage_calculator`
itself (`renal_adjustment` never reached this point — no `metadata.yaml`
was ever built for it). Run for real: produces a genuine PROVEN record,
accepted cleanly by R3; two negative-case checks (tampered `method`,
tampered `verifier_completion_status`) confirm R3 still independently
refuses, not just trusting the binder's own diligence. See
`KNOWN_LIMITATIONS.md`'s "Phase E Gate C2" section. Gates C5/C6 not
started yet.

**Fifth same-day addendum: Gate C5 built, found and fixed a real crash
bug in Gate C3's own code, then 7 real survivors.** 962 mutants
(ROR/LOR/COI; AOR/LVR both confirmed contributing zero — no arithmetic
operator or numeric literal anywhere in `CheckInteraction`). **A real
crash, not a Dafny finding, caught mid-run**: a ROR mutant introducing
`<=`/`>=` between two `DOAC` datatype operands crashed
`evidence/dafny_spec_lint.py`'s Z3 translator with a raw Python
`TypeError` — Z3's Python bindings don't overload ordering operators for
`DatatypeRef` the way they do for `==`/`!=`. Fixed in `_apply_cmp` (a
`z3.is_arith` guard, refusing cleanly via `SystemExit` instead of
crashing) — a shared-module fix, shipped as its own PR before the full
mutation run could even complete. Final real run: **564 killed, 389
filtered_static, 7 survived, 2 unclassifiable.** The 2 unclassifiable
are genuine Dafny type errors on `<=`/`>=` between `DOAC` values — a
materially different failure mode from `renal_adjustment`'s own
unclassifiable case (a parser ambiguity, not a type error). The 7
survivors fall into the same two structural categories
`renal_adjustment`'s own Gate C5 already established — no new category
of finding: 4 mutate the one `requires` clause's `doac == Apixaban`
comparison (not load-bearing for any of the 60 `ensures` clauses); 3
mutate one `ensures` clause's `doac == Dabigatran` antecedent (the
consequent is independently guaranteed for the other three DOACs by
sibling clauses, confirmed directly against the real spec text). An
earlier draft's prediction that ordering comparisons on datatype values
would be "always killed" was wrong — corrected in place in
`run_mutation_suite_ddi.py`'s own comments, left visible rather than
silently rewritten. See `KNOWN_LIMITATIONS.md`'s "Phase E Gate C5"
section. Gate C6 is the only gate left unbuilt for this example.

**Sixth same-day addendum: Gate C6 built, genuinely extended the shared
NL-summary generator — a different call than `renal_adjustment`'s own
equivalent gap.** `evidence/dafny_nl_summary.py::summarize_method`
refused outright on first attempt: `CheckInteraction`'s one `requires`
clause spans three physical lines, the first genuinely multi-line clause
this repo has pointed the summary generator at (every clause in
`dosage.dfy`/`renal_adjustment.dfy` happened to be one line).
`renal_adjustment` hit an equivalent gap for two `ensures` clauses and
that time the fix was to reformat them to single-line rather than extend
the tool ("a formatting choice that was mine, not a genuine spec need").
**This time the call went the other way, for a concrete reason**: this
spec already had committed Gate C1/C4/C5 captures bound to its current
formatting, so a cosmetic reformat would have meant re-running and
re-committing all three for a change with zero semantic content. Fixed
instead by making `_extract_annotated_clauses` accumulate a clause
across multiple physical lines — ending accumulation at a blank line, a
standalone `//`-comment line, or the next clause keyword, so a
free-floating block comment between two clauses (this spec has several)
is never misattributed as either clause's citation. The original
single-line regex is preserved unchanged, since `dafny_mutate.py`
imports it for a different, byte-precise need this extension didn't
touch. The safety net is unchanged in spirit: still cross-checks against
`dafny_spec_lint`'s canonical extractor and refuses on any mismatch — a
comment sitting on its own line *inside* a multi-line clause (as opposed
to between two clauses) still correctly refuses, genuinely ambiguous,
confirmed by a new regression test. Verified end-to-end: all 60
`ensures` clauses and the one multi-line `requires` clause reconstruct
byte-for-byte correctly. **A real, notable fact this summary surfaces,
not a defect**: none of `CheckInteraction`'s 60 `ensures` clauses carry
an inline `REQ-DDI-*` citation — unlike `dosage.dfy`/`renal_adjustment.dfy`'s
per-clause style, this spec is validated as a whole lookup table, so
every `*(no requirement cited)*` is accurate, flagged explicitly for
Steven to confirm at sign-off. Presented in
`examples/drug_interaction_checker/nl_confirmation_drug_interaction_checker_dfy.md`.
3 new/changed
tests in `tests/test_dafny_nl_summary.py`, 190 total (up from 188). See
`KNOWN_LIMITATIONS.md`'s "Phase E Gate C6" section.

**Seventh same-day addendum: Gate C6 sign-off confirmed by Steven —
against the raw source directly, and it caught a real doc-accuracy bug
in the sign-off document's own text along the way.** Not a rubber
stamp: Steven checked the sign-off document's four numbered items
against `sources/sps-doac-interactions-2024.md` directly and found item
1 mislabeled the precondition's exclusion as apixaban's "real source
gap" — that phrase belongs to a different, genuinely-silent cell
(apixaban+dronedarone), already correctly labeled that way in both the
`.dfy` spec and the STP suite. The precondition's actual exclusion
(`Apixaban` + `{Rifampicin, Carbamazepine, Phenytoin, Phenobarbital}`)
is indication-dependent, not silence — confirmed verbatim against source
lines 80-84/135-136: "use apixaban with caution" for two named
indications, an explicit branch v1 doesn't model (`REQ-DDI-5`). Fixed in
the sign-off document (no `.dfy` change needed — the precondition was
always correct, only the rationale needed tightening). Every other
sign-off item was independently re-verified against the real source, not
taken on faith, and a programmatic cross-reference confirmed the 60
`ensures` clauses, the NL summary, and the STP suite's 11 lemmas are
mutually consistent. Full account: `KNOWN_LIMITATIONS.md`'s "Phase E
Gate C6 sign-off" section. **All six Gate C1–C6 pipeline steps have now
been built AND confirmed for this example — Gate C6 is closed.** What
remains is only the explicitly out-of-scope v2 items
(`REQ-DDI-5`/`REQ-DDI-6`).

## What this repo is, in one paragraph

Turns real verification tool output (CrossHair, Dafny/Z3) plus authored
metadata into IEC 62304/FDA §524B traceability artifacts, where every
claim is bound to a committed, replayable evidence record of honestly-
labeled strength — `PROVEN` can never appear unless a real, completed
Dafny proof produced it. Full explanation: `README.md` (plain-English)
and `OPERATIONS_MANUAL.md` (technical reference — read this one if
you're about to build something, not just read about the system).

## Current state of all three worked examples

**`examples/dosage_calculator/` — complete.** Every requirement carried
through source citation → formal spec → mathematical proof → mutation
testing → recorded human sign-off. Nothing pending here. Don't touch it
unless something new demands it — it's the reference implementation the
second example was built to prove the pipeline generalizes to.

**`examples/renal_adjustment/` — Phase 2 done: all six Gates C1–C6
built AND confirmed.** Read `examples/renal_adjustment/PHASE1_PLAN.md`
top to bottom before touching this example — it's the living status
document for this example specifically and is kept current, unlike this
handoff file's example-agnostic summary. As of this writing:

- Gate 1 (clinical sourcing, spec skeleton, consistency audit) is
  closed under one remaining named, deliberately provisional fallback
  assumption (the CrCl/eGFR one below is now closed for Cockcroft-Gault)
  — see `PHASE1_PLAN.md`'s "Closed under named fallback assumptions"
  section.
- `renal_adjustment.dfy` exists, is committed, and verifies (`7
  verified, 0 errors`) — seven functions: `RoundHalfUp`, `GStage`,
  `SelectFormula`, `ComposedCeiling`, `AssessRenalFunction`,
  `CockcroftGaultCrClMlPerMin`, `AssessRenalFunctionFromInputs`.
- **Gate C6 (NL confirmation) confirmed and closed, 2026-07-11.** The
  sign-off document (`nl_confirmation_renal_adjustment_dfy.md`) — three
  amendments (two functions fixed 2026-07-09, two functions added
  2026-07-09) plus the original seven-function summary — was reviewed
  by Steven against the raw KDIGO/MHRA sources directly, not rubber-
  stamped: every checkable claim independently re-verified against the
  real source files and live Dafny re-runs before being recorded. One
  unverifiable supporting citation ("Sheffield and BSW" sources) was
  flagged, not silently absorbed — see the Decision section for the
  full account.
- Gate C4 (STPs) is built and found + fixed two real gaps for real
  (`ComposedCeiling`, `AssessRenalFunction` both needed pinning
  clauses) — see `gate_c4_stp_plan.md` and the `_underconstrained`/
  `_stp_suite_against_underconstrained` honesty-exhibit files. Extended
  2026-07-09 with real ACCEPT/REJECT lemma coverage for the two new
  functions below (`52 verified, 0 errors`, up from 44).
- **Gate C3 (spec lint) built 2026-07-09** — all seven functions pass
  vector 1 (satisfiable preconditions); five have expected vector 2
  warnings (one-way `==>` clauses, all STP-covered). Found and fixed a
  real gap: the checker used to build a Z3 symbol for every declared
  parameter regardless of use, refusing on `AssessRenalFunction`'s
  unused `Formula`-typed parameter — narrowed to only model referenced
  parameters.
- **Gate C5 (mutation testing) built 2026-07-09** — 450 mutants across
  all seven functions, 51 survivors, all explained and categorized (not
  a proof gap — see `examples/renal_adjustment/README.md`'s Gate C5
  amendment for the three named categories), plus two named engine
  limitations (a `||`-chain ambiguity, two arithmetic-embedded LVR
  literals) deliberately not fixed — real new engineering, and Gate C4's
  STPs already cover what they'd add. Four real engine gaps found and
  fixed along the way (missing tokenizer chars, int/real literal typing)
  — see `run_mutation_suite_renal.py`'s module docstring.
- **All six Gate C1–C6 pipeline steps are now built and confirmed —
  this example's Phase 2 is done.** What remains: the named,
  deliberately unbuilt requirements (`REQ-RENAL-3`, `REQ-RENAL-4`,
  `REQ-RENAL-6`, `REQ-RENAL-7`) and `REQ-RENAL-8`'s classification-flag
  provenance question (reclassified as a Phase 3 concern, not a Phase 2
  blocker).

**`examples/drug_interaction_checker/` — Phase 2 underway, all six
Gates C1–C6 built or confirmed.** Read
`examples/drug_interaction_checker/PHASE1_PLAN.md` top to bottom before
touching this example. Third worked example, testing whether the
pipeline generalizes to **set/list-membership logic** — sourced from
NHS SPS's DOAC-interaction guidance, UK-jurisdiction like
`renal_adjustment`. As of this writing:

- Gate 1a (clinical sourcing) closed: single primary source, chosen
  after direct comparison against BNF/MHRA DSU (bounded, versioned,
  publicly fetchable, states its own scope boundary explicitly).
- Gate 1c (consistency audit) closed: three real findings — a dropped
  risk-direction axis, a `CheckInteraction` function non-total over its
  own declared `Agent` type, two genuinely ambiguous source cells — all
  resolved by explicit decision, none deferred (unlike `renal_adjustment`'s
  own Finding 1, which was deliberately left open).
- `drug_interaction_checker.dfy` exists, is committed, and verifies (`1
  verified, 0 errors`) — `CheckInteraction`, 63 match arms across 15 v1
  agents, 60 pinning `ensures` clauses (one per match arm).
- **Gate C1's first draft had a real false-clean result, caught before
  committing:** an early version with no `ensures` clauses reported "0
  verified, 0 errors" — Dafny had generated zero verification tasks,
  not zero problems.
- **Gate C4 then found the fix was itself only a stopgap, and this time
  the gap was real and much bigger — confirmed with a genuinely failing
  captured run, not just predicted.** The 3 `ensures` clauses Gate C1
  first added didn't pin almost anything: a real IronSpec ACCEPT lemma
  restating just those 3 clauses failed to prove the correct value for
  `(Dabigatran, Ketoconazole)` — and 3 more such lemmas, preserved
  against `drug_interaction_checker_underconstrained.dfy`, genuinely
  fail as a committed capture (`0 verified, 3 errors`). Fixed for real
  by pinning all 63 cells explicitly, then building a real 11-lemma
  ACCEPT/REJECT STP suite (`22 verified, 0 errors` — ~2 verification
  tasks per lemma, not a 1:1 count) with REJECT coverage for the three
  `Contraindicated` cells specifically. See `KNOWN_LIMITATIONS.md`'s
  "Phase E Gate C1"/"Phase E Gate C4" sections for the full account —
  worth reading before assuming a clean `dafny verify` pass on any
  future function means something was actually checked, or that adding
  *some* `ensures` clauses means enough were added.
- **Gate C3 then required genuinely extending shared tooling, not just
  running it.** `evidence/dafny_spec_lint.py`'s Z3 translator refused
  `CheckInteraction`'s precondition outright (`doac == Apixaban`
  compares a datatype value directly — a real gap this repo's earlier
  worked examples never hit, since `renal_adjustment`'s one
  datatype-typed parameter was never referenced by any precondition).
  Fixed by modeling simple, zero-argument-constructor Dafny datatypes as
  a Z3 `EnumSort` — a real, if narrower-than-originally-feared,
  extension. Caught a second, independent bug while testing it: Z3
  registers `EnumSort` names globally per process, not per call, so two
  callers modeling a same-named type collide — fixed with a per-call
  disambiguating tag that protects every future caller, not just this
  one. See `KNOWN_LIMITATIONS.md`'s "Phase E Gate C3" section.
- **Gate C2 confirmed, no new gap this time.** The PROVEN-exclusivity
  binder (`dafny_record()`/`assert_no_realized_proven`, built
  2026-07-07) had never been run against anything but
  `dosage_calculator`'s captures — `renal_adjustment` never got a
  `metadata.yaml`, so it never exercised this path at all. Run for real
  against this example's capture: produces a genuine PROVEN record,
  accepted cleanly; two negative-case checks confirm R3 still
  independently refuses tampered records shaped like this one, not just
  trusting the binder. See `KNOWN_LIMITATIONS.md`'s "Phase E Gate C2"
  section.
- **Gate C5 (mutation testing) built** — 962 mutants (ROR/LOR/COI; AOR/
  LVR confirmed contributing zero). Found and fixed a real crash bug in
  `evidence/dafny_spec_lint.py`'s `_apply_cmp` along the way (ordering
  operators on datatype/`EnumSort` operands weren't modeled by Z3's
  Python bindings, crashed instead of refusing cleanly) — shipped as its
  own PR. Final: 564 killed, 389 filtered_static, 7 survived (both
  explained categories already established by `renal_adjustment`'s own
  Gate C5), 2 unclassifiable (genuine Dafny type errors, a different
  failure mode from `renal_adjustment`'s parser-ambiguity case). See
  `KNOWN_LIMITATIONS.md`'s "Phase E Gate C5" section.
- **Gate C6 (NL-dialogue confirmation) built.** Refused on first
  attempt — `CheckInteraction`'s one `requires` clause is the first
  genuinely multi-line clause this repo has pointed
  `evidence/dafny_nl_summary.py::summarize_method` at. Fixed by
  genuinely extending the tool to accumulate a clause across multiple
  physical lines (a deliberately different call than `renal_adjustment`'s
  own equivalent gap, which was fixed by reformatting the spec instead —
  this spec already had Gate C1/C4/C5 captures bound to its current
  formatting, so reformatting would have meant re-committing all three
  for a cosmetic change). Verified end-to-end against the real spec;
  presented for sign-off in
  `nl_confirmation_drug_interaction_checker_dfy.md` — **confirmed by
  Steven, against the raw source directly**, which caught and fixed a
  real doc-accuracy bug in the sign-off document's own text (item 1
  mislabeled an indication-dependent precondition exclusion as apixaban's
  "source gap" — the precondition itself was always correct). See
  `KNOWN_LIMITATIONS.md`'s "Phase E Gate C6 sign-off" section.
- **All six Gate C1–C6 pipeline steps built and confirmed for this
  example — Gate C6 is closed.** What remains:
  two explicitly out-of-scope v2 items, not built:
  `REQ-DDI-5` (an indication-dependent axis for two agents' apixaban
  cells) and `REQ-DDI-6` (proving the specific numeric dose-reduction
  targets, staged as v2 — "both but in order of difficulty").

## One thing explicitly left open, not forgotten

1. **Classification-flag provenance** (`REQ-RENAL-8`): who sets
   `SelectFormula`'s caller-supplied boolean flags, by what process.
   Reclassified as a Phase 3 integration concern, not a Phase 2 proof
   blocker — doesn't block the Dafny work, but is a real open item for
   whenever Phase 3 (evidence packaging) starts.

**Closed, 2026-07-09 — CrCl/eGFR value computation** (Gate 1c "Finding
1"): Cockcroft-Gault CrCl is now computed
(`CockcroftGaultCrClMlPerMin`/`AssessRenalFunctionFromInputs`, both
verified and STP-covered). CKD-EPI eGFR stays caller-supplied — Steven's
framing, confirmed correct: "if we have to tie to specific software then
if we physically cannot at the moment, then the choice is made for us"
— Dafny/Z3 genuinely cannot express CKD-EPI's real-valued fractional
exponents on a variable base, so that half was never actually a choice.
**This was only an asserted claim until 2026-07-10** — direct challenge
before Gate C6 sign-off ("can we actually make this claim with the
evidence we have?") found the prior "confirmed" was circular between
two docs, neither containing a real test. Now empirically demonstrated:
`examples/renal_adjustment/run_verify_pow_probes.py` shows Dafny has no
real-exponentiation primitive at all, and that the obvious axiom
workaround verifies trivially even for an absurd, wrong claim — see
`GATE_1C_AUDIT.md`'s 2026-07-10 addendum.
Closing this also re-verified the MHRA and NICE NG203 source URLs
(both unchanged since 2026-07-08) and caught a real, minor attribution
error along the way: earlier notes called the derived 1.23/1.04
multiplier "MHRA's constants" when MHRA's page states no formula or
constant at all — see `GATE_1C_AUDIT.md`'s 2026-07-09 addendum and
`sources/mhra-renal-formula-selection-2019.md`'s amendment.

## A standing discipline, learned the hard way more than once this build

- **Verify empirically before trusting a claim, including your own
  claims and this repo's own prior claims.** The infrastructure plan
  predicted Gate C6's tooling "generalizes for free" to
  `renal_adjustment.dfy` — it didn't; `_find_method_header` only
  matched Dafny's `method` keyword, never `function`, because the first
  worked example always had both and the gap was untested until the
  second example actually exercised it. Small real fixes to shared code
  are normal and expected when a second example stresses a different
  shape — that's the point of having a second example.
- **External "research findings" documents have contained fabricated
  citations, more than once, including a repeat of the same fabrication
  across two separate documents.** Use `evidence/citation_gate.py`
  (built specifically for this) to mechanically check any claimed quote
  against real source text before trusting it — it won't catch
  everything (it can't fetch sources itself, and it just had its own
  real false-positive bug fixed — see `DEVLOG.md`'s 2026-07-09 audit
  entry), but it's a real, tested first line of defense, not a
  suggestion.
- **A clean `dafny verify` pass proves the spec is internally
  consistent, not that it says what you think it says.** Both real gaps
  Gate C4 found in `renal_adjustment.dfy` verified perfectly clean
  before being caught — the postconditions bounded a result without
  pinning it to an exact value. Write the STP before trusting a clean
  pass at face value.
- **"0 verified, 0 errors" is not the same claim as "N verified, 0
  errors" for N > 0 — check which one a capture actually says before
  calling a gate built.** `drug_interaction_checker.dfy`'s first draft
  had no `ensures` clauses and reported exactly this: zero errors
  because there was nothing to disprove, since Dafny generates zero
  verification tasks for a function with no postconditions
  (match-exhaustiveness is a resolve-time syntax rule, not an SMT
  proof). Caught before committing by actually reading the count, not
  just the "0 errors" half of the line.
- **Adding *some* `ensures` clauses isn't the same as adding *enough* —
  Gate C4 exists precisely to test that, and it found a real gap even
  right after Gate C1's own fix above.** The 3 clauses added to fix the
  "0 verified" problem were real, but only covered 3 of 63 match arms;
  a genuine IronSpec ACCEPT lemma restating just those 3 as premises
  still failed for every other cell, confirmed with a real committed
  failing capture (`0 verified, 3 errors`), not assumed from the fact
  that the main file itself verified clean. A clean `dafny verify` on
  the function being specified says nothing about whether cells outside
  its `ensures` clauses are actually guaranteed — only Gate C4's
  spec-only lemmas test that directly.
- **Hand-derive a prediction before building, especially for mutation
  testing and STPs.** Every extension in this repo's history that did
  this caught something real or confirmed its own reasoning explicitly,
  rather than discovering after the fact whether the approach worked.
- **Never hand-edit a generated artifact.** If a traceability matrix or
  report looks wrong, the metadata or capture it came from is wrong —
  fix that, regenerate.
- **A generator that happily produces a mutant doesn't mean the
  translator underneath can actually evaluate it.** Gate C5's ROR
  generator has no reason to know `evidence/dafny_spec_lint.py`'s Z3
  translator can't handle an ordering operator between two datatype
  values — it generated the mutant anyway, and the translator crashed
  with a raw Python `TypeError` instead of refusing cleanly like every
  other unsupported construct. Mutation testing exercises shared tooling
  in combinations its own test suite never tried; treat a crash found
  this way as a real bug in the shared module, not a mutation-suite
  quirk to work around locally.
- **Full review discipline:** `REVIEW_PROTOCOL.md`. **Full known-gap
  ledger:** `KNOWN_LIMITATIONS.md`. **Full dated history:** `DEVLOG.md`
  — this handoff file is a summary, not a replacement for it.

## Working conventions specific to this environment

- Tests: `python -m pytest tests/ -q` — must pass before any commit.
  190 as of this writing.
- Dafny 4.11.0 / Z3 are installed; `dafny verify <file>.dfy` works
  directly.
- Branch workflow used this session: create a `claude/<topic>` branch
  off `main`, commit there, open a PR. **Two CI checks now run on every
  PR into `main` (added 2026-07-10, both real — this line was stale
  before that and said "no CI is configured," "0 checks"):**
  `.github/workflows/tests.yml` (`python -m pytest tests/ -q`) and
  `.github/workflows/payloadguard.yml` (third-party pre-merge scan —
  see `KNOWN_LIMITATIONS.md`'s "PayloadGuard CI gate" entry). **Branch
  protection now requires human approval before merge** — open the PR,
  let both checks run, then stop and wait; don't auto-merge even once
  CI is green. `main` is the live, current state; feature branches are
  short-lived and not meant to accumulate.
- Every real tool run (Dafny, CrossHair, pytest) gets its raw output
  and a manifest committed verbatim — never re-typed, never smoothed
  over if the result is unexpected.
