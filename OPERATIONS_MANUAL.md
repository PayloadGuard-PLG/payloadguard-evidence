# Operations Manual — payloadguard-evidence

The technical reference for operating this system: architecture, every
verification gate explained, full command reference, and how to extend
it to a new example. Written for someone who is going to run this
system, not just read about it — assumes familiarity with Python,
command-line tools, and enough formal-methods vocabulary to look up a
term you don't recognize, but doesn't assume you've read the source
code first.

For the plain-English overview, start with [`README.md`](README.md).
This document goes deeper.

---

## 1. Architecture

### 1.1 Component map

```
payloadguard-evidence/
├── evidence/                 The reusable engine (domain-free — nothing
│                              in here is specific to any one example)
│   ├── model.py               Strength vocabulary, evidence dataclasses
│   ├── schema/                JSON Schema contracts for metadata files
│   ├── reconcile.py           Cross-artifact fact-equality checking
│   ├── conflict.py            Contradiction detection (CONFLICT rule)
│   ├── render/matrix_variants.py  The traceability-matrix builder
│   ├── cli.py                 `python -m evidence.cli build`
│   ├── dafny_adapter.py       Parses real Dafny verifier output safely
│   ├── dafny_spec_lint.py     Checks a Dafny spec's TEXT for weaknesses
│   ├── dafny_nl_summary.py    Plain-English summary of a Dafny contract
│   ├── dafny_mutate.py        Mutation-testing engine for Dafny specs
│   └── citation_gate.py       Mechanical citation verification (§4.7)
├── examples/
│   ├── dosage_calculator/          Worked example 1 (complete)
│   ├── renal_adjustment/           Worked example 2 (complete)
│   └── drug_interaction_checker/   Worked example 3 (complete)
├── sources/                   Primary source documents, archived verbatim
└── tests/                     Regression suite (205 tests)
```

`evidence/` is deliberately vocabulary-agnostic: nothing in it knows
about infusion pumps or kidney function. Every example directory under
`examples/` supplies its own requirements, its own verification targets,
and its own captured evidence; the engine just binds and renders.

### 1.2 Data flow

```
sources/*.md  ──cite──►  metadata.yaml  ──validate (JSON Schema)──►
                              │
                              ▼
                    generate_matrix*.py
                    ┌──────────────────────────────────┐
                    │ 1. validate metadata against schema│
                    │ 2. bind captured evidence to reqs  │
                    │ 3. derive intent_ok (once, ever)   │
                    │ 4. refuse if any realized strength │
                    │    == PROVEN unless it's a real,   │
                    │    completed Dafny proof           │
                    │ 5. render JSON + Markdown          │
                    └──────────────────────────────────┘
                              │
                              ▼
                traceability_matrix.*.json / .md
```

Everything that isn't authored (the metadata file, the source citations)
is either a **capture** (the verbatim output of actually running a
verification tool, plus a manifest recording the exact command, exit
code, and timestamp) or **generated** (the traceability matrix itself).
Nothing in between is hand-typed. If you ever see a traceability matrix
that doesn't match what `generate_matrix*.py` would produce from the
committed captures, that's a bug, not a feature — regenerate it.

---

## 2. Core concepts

### 2.1 The Strength vocabulary

Defined once, in `evidence/model.py`, and nowhere else — every part of
the system imports this, none of them re-derive it:

| Strength | Where it comes from | Caveat rendered on every record |
|---|---|---|
| `PROVEN` | A Dafny proof, verified by Z3, with a real `verifier_completion_status == "completed"` capture | "Formally proven against the stated specification." |
| `BOUNDED_CHECKED` | A CrossHair symbolic-execution pass that found no counterexample within a recorded search bound | "No counterexample found within the recorded bounds; this is a bounded search, not a proof." |
| `TESTED` | Concrete test cases actually executed | "Exercised on the recorded test cases only." |
| `EXAMPLE_CHECKED` | Specific recorded input/output pairs actually executed | "Holds for the specific recorded inputs only; no claim of generality beyond them." |
| `DECLARED` | A human asserted it; no tool checked it | "Asserted by the author; not established by any tool." |
| `GAP` | Nothing established | "Not established. Human input required." |

**Rules that are enforced in code, not just convention:**

- Strength is derived **only** from what a captured tool run actually
  reported. A requirement's stated *intent* (what strength it was
  hoping to achieve) never leaks into the *realized* strength that gets
  rendered.
