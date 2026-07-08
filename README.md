# PayloadGuard Evidence

PayloadGuard Evidence turns software verification results into
regulatory-grade paperwork for medical device software — the kind of
paperwork a submission to a regulator (FDA, or under IEC 62304 more
generally) needs to show that a safety claim isn't just asserted, it was
actually checked, and checked by a specific method whose strength is
stated honestly.

If you've worked anywhere near a medical device submission, you know the
usual failure mode: a requirements document says "the software shall
never exceed the safe dose," a test suite runs a handful of cases, and
somewhere in between those two facts get quietly overstated — "tested"
becomes "verified," a few passing examples become a blanket guarantee.
This tool exists to make that overstatement structurally impossible. It
will not let a document claim more than the evidence in front of it
actually supports.

## The problem, in plain terms

Every requirement for a piece of medical device software should be able
to answer three questions:

1. **What exactly must the software do (or never do)?** Traced to a real
   source document — a hazard analysis, a safety standard, a clinical
   guideline — not invented.
2. **How do we know it does that?** Traced to a specific, real run of a
   specific verification tool, with the tool's actual output kept on
   file, not summarized from memory.
3. **How strong is that evidence, really?** A mathematical proof, a
   large search that found no counterexample, and a test that ran a
   handful of examples are three very different levels of confidence —
   and mixing them up is exactly the kind of mistake that matters in a
   safety-critical system.

This repository's job is to make those three answers automatic,
traceable, and — critically — impossible to fake or round up.

## The core idea

- **A requirement** is a specific, sourced claim about what the software
  must do (e.g. "the delivered dose must never exceed the configured
  safe maximum").
- **Evidence** is the actual, captured output of a verification tool run
  against real code or a real formal specification — never a summary,
  never hand-typed, always the verbatim result of a real run.
- **Strength** is an honest label for how much that evidence actually
  proves:

  | Label | What it really means |
  |---|---|
  | **Proven** | A mathematical proof (via the Dafny/Z3 toolchain) that the requirement holds for *every* possible input, not just the ones tested. |
  | **Bounded-checked** | A large, automated search (via CrossHair) found no counterexample within a stated, recorded search budget — strong evidence, but not a proof; something outside the search budget could still be wrong. |
  | **Tested / example-checked** | The software was run on a specific set of concrete inputs and gave the expected output on each. Says nothing about inputs that weren't tried. |
  | **Declared** | A human stated this is true. No tool checked it. |
  | **Gap** | Nothing has been established yet. This is flagged, never hidden. |

  Every one of these levels is legitimate evidence — the point isn't
  that only "Proven" counts, it's that a reader is never left guessing
  which one they're looking at.
- **The traceability matrix** is the generated document that ties all of
  this together: for every requirement, which evidence backs it, at
  what strength, with a link back to the real captured tool output. It
  is always machine-generated from real inputs — nobody hand-edits it,
  and the system actively refuses to build one that overstates its own
  evidence (a "Proven" label can never appear unless it was actually
  produced by a real mathematical proof).

## What's in this repository

- **`evidence/`** — the reusable engine: schema validation, evidence
  binding, the traceability-matrix generator, the Dafny toolchain
  integration (proof capture, mutation testing, spec linting, and a
  human-in-the-loop plain-English confirmation step), and a mechanical
  citation-verification check for source claims.
- **`examples/dosage_calculator/`** — a complete, worked proof-of-concept:
  an IV infusion pump's dose-clamping logic, with requirements sourced
  from a published infusion-pump hazard analysis, taken all the way
  through to a full mathematical proof and mutation-tested for real.
- **`examples/renal_adjustment/`** — a second, independent worked
  example, in progress: adjusting a drug dose for a patient's kidney
  function, sourced from UK clinical guidelines (MHRA, KDIGO, NICE).
  Built specifically to prove the same verification pipeline generalizes
  beyond simple arithmetic to lookup tables and conditional branching.
- **`sources/`** — the primary source documents (hazard analyses,
  clinical guidelines, regulatory guidance) that every sourced
  requirement traces back to, archived so a claim can always be checked
  against the actual document, not a paraphrase of it.
- **`tests/`** — the automated regression suite protecting every rule
  above (152 tests as of this writing).

## Quick start

```bash
pip install crosshair-tool jsonschema pyyaml pytest
# Dafny 4.11.0 and Z3 are also required for the formal-proof examples —
# see OPERATIONS_MANUAL.md for install notes.

# Run the full test suite
python -m pytest tests/ -v

# Rebuild the infusion-pump example's traceability matrices from its
# committed evidence
cd examples/dosage_calculator
python generate_artifacts.py
```

That's enough to confirm everything in the repository is internally
consistent. For how to re-run the actual verification tools, add a new
requirement, or extend the system to a new example, see
[`OPERATIONS_MANUAL.md`](OPERATIONS_MANUAL.md) — the full technical
reference for operating this system.

## Status at a glance

- **Infusion-pump dose calculator**: complete. Every requirement has
  been carried through source citation, formal specification,
  mathematical proof, mutation testing (to check the proof is actually
  tight, not just present), and a recorded human sign-off confirming the
  formal specification says what was intended.
- **Renal-function dose adjustment**: in progress. Clinical sourcing and
  the core formal specification are built and proof-checked; some
  requirements are still deliberately left as open, named decisions
  rather than guessed at.
- Full, dated build history: [`DEVLOG.md`](DEVLOG.md). Current open
  items and known gaps: [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md).

## What this is not

- **Not a PR-gate or merge-blocking CI tool.** (A separate repository,
  `PayloadGuard-PLG/payload-consequence-analyser`, is that product — it
  shares no code with this one.)
- **Not a replacement for human regulatory sign-off.** Every generated
  claim is reviewed by a person before it goes anywhere near a real
  submission — see [`REVIEW_PROTOCOL.md`](REVIEW_PROTOCOL.md).
- **Not a tool that infers or estimates how strong evidence is.**
  Strength labels come only from what a verification tool actually
  reported in a real, captured run — never from what a requirement was
  merely *hoped* or *intended* to achieve.

## Further reading

| Document | What it covers |
|---|---|
| [`HANDOFF.md`](HANDOFF.md) | Start here if you're picking this repo up fresh: current status, what's actually done vs. in progress, and the concrete next step. |
| [`OPERATIONS_MANUAL.md`](OPERATIONS_MANUAL.md) | The full technical manual: architecture, every verification gate explained, complete command reference, how to add a new example. |
| [`SYSTEM_BLUEPRINT.md`](SYSTEM_BLUEPRINT.md) | Component map and data-flow reference, kept in sync with the code. |
| [`DEVLOG.md`](DEVLOG.md) | Dated, append-only log of every real build session. |
| [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md) | The live ledger of every open item, named rather than hidden. |
| [`REVIEW_PROTOCOL.md`](REVIEW_PROTOCOL.md) | How generated artifacts get reviewed before real use. |
| [`sources/README.md`](sources/README.md) | The discipline for adding and citing a new primary source document. |
