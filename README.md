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

## A worked example: what "Proven" actually looks like

Abstract claims about "formal verification" are easy to write and hard
to trust. Here is one real requirement, traced through every gate this
system runs, with the actual captured output at each step — not a
summary, not a paraphrase, all pulled verbatim from files committed in
`examples/drug_interaction_checker/`.

**The requirement:** dabigatran (a blood thinner) combined with
ketoconazole (an antifungal) is contraindicated — the two must never be
prescribed together. Sourced from NHS Specialist Pharmacy Service
guidance (`sources/sps-doac-interactions-2024.md`): *"Itraconazole and
ketoconazole — contraindicated with dabigatran."* This is exactly the
kind of claim that matters: get it wrong, and the software tells a
clinician a dangerous combination is merely worth "caution."

**Gate C1 — capture the proof, verbatim, or don't count it.**
The requirement is encoded as one clause (of 60) on a Dafny function,
`CheckInteraction`:

```dafny
ensures (doac == Dabigatran && agent == Ketoconazole) ==>
  CheckInteraction(doac, agent, hasOtherBleedingRiskFactors)
  == InteractionResult(Contraindicated, BleedingRisk)
```

Running the real Dafny 4.11.0 / Z3 toolchain against it produces exactly
one line of output, captured byte-for-byte in
`raw_dafny_output_ddi.txt`:

```
Dafny program verifier finished with 1 verified, 0 errors
```

That's the raw evidence. `evidence/dafny_adapter.py` parses it into a
strength label — and it isn't a rubber stamp: an early draft of this
same spec had *no* `ensures` clauses at all, and Dafny reported the
identical-looking "0 verified, 0 errors" — meaning zero proof
obligations existed, not zero problems. Gate C1's own job is catching
that difference before anything gets labeled `PROVEN`. Once real
postconditions exist, the same parser turns this capture into:

```
strength = PROVEN, verifier_completion_status = "completed"
```

**Gate C2 — a `PROVEN` label can't be typed in by hand.** The only code
path in this repository that can attach a `PROVEN` strength label is
`evidence/render/matrix_variants.py::dafny_record()`, and it re-derives
that label from the raw capture above — it does not trust a
pre-existing label. A second rule, ruling R3
(`assert_no_realized_proven`), independently refuses two tampered copies
of this exact record before it accepts the real one: one with the tool
name changed to `"crosshair"`, one with `verifier_completion_status`
changed to `"incomplete"`. Both are rejected. Only the real, complete
Dafny capture above passes.

**Gate C3 — the proof isn't quietly checking nothing.** A precondition
that can never be satisfied makes every postcondition trivially,
uselessly "true" — the classic way a formal proof lies without actually
lying. `evidence/dafny_spec_lint.py` asks Z3 directly: can
`CheckInteraction`'s precondition ever hold? The real answer, computed
fresh, not asserted:

```
sat — model: [agent = Naproxen, doac = Dabigatran]
```

Z3 found a real, concrete input that satisfies the precondition —
proof obligations are being exercised, not vacuously discharged.

**Gate C4 — the proof pins the exact answer, not just a plausible one.**
A clean Dafny pass only shows the spec is internally consistent, not
that "Contraindicated" is actually forced. A companion lemma (`GATE_1C_AUDIT.md`
hand-trace 1) tests the specification alone, with no access to the
function's implementation:

```dafny
lemma STP_Accept_CheckInteraction_DabigatranKetoconazole(hasFlag: bool)
  ensures CheckInteraction(Dabigatran, Ketoconazole, hasFlag)
       == InteractionResult(Contraindicated, BleedingRisk)
{}
```

That alone isn't enough — a *weaker* answer (a plain "Caution" instead
of "Contraindicated") might also be consistent with an under-specified
proof. A second, REJECT lemma tests exactly that and must fail to
verify:

```dafny
lemma STP_Reject_CheckInteraction_DabigatranKetoconazole_NotMerelyCaution(hasFlag: bool)
  requires CheckInteraction(Dabigatran, Ketoconazole, hasFlag)
        == InteractionResult(Caution, BleedingRisk)  // wrong: real answer is Contraindicated
  ensures false
{}
```

Both lemmas, and 9 others covering the rest of the table, verify
together in one real run: `22 verified, 0 errors`
(`raw_dafny_output_ddi_stp_suite.txt`) — 11 lemmas, ~2 Dafny
verification tasks each. The weaker "Caution" answer is provably
excluded, not merely absent from the code by coincidence.