- `PROVEN` can appear as a realized strength in a generated artifact
  **only** if the underlying record has `method == "dafny"` and
  `verifier_completion_status == "completed"`. This is a hard assertion
  in the generation path (`assert_no_realized_proven`,
  `evidence/render/matrix_variants.py`) backed by a dedicated test
  suite (`tests/test_proven_exclusivity.py`) — not a lint rule someone
  could forget to run.
- When a requirement's intent and its realized strength don't match
  (e.g. a requirement hoped for `PROVEN` but only achieved
  `BOUNDED_CHECKED`), that mismatch is rendered explicitly
  (`intent_ok: false`, with a note), never smoothed over.
- A `GAP` is represented by the field being genuinely absent — never by
  a placeholder string like `"N/A"` or `"TBD"` that could be mistaken
  for real content.

### 2.2 Requirements and metadata

Each worked example has a `metadata.yaml` (or `.a.yaml` / `.b.yaml` /
`.c.yaml` for the schema-variant forks — see 2.4) declaring:

- the device/system under evaluation,
- its requirements, each with either a citation into `sources/` or an
  explicit `DECLARED` marker (if it's a design invariant rather than a
  sourced clinical/regulatory fact),
- the threat model,
- the intended verification envelope (what strength each requirement is
  hoping to achieve, and — for CrossHair — the declared search bounds).

Every metadata file is validated against a JSON Schema
(`evidence/schema/metadata.schema*.json`, draft 2020-12) before anything
else happens. An invalid metadata file fails loudly at generation time,
not silently at render time.

### 2.3 Evidence capture

A **capture** is the record of one real run of one verification tool.
Every capture consists of two files:

- **Raw output** (`raw_*.txt`) — the tool's actual stdout+stderr,
  verbatim, byte-for-byte.
- **A manifest** (`run_manifest*.json`) — the exact command run, the
  process exit code, the tool version, and an ISO-8601 UTC timestamp.

Captures are never edited after the fact. If a run produces an
unexpected result, that result is committed as-is and reported — never
silently re-run until it looks better ("re-rolled").

For Dafny specifically, captures are parsed by
`evidence/dafny_adapter.py::parse_dafny_capture`, which is deliberately
paranoid: it refuses (raises, does not guess) on a nonzero exit code, a
missing or ambiguous verifier summary line, or any marker suggesting the
run was incomplete (out of resource, out of memory, timed out) — see
§4.3 for why this specific paranoia exists.

### 2.4 Variant shapes (A / B / C)

The traceability matrix is generated in several parallel shapes,
covering different ways a real regulatory toolchain might want evidence
represented (evidence listed inline per requirement, vs. "shadow rows"
with a parent/child relationship, vs. a self-describing single matrix
partitioned by verification method). These are **presentation
differences only** — a fact-equality gate
(`evidence/reconcile.py::run_gate`, backed by
`tests/test_fact_equality.py`) mechanically checks that every variant
carries the *same underlying facts* (same evidence, same intent, same
bounds) regardless of shape. Shape divergence is design; fact divergence
is a defect the system is built to catch, not something a reviewer has
to eyeball.

---

## 3. The evidence pipeline, step by step

### 3.1 Author

Write or edit `examples/<name>/metadata.yaml`. Every sourced requirement
must cite a document actually present in `sources/` — if the source
doesn't exist yet, add it first (see `sources/README.md`'s discipline:
every new source states explicitly what it confirms, corrects, or
extends relative to what's already claimed).

### 3.2 Capture

Run the relevant `run_verify*.py` script. Each one:

1. Invokes the real verification tool as a subprocess (CrossHair or
   Dafny).
2. Writes the verbatim stdout+stderr to `raw_*.txt`.
3. Writes a manifest (command, exit code, tool version, timestamp) to
   `run_manifest*.json`.

There is one `run_verify*.py` per target — see §5 for the full command
reference.

### 3.3 Generate

Run the relevant `generate_matrix*.py` (or `generate_artifacts.py` for
the full end-to-end pipeline — schema validation, capture integrity
checks, CONFLICT detection, regeneration, the structural PROVEN sweep,
and a provenance index in one pass). This binds captured evidence to
requirements, derives intent, runs the structural PROVEN check, and
writes the traceability matrix as both JSON and Markdown. **Never
hand-edit a generated matrix** — if it looks wrong, the input (metadata
or capture) is wrong; fix that and regenerate.

---

## 4. The Dafny verification pipeline (Gates C1–C6)

