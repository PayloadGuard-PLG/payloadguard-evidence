# Handoff — read this first

For a new session picking this repo up cold. Answers "what is this,
what's actually done, and what's the very next thing to do" without
requiring you to reconstruct it from `DEVLOG.md`'s full history.
Updated at the end of a work session, not continuously — check its own
"Last updated" line against `DEVLOG.md`'s top entry; if `DEVLOG.md` has
newer entries this file doesn't reflect, trust `DEVLOG.md` and update
this file to match before relying on it further.

**Last updated:** 2026-07-09, after adding two `DEVLOG.md` entries that
had gone missing (PR #4, HANDOFF.md/CLAUDE.md; PR #5, SYSTEM_BLUEPRINT.md/
KNOWN_LIMITATIONS.md currency) — Steven caught this directly ("devlog in
main is still 2 hours old"), not self-caught. That's a second, distinct
staleness gap in the same session: the first was current-state docs
(`SYSTEM_BLUEPRINT.md`, `KNOWN_LIMITATIONS.md`) drifting behind the code;
this one was the append-only history itself drifting behind merged PRs.
Both had the same root cause — a doc update treated as optional cleanup
rather than part of finishing the change. **Update `DEVLOG.md` in the
same commit as the change it records, and update this file, `README.md`,
`OPERATIONS_MANUAL.md`, and `SYSTEM_BLUEPRINT.md`'s component map in the
same session as any real change.** Neither direction keeps the other
honest automatically — this session found that out twice.

## What this repo is, in one paragraph

Turns real verification tool output (CrossHair, Dafny/Z3) plus authored
metadata into IEC 62304/FDA §524B traceability artifacts, where every
claim is bound to a committed, replayable evidence record of honestly-
labeled strength — `PROVEN` can never appear unless a real, completed
Dafny proof produced it. Full explanation: `README.md` (plain-English)
and `OPERATIONS_MANUAL.md` (technical reference — read this one if
you're about to build something, not just read about the system).

## Current state of both worked examples

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
  closed under two named, deliberately provisional fallback assumptions
  — not permanent decisions, see `PHASE1_PLAN.md`'s "Closed under named
  fallback assumptions" section.
- `renal_adjustment.dfy` exists, is committed, and verifies (`5
  verified, 0 errors`) — five functions: `RoundHalfUp`, `GStage`,
  `SelectFormula`, `ComposedCeiling`, `AssessRenalFunction`.
- Gate C6 (NL confirmation) is built; the sign-off document
  (`nl_confirmation_renal_adjustment_dfy.md`) is presented but its
  "Decision" section is **pending Steven's actual confirmation** — it
  has not been rubber-stamped, don't treat it as closed.
- Gate C4 (STPs) is built and found + fixed two real gaps for real
  (`ComposedCeiling`, `AssessRenalFunction` both needed pinning
  clauses) — see `gate_c4_stp_plan.md` and the `_underconstrained`/
  `_stp_suite_against_underconstrained` honesty-exhibit files.
- **Gate C3 (spec lint) and Gate C5 (mutation testing) have not been
  built yet for this example.** This is the actual next concrete step
  if picking this work back up — both should work largely unmodified
  against `renal_adjustment.dfy` per the infrastructure plan, but that
  claim needs checking empirically, not assumed (see "A standing
  discipline," below — this exact assumption already failed once, for
  Gate C6, and cost a real debugging detour).

## Two things explicitly left open, not forgotten

1. **CrCl/eGFR value computation** (Gate 1c "Finding 1"): currently
   caller-supplied for both formulas — no function computes Cockcroft-
   Gault CrCl or CKD-EPI eGFR from raw patient data. The equations
   themselves are verified and ready
   (`sources/ckd-epi-2021-and-cockcroft-gault-verification.md`) if this
   ever gets built. Recommendation on record: build Cockcroft-Gault
   (small, linear, low risk), leave CKD-EPI eGFR caller-supplied
   (genuine Dafny/Z3 expressiveness gap — real fractional exponents on
   a variable base — not just a performance issue). This is Steven's
   scope call, not something to decide unilaterally.
2. **Classification-flag provenance** (`REQ-RENAL-8`): who sets
   `SelectFormula`'s caller-supplied boolean flags, by what process.
   Reclassified as a Phase 3 integration concern, not a Phase 2 proof
   blocker — doesn't block the Dafny work, but is a real open item for
   whenever Phase 3 (evidence packaging) starts.

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
  154 as of this writing.
- Dafny 4.11.0 / Z3 are installed; `dafny verify <file>.dfy` works
  directly.
- Branch workflow used this session: create a `claude/<topic>` branch
  off `main`, commit there, open a PR, merge it into `main` the same
  session once tests pass locally (no CI is configured on this repo —
  0 checks — so there's nothing to wait for beyond the local test run).
  `main` is the live, current state; feature branches are short-lived
  and not meant to accumulate.
- Every real tool run (Dafny, CrossHair, pytest) gets its raw output
  and a manifest committed verbatim — never re-typed, never smoothed
  over if the result is unexpected.