**Gate C5 — the proof isn't accidentally tight only where nobody
looked.** Mutation testing rewrites the spec's own operators —
`==`→`!=`, `&&`→`||`, and so on — and reruns the real verifier on each
mutant, checking that a *wrong* spec actually fails to verify. Every
mutant generated against this specific clause was either killed by
Dafny (proof genuinely fails on the corrupted spec) or filtered as a
detected non-arithmetic operator — zero survived undetected
(`mutation_report_ddi.json`). Across the whole 63-cell function: 962
mutants, 564 killed, 389 filtered as structurally redundant before even
invoking Dafny, 7 real survivors — each individually explained, not
hidden (`KNOWN_LIMITATIONS.md`'s "Phase E Gate C5" section) — and 2
refused outright as genuine Dafny type errors rather than guessed at.

**Gate C6 — a human confirmed it means what it was meant to mean, and
actually checked.** A mechanical step
(`evidence/dafny_nl_summary.py`) renders the clause in plain English for
review:

> `(doac == Dabigatran && agent == Ketoconazole) ==> CheckInteraction(...) == InteractionResult(Contraindicated, BleedingRisk)`
> — (doac equals Dabigatran and agent equals Ketoconazole) implies
> CheckInteraction(...) equals InteractionResult(Contraindicated,
> BleedingRisk)

This is not itself evidence — a generated sentence isn't a proof. The
actual deliverable is the recorded human decision in
`nl_confirmation_drug_interaction_checker_dfy.md`, and it was not a
rubber stamp: reviewing it against the primary source directly caught a
real inaccuracy in the sign-off document's own supporting text (an
unrelated clause's rationale had been mislabeled), which was corrected
and left visible, not silently fixed, before the sign-off was recorded.

**The result:** one clinical claim, traced from a cited source, through
a machine-checked proof, through two independent checks that the proof
means what it says and pins the value it claims to pin, through 962
adversarial mutations of the spec itself, to a human confirmation that
actually found and fixed something — six independent layers, every one
of them capable of catching a different class of mistake, all pointing
at the same real, committed artifact. That's what a `PROVEN` label
costs in this system, and why it's the only label that can carry that
word.

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
  example: adjusting a drug dose for a patient's kidney function,
  sourced from UK clinical guidelines (MHRA, KDIGO, NICE). Built
  specifically to prove the same verification pipeline generalizes
  beyond simple arithmetic to lookup tables and conditional branching.
- **`examples/drug_interaction_checker/`** — a third, independent
  worked example: checking a specific drug pairing against a known
  interactions table, sourced from NHS Specialist Pharmacy Service
  guidance. Built to prove the pipeline generalizes again, this time to
  set/list-membership logic. The worked example above walks this one
  through every gate with real, verbatim evidence.
- **`sources/`** — the primary source documents (hazard analyses,
  clinical guidelines, regulatory guidance) that every sourced
  requirement traces back to, archived so a claim can always be checked
  against the actual document, not a paraphrase of it.
- **`tests/`** — the automated regression suite protecting every rule
  above (205 tests as of this writing).

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
- **Drug-drug interaction checker**: complete. All six verification
  gates built and confirmed — including a human sign-off review that
  caught and fixed a real inaccuracy in its own supporting text before
  being recorded. The worked example above walks this one through every
  gate with real, verbatim evidence.
- **Renal-function dose adjustment**: complete. All six verification
  gates built and confirmed, including a proven Cockcroft-Gault CrCl
  computation from raw patient inputs; CKD-EPI eGFR remains
  caller-supplied (a real Dafny/Z3 expressiveness gap, confirmed
  empirically, not a choice). The Gate C6 human sign-off is recorded —
  reviewed against the raw KDIGO/MHRA sources directly, not
  rubber-stamped. The named, deliberately unbuilt requirements
  (`REQ-RENAL-3/4/6/7`, `REQ-RENAL-8`'s classification-flag provenance)
  remain open but no longer block anything.
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
| [`dashboards/`](dashboards/) | Visual, at-a-glance HTML snapshots (status/findings, condensed blueprint) — dated, not auto-regenerated; see its own README for what that means. |
| [`DEVLOG.md`](DEVLOG.md) | Dated, append-only log of every real build session. |
| [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md) | The live ledger of every open item, named rather than hidden. |
| [`REVIEW_PROTOCOL.md`](REVIEW_PROTOCOL.md) | How generated artifacts get reviewed before real use. |
| [`sources/README.md`](sources/README.md) | The discipline for adding and citing a new primary source document. |