This is the part of the system that produces `PROVEN` evidence — a real
mathematical proof, not a search. It's organized as six gates, each
catching a different, real failure mode that formal verification tools
are prone to. Every gate below is illustrated by both worked examples;
mechanisms are described generically, file names in `dosage_calculator`
are given as concrete examples.

### 4.1 Gate C1 — the spec and the capture

Write the Dafny specification itself (`.dfy` file: `requires`/`ensures`
clauses expressing the requirement, machine-checked by Dafny against a
concrete implementation or a self-contained function body). Verify it
for real (`dafny verify <file>.dfy`), capture the output, and parse it
with `evidence/dafny_adapter.py::parse_dafny_capture`.

**The specific risk this gate defends against: the "false zero."** A
naive parser might treat exit code 0 as "verified." Dafny's own summary
line is the actual source of truth (`"Dafny program verifier finished
with N verified, 0 errors"`) — the adapter matches that line with a
regex, never a substring check, and refuses outright on a nonzero exit
code, a missing summary line, more than one summary line in a capture,
or a nonzero error count.

### 4.2 Gate C2 — PROVEN's exclusivity

A structural rule, not a per-spec check: `PROVEN` may be assigned as a
*realized* strength in a generated artifact only for a record with
`method == "dafny"` **and** `verifier_completion_status == "completed"`.
Every other method — CrossHair, concrete tests, or a record with no
method at all — is permanently excluded, even if someone tried to claim
it. This is enforced by `assert_no_realized_proven`
(`evidence/render/matrix_variants.py`) and checked explicitly, not by
omission, in `tests/test_proven_exclusivity.py`.

### 4.3 Gate C3 — hardening the Dafny output parser

Three real, distinct failure modes a naive Dafny integration would miss:

1. **Vacuous preconditions.** A `requires` clause that can never be true
   (e.g. `x > 0 && x < 0`) makes every `ensures` clause hold vacuously —
   Dafny reports a clean pass with no hint anything is wrong.
   `evidence/dafny_spec_lint.py::check_precondition_satisfiability`
   extracts a method's `requires` clauses and asks Z3 directly whether
   they're jointly satisfiable, rather than trusting Dafny's clean
   report at face value.
2. **Weak postconditions.** A best-effort heuristic
   (`scan_weak_postconditions`) flags one-directional `==>` clauses in
   `ensures` that lack a matching `<==>` — a common shape for an
   under-constrained spec (see Gate C4 for the mechanized version of
   this check).
3. **Timeout/resource-limit masking.** A resource-starved Dafny run can
   report `0 verified, 0 errors` alongside an `"N out of resource"`
   marker — a result that looks clean at a glance but isn't. The
   adapter refuses independently on any out-of-resource/out-of-memory/
   timed-out marker in the summary tail, on top of the exit-code check.

Run: `dafny verify --resource-limit=<N> <file>.dfy` to reproduce
condition 3 directly; `evidence/dafny_spec_lint.py`'s functions are
called directly (they lint source text, not captured output, and are
not wired into the generation pipeline — they're standalone, tested
tools you run deliberately).

### 4.4 Gate C4 — Spec-Testing Proofs (STPs)

**The single most important gate for catching a spec that says less
than you think it does.** The idea (IronSpec methodology): pick a
specific candidate output value, and try to prove — using *only* the
`requires`/`ensures` clauses, never the function's actual body — that
this value is either forced (an ACCEPT lemma) or impossible (a REJECT
lemma). If a REJECT lemma assuming a *wrong* value fails to prove
`false`, that means the specification doesn't actually rule the wrong
value out — a broken implementation could satisfy the exact same
contract undetected.

This isn't hypothetical: it found real gaps in both worked examples.
`dosage_calculator`'s original postcondition bounded the dose and forced
it to zero on reverse flow, but never pinned it to the actual clamped
value — a function that always returned `0.0` would have passed the
same spec. The fix is a **pinning clause**: a new `ensures` clause
asserting the result equals a concrete defining expression (e.g.
`ensures dose == ExpectedDose(...)`), which fully determines the value
rather than merely bounding it.

**How to build an STP suite:**

1. Write ACCEPT/REJECT lemmas in a new `<target>_stp_suite.dfy` file
   that `include`s the spec under test.
2. Run it (`dafny verify <suite>.dfy`) against the spec **as it
   currently stands, before any fix** — don't assume, check.
3. If a REJECT lemma fails, that's a real gap. Fix the spec with a
   pinning clause, not a loosened test.
