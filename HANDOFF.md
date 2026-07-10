# Handoff — read this first

For a new session picking this repo up cold. Answers "what is this,
what's actually done, and what's the very next thing to do" without
requiring you to reconstruct it from `DEVLOG.md`'s full history.
Updated at the end of a work session, not continuously — check its own
"Last updated" line against `DEVLOG.md`'s top entry; if `DEVLOG.md` has
newer entries this file doesn't reflect, trust `DEVLOG.md` and update
this file to match before relying on it further.

**Last updated:** 2026-07-10, while walking through Gate C6's actual
sign-off review with Steven. Before confirming, he pushed on whether the
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
section for the full account. Gates C2–C6 not started yet.

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

**`examples/renal_adjustment/` — Phase 2 in progress, Gates C1/C4/C6
built, Gates C3/C5 not yet started.** Read `examples/renal_adjustment/PHASE1_PLAN.md`
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
- Gate C6 (NL confirmation) is built; the sign-off document
  (`nl_confirmation_renal_adjustment_dfy.md`) is presented but its
  "Decision" section is **pending Steven's actual confirmation** — it
  has not been rubber-stamped, don't treat it as closed. Now has three
  amendments (two functions fixed 2026-07-09, two functions added
  2026-07-09) all awaiting the same one sign-off.
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
- **The only thing left before this example's Phase 2 is done: Gate
  C6's sign-off.** Everything else is built.

**`examples/drug_interaction_checker/` — Phase 2 just started, Gate C1
built, Gates C2–C6 not yet started.** Read
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
  agents.
- **A real false-clean result caught before committing, not after:** an
  early draft with no `ensures` clauses reported "0 verified, 0
  errors" — Dafny had generated zero verification tasks, not zero
  problems. Fixed by adding three real `ensures` clauses. See
  `KNOWN_LIMITATIONS.md`'s "Phase E Gate C1" section for the full
  account — worth reading before assuming a clean `dafny verify` pass
  on any future function means something was actually checked.
- Gates C2–C6 not started. Two items named, not built: `REQ-DDI-5`
  (an indication-dependent axis for two agents' apixaban cells) and
  `REQ-DDI-6` (proving the specific numeric dose-reduction targets,
  staged as v2 — "both but in order of difficulty").

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
- **Hand-derive a prediction before building, especially for mutation
  testing and STPs.** Every extension in this repo's history that did
  this caught something real or confirmed its own reasoning explicitly,
  rather than discovering after the fact whether the approach worked.
- **Never hand-edit a generated artifact.** If a traceability matrix or
  report looks wrong, the metadata or capture it came from is wrong —
  fix that, regenerate.
- **Full review discipline:** `REVIEW_PROTOCOL.md`. **Full known-gap
  ledger:** `KNOWN_LIMITATIONS.md`. **Full dated history:** `DEVLOG.md`
  — this handoff file is a summary, not a replacement for it.

## Working conventions specific to this environment

- Tests: `python -m pytest tests/ -q` — must pass before any commit.
  171 as of this writing.
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