4. Preserve the pre-fix spec verbatim as `<target>_underconstrained.dfy`
   (an honesty exhibit — it still verifies fine on its own, the bug is a
   spec *weakness*, not a Dafny error) and keep the failing STP lemmas
   in a separate `<target>_stp_suite_against_underconstrained.dfy` file,
   `include`-ing the preserved original. **Commit its genuinely failing
   capture** (nonzero exit code, real error text) — this is the
   mechanized proof that the methodology actually caught something,
   not a synthetic demonstration.
5. Re-run the full STP suite against the fixed spec — every lemma should
   now pass.

### 4.5 Gate C5 — mutation testing

Answers a different question from Gate C4: not "does the spec pin an
exact value," but "does every individual piece of the spec's *text*
actually matter?" `evidence/dafny_mutate.py` mechanically perturbs a
spec's `requires`/`ensures` clauses (and, optionally, a companion
function's body) one small change at a time, and re-verifies each
mutant for real. A mutant that still verifies cleanly despite the
change reveals a piece of the spec that isn't pulling its weight — a
**survivor**, which must be investigated and fixed (either the spec is
genuinely looser than intended, or the mutation revealed an equivalent
formulation, which gets filtered rather than reported as a defect).

Five operator classes, run via `generate_mutants(source, method_name,
function_name=None)`:

| Class | What it mutates |
|---|---|
| ROR (Relational Operator Replacement) | `<`, `<=`, `>`, `>=`, `==`, `!=` in clauses — chain-direction-aware, so a mutation that would produce an invalid Dafny chained comparison is filtered before ever reaching the verifier |
| LOR (Logical Operator Replacement) | `&&`, `\|\|` in clauses |
| AOR (Arithmetic Operator Replacement) | `+`, `-`, `*`, `/`, `%` in a companion function's body only — never the method's own trusted implementation — and restricted to MutDafny's own group rule (`+`/`-`/`*` interchange freely; `/` only with `%`), so a mutation can never introduce a division-by-zero risk the original spec never had |
| LVR (Literal Value Replacement) | every numeric literal, perturbed by a fixed clinical-precision delta (`±0.01`) |
| COI (Conditional Operator Insertion) | inserts negations at decision points |

A fast static pre-filter (pass 1) discards mutants that are provably
uninteresting *before* spending a real Dafny invocation on them (e.g.
weakening a postcondition's operator is trivially still implied by a
stronger original) — the direction of "trivial" flips depending on
whether the clause is a `requires` or an `ensures`, which is the least
obvious part of this design and is tested against a synthetic spec
independent of any real example, specifically so getting the direction
backwards would be caught rather than silently filtering out the
mutants that actually matter.

**Running it:** each worked example has its own
`run_mutation_suite*.py`, which generates every mutant, filters
statically-trivial and vacuous-precondition mutants, and real-verifies
every survivor against the installed Dafny binary. Mutant `.dfy` files
are not committed individually (they're mechanically derived and
reproducible); the real per-mutant outcome is written to
`mutation_report.json`/`.md`.

### 4.6 Gate C6 — NL-dialogue confirmation

A process-control gate, not a mechanical proof. Its purpose: catch a
mismatch between what a Dafny spec's `requires`/`ensures` clauses
actually say and what the author *intended* them to say, at the moment
the spec is written — the cheapest possible point to catch it, and the
same defect class that caused this project's very first finding (a
requirement whose formal encoding didn't match its source text).

`evidence/dafny_nl_summary.py::summarize_method` mechanically extracts
every `requires`/`ensures` clause verbatim (never inferred), alongside
any requirement ID cited in a trailing `// REQ-...` comment, plus a
best-effort plain-English gloss (a simple operator-substitution
template — explicitly labeled a reading aid, not comprehension; the raw
clause is always shown first and is the authoritative artifact).

**The gate's actual deliverable is not this code — it's a recorded human
decision.** Each worked example has an `nl_confirmation_<file>.md`
document: the generated summary, plus an explicit sign-off ("this
matches intent") or correction, dated and attributed. If a later change
touches a function that was already signed off, the document gets a
dated **amendment**, not a silent edit — the original decision stays on
the record alongside what changed and why.

### 4.7 Citation gate — mechanical citation verification

Not one of the numbered Dafny gates (it's not Dafny-specific at all),
but built for the same reason: this session caught two real, fabricated
citations by hand — a NICE NG203 misquote repeated verbatim across two
separately-supplied "research findings" documents, and a KDIGO misquote
with both the wrong recommendation number and the wrong content. Both
were caught only by fetching the actual primary source and reading it
directly. `evidence/citation_gate.py::verify_citation` mechanizes that
same check: normalized substring matching between a claimed quote and
source text the caller already has, returning `CONFIRMED` or
`NOT_FOUND` — deliberately not an LLM judgment call, so a system that
drafts a citation and a system that checks it can't share the same
failure mode.

`NOT_FOUND` is never presented as proof of fabrication — source-text
extraction (particularly from PDFs) can be lossy, so a `NOT_FOUND`
verdict means "could not confirm automatically, check the raw source,"
mirroring how `BOUNDED_CHECKED` is never presented as a proof (§2.1).
The matcher also guards against a real false-positive the module's own
audit found in itself: normalizing away punctuation means a naive
substring check would let a claim citing "Recommendation 1.1.2" falsely
confirm against source text reading "Recommendation 1.1.2.1" (a
different recommendation) — fixed with a digit-adjacency boundary check
specific to numeric matches. Not wired into any generation pipeline — a
standalone tool, called directly (`evidence.citation_gate.verify_citation`
/ `verify_citations`), same scope discipline as the other Gate modules.

---

## 5. Command reference

```bash
# --- Setup ---
pip install crosshair-tool jsonschema pyyaml pytest
# Dafny 4.11.0: dotnet tool install --global dafny  (requires .NET SDK)
# Z3: must be on PATH; Dafny's installer typically bundles a compatible version

# --- Full test suite ---
python -m pytest tests/ -v

# --- dosage_calculator: capture evidence (from examples/dosage_calculator/) ---
python run_verify.py                    # CrossHair: clean kernel
python run_verify_broken.py             # CrossHair: broken variant (fixture)
python run_verify_naive_widening.py     # CrossHair: honesty exhibit
python run_verify_overflow_probe.py     # CrossHair: honesty exhibit (paired)
python run_verify_concrete.py           # pytest capture -> concrete_results.json
python run_verify_dafny.py              # Dafny: the real spec
python run_verify_dafny_broken.py       # Dafny: broken variant (fixture)
python run_verify_dafny_stp_suite.py    # Gate C4: STP suite against the fixed spec
python run_verify_dafny_stp_suite_against_underconstrained.py  # Gate C4: the "before" proof
python run_mutation_suite.py            # Gate C5: full mutation run

# --- dosage_calculator: regenerate artifacts ---
python generate_artifacts.py            # full pipeline: validate -> capture
                                         # integrity -> regenerate -> PROVEN
                                         # sweep -> provenance index
python generate_matrix.py               # base matrix only
python generate_matrix_a.py / _b.py / _c.py   # individual schema variants

# --- Gate 2 CLI: vocabulary-agnostic, works on any example ---
python -m evidence.cli build --variant a \
    --metadata examples/dosage_calculator/metadata.a.yaml \
    --manifest examples/dosage_calculator/run_manifest.json \
    --concrete examples/dosage_calculator/concrete_results.json \
    --out-json /tmp/out.json --out-md /tmp/out.md
# --dafny-captures <path> is required once the target metadata declares
# any method: dafny evidence.

# --manifest and --concrete are optional (2026-07-11) - omit both for a
# Dafny-only example with zero crosshair/concrete_test evidence, as
# renal_adjustment and drug_interaction_checker both are:
python -m evidence.cli build --variant a \
    --metadata examples/renal_adjustment/metadata.a.yaml \
    --dafny-captures examples/renal_adjustment/dafny_captures_index.json \
    --out-json /tmp/out.json --out-md /tmp/out.md

# --- Raw Dafny commands, useful when developing a new spec ---
dafny verify path/to/spec.dfy                      # verify a spec directly
dafny verify --resource-limit=<N> path/to/spec.dfy  # reproduce Gate C3's
                                                     # timeout-masking check
```

---

## 6. Adding a new worked example

The `examples/renal_adjustment/` build is the reference template for
this — it was built specifically to test whether the pipeline
generalizes, and the process below is what that build actually followed,
gate by gate, including the parts that needed a small, real fix to the
shared engine along the way (see §6.4).

### 6.1 Source and scope first

Before any code: gather primary source documents into `sources/`,
following the discipline in `sources/README.md` (every new source states
explicitly what it confirms, corrects, or extends). Write a Phase 1
planning document (see `examples/renal_adjustment/PHASE1_PLAN.md` for
the template) covering: a requirements table with citations, a formal
specification skeleton (preconditions/postconditions in prose, before
any Dafny), and an explicit list of non-goals — things deliberately out
of scope, named rather than silently absent.

### 6.2 Internal consistency audit before writing Dafny

Hand-trace every requirement and at least one real worked example
through the specification skeleton **before writing formal code**. This
is the cheapest point to catch a conceptual gap — see
`examples/renal_adjustment/GATE_1C_AUDIT.md` for a worked instance that
caught two real design gaps this way (a missing computation step, and a
type ambiguity that a stronger Dafny type system design later closed
structurally).

### 6.3 Build the Dafny spec, then run all six gates in order

Gate C1 (spec + capture) → Gate C6 (NL confirmation — deliberately moved
earlier than in the first worked example, since it's cheapest to run
right after the spec first verifies clean) → Gate C4 (STPs) → Gate C3
(spec lint) → Gate C5 (mutation testing). The exact order isn't sacred,
but "prove the spec is internally sound (C4) before spending effort
mutation-testing it (C5)" is a real dependency, not an arbitrary
convention.

### 6.4 Expect to find, and fix, real gaps in the shared engine

Two of the shared engine's helper functions
(`evidence/dafny_spec_lint.py::_find_method_header`, and its duplicate
in `evidence/dafny_mutate.py`) had only ever been exercised against a
Dafny `method`, never a plain `function` — because the first worked
example always had both. The second worked example is pure `function`s,
and running Gate C6 against it immediately surfaced the gap. Small, real
fixes to shared code like this are expected and normal when extending
the system to a genuinely different shape of spec — that's the entire
point of building a second example. Fix them the same way any other real
gap gets fixed: confirm it empirically, apply a real fix (not a
special-case workaround), add a regression test, re-run the full suite.

---

## 7. Testing discipline

- `python -m pytest tests/ -v` must pass before any commit.
- New capability gets new tests in the same commit, not a follow-up.
- Tests that validate a **committed real capture** (e.g.
  `tests/test_mutation_report.py`) check the artifact as it stands
  rather than re-running the underlying tool 50+ times per test pass —
  but the artifact itself must always be the output of a real run, never
  hand-typed to make a test pass.
- A regression test exists for every self-caught mistake during a build
  (see `tests/test_dafny_stp_suite.py`'s wrong-candidate-value
  regression, or `tests/test_dafny_nl_summary.py`'s multi-line-clause
  regression) — the mistake gets fixed, and a test is added so it can't
  silently reappear.

---

## 8. Review protocol summary

Full detail: [`REVIEW_PROTOCOL.md`](REVIEW_PROTOCOL.md). In brief, review
is two-tiered:

- **Tier 1 (machine gates)** — the fact-equality gate and the structural
  PROVEN check. A Tier 1 failure is a defect, never a judgment call: it
  stops generation, and it's fixed by correcting the code, metadata, or
  evidence that caused it — **never** by hand-editing a generated
  artifact.
- **Tier 2 (human review)** — with Tier 1 green, a person reviews the
  structured findings: intent mismatches, `GAP` rows, `DECLARED`-strength
  records, the declared-vs-effective bounds block, and the honesty
  exhibits. Reviewed per-reason, not by re-checking the whole artifact
  from scratch.

---

## 9. Troubleshooting

- **A traceability matrix looks wrong.** Never edit it. Check the
  metadata and the captures it was generated from, fix those, and
  regenerate.
- **Dafny reports a clean pass but you suspect the spec is weak.** Write
  an STP (§4.4) before trusting a clean `dafny verify` at face value —
  a clean pass proves the spec is internally consistent, not that it
  says what you think it says.
- **A Dafny run exits 0 but a summary marker mentions "out of
  resource."** This is exactly Gate C3's timeout-masking check (§4.3) —
  the adapter should already refuse it; if it doesn't, that's a real
  regression, file it as one.
- **`evidence.cli build` refuses with a missing `--dafny-captures`
  error.** The target metadata declares Dafny evidence; point
  `--dafny-captures` at a JSON index of the real capture file paths (see
  `examples/dosage_calculator/dafny_captures_index.json` for the shape).
- **You're extending the engine and something that "should just work"
  doesn't.** Check empirically before assuming — §6.4 above is the
  standing reminder that "generalizes for free" claims get checked by
  actually running them, not by reading the code and deciding it looks
  generic enough.

For the full, current list of open items and named gaps, see
[`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md). For the complete,
dated history of every real build session, see [`DEVLOG.md`](DEVLOG.md).
