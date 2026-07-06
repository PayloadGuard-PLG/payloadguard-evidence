# PayloadGuard Evidence Layer — Roadmap: Phase B → Phase C

Updated 2026-07-05 with verified external research (IronSpec/MutDafny
academic prior art, a CrossHair seed-override technique, a dual-authorship
traceability mechanism) and this session's own findings (Gate 1 review,
REQ-GIP-1-4-12 alarm scope, FRN resolution). Superseding the 2026-07-05
morning version — Gates 3, 4, and 6 have moved; Phase C section is now
concrete instead of aspirational.

## Where we are

- Phase A closed (R1–R3).
- Gate 1 (artifact generation) — clean pass. Fact-equality holds (7
  facts, consistent across A/B/C-split renders). Two defects found and
  fixed: the Notes-column cross-evidence-type leak/duplication, and
  REQ-GIP-1-4-12's evidence not matching its "shall trigger an alarm"
  text.
- Gate 5 (single-evidence-type fixture) — resolved for the constructible
  half; concrete-only fixture blocked on Gate 2's binder existing.
- Gate 6 (FRN) — resolved, see below.
- Gate 2 (CONFLICT rule) — defined and ratified 2026-07-06, see below.
  Not yet built.

## Guiding principle (unchanged)

Open questions get resolved at the gate where they're first encountered,
with the resolution documented inline — not batched and left for later.
If a gate can't be resolved when reached, name it explicitly as blocked
and why.

---

## Gate 2 — CONFLICT rule: DEFINED (ratified 2026-07-06), not yet built

Was not defined anywhere in the Blueprint or SYSTEM_BLUEPRINT.md beyond a
to-do mention — correctly left unresolved rather than inferred, until
tested against concrete cases and ratified.

**Definition, two sub-types sharing one precondition** (full text and
worked test cases in `KNOWN_LIMITATIONS.md`): CONFLICT only applies
between two claims about the *same* `(requirement, scope)` **and** the
same underlying verification act — never between two legitimately
different evidence types bound to one requirement.
- **Type 1 (identity mismatch):** a top-down ALM-authored contract claims
  "REQ-X is verified at file F, method M" and the bottom-up
  source-embedded assertion says a different file/method/hash. This is
  Gate 4's exact cross-check trigger.
- **Type 2 (outcome mismatch):** two claims agree on target identity but
  disagree on what that identical run produced — added after the
  original single-test-case draft, because CrossHair's own documented
  model-fidelity non-determinism (see Gate 3, and the Sample C /
  overflow-probe exhibits) means the same invocation really can produce
  different results, and the original definition had no way to catch
  that if it ever happened twice for the same target.

REQ-GIP-1-4-12's kernel_scope vs. system_scope split (one evidenced, one
an explicit GAP) remains the negative case — not a conflict, a documented
absence, because there's no second claim to disagree with.

**Status:** definition ratified by Steven; **both types built
2026-07-06** (`evidence/conflict.py`, wired into `generate_artifacts.py`
as stages 3–4, `tests/test_conflict_check.py` — 11 tests, all three
ratified cases covered across all three metadata shapes, 0 conflicts on
the real committed dataset). Variant C's declared-binding asymmetry
(Gate 4) is closed: `metadata.c.yaml` now carries the same top-down
`evidence` declarations as variant A, for cross-checking only — C's
actual binding stays evidence-store-carried, confirmed unchanged by a
byte-identical regeneration diff (timestamp aside).

**Vocabulary-agnostic binder — Step 1 done, Step 2 pending.**
`evidence/render/matrix_variants.py` gained `build_matrix()`: a literal
extraction of all three existing variants' binding/rendering logic into
named, reusable functions, dispatched through one declarative table
instead of three top-level functions. Proven byte-identical (dict AND
JSON-string equality) to the original `build_matrix_variant_a/b/c` over
real committed data (`tests/test_binder_equivalence.py`, 5 tests).
Additive only — `generate_matrix_a.py` / `_b.py` / `_c.py` are untouched
and still authoritative; the pipeline was re-run end to end and every
regenerated artifact differs only by timestamp. Step 2 (retiring the
three old functions and generator scripts in favor of `build_matrix()`,
and folding Types 1/2 into the binder) is the deliberate next stopping
point, not yet started. The CLI remains unstarted, planned as a thin
wrapper once the binder itself is stable post-cutover.

## Gate 3 — Bounds enforcement via CrossHair API: DECIDED, stay-CLI (empirically tested, 2026-07-05)

**Result:** seed override tested for real, not just read. The verification
script itself had three bugs that only surfaced by actually running it —
worth recording, since it's the same lesson this whole gate has been
teaching, now caught in my own "corrected" output:

1. The documented constructor `AnalysisOptions(max_iterations=...,
   per_condition_timeout=...)` throws `TypeError` on the installed
   0.0.107 — `analyze_function` actually wants `AnalysisOptionSet`.
2. Importing from bare `crosshair.core` raises
   `CrossHairInternal("Opcode patches haven't been loaded yet.")` —
   needs `crosshair.core_and_libs`.
3. The critical one: `analyze_function` only parses conditions into
   `Checkable` objects — it never runs the solver unless `.analyze()` is
   called on each one. The uncorrected script "passed" in under a second
   without ever actually invoking CrossHair. A script that runs without
   error is not the same as a script that tested anything.

**After fixing all three:** ran twice per seed, on two targets — the
clean kernel (no counterexample either way) and the broken variant
(which has real counterexamples). **Both seeds produced byte-identical
results, including identical counterexamples on the broken variant.**
The patch applies without error. It has no observed effect.

**Decision:** stay on CLI capture. `seed` is a confirmed hard
tool-version limitation — not "probably unfixable," empirically tested
and found to have no effect on solver behavior at 0.0.107.
`max_iterations` remains confirmed enforceable via the API, independent
of the seed question — that part of Gate 3 is solved and can be wired in
whenever it's useful.

**Status: closed.**

## Gate 4 — Binding authorship: DECIDED (option 3), mechanism recorded, building deferred to Gate 2

**Decision:** option 3 — both models, cross-checked, Tier-1 failure on
disagreement. Matches the cross-validation philosophy already built into
the four-variant design.

**Mechanism (recorded, not yet built):** dual-authorship cross-checking
via verified code-location match —
- **Top-down contract:** the system/QA-authored master traceability
  config states "REQ-X is verified by the proof/test at file F, method
  M."
- **Bottom-up contract:** the source-embedded assertion (a decorator,
  structured comment, or in Dafny's case an `ensures`/`invariant` clause)
  states "this method verifies REQ-X."
- **Intersection check:** at generation time, extract both, and flag
  non-compliant if the physical file/method/hash doesn't match between
  them. This is exactly what Fable's bonus finding from Gate 5 flagged as
  missing — the current C builder binds evidence without verifying it
  against the capture's actual target.

**Status:** decision and mechanism locked. Building this is Gate 2's
binder work, not a separate task — the intersection check above is also
Gate 2's clearest concrete CONFLICT trigger (see below).

## Gate 6 — FRN: RESOLVED

`FRN` = FDA Product Code for "Infusion Pump" (21 CFR 880.5725). Within the
GIP taxonomy specifically, denotes general-purpose volumetric infusion
pumps (peristaltic mechanism, cassette-based administration set), distinct
from `All`. Resolved via NotebookLM's extraction of the full source PDF,
cross-checked against independent FDA-registry research landing on the
same code. Well-supported, not yet independently re-verified against the
raw Sec 2.4.1 text. Full trail in `sources/README.md`.

---

## Phase C — now concrete, not just an interface contract

Previously this section only flagged two things to design for (the
false-zero trap, PROVEN's exclusivity). External research (IronSpec,
MutDafny) gives Phase C actual mechanisms rather than open design
questions.

### 1. Spec-Testing Proofs (STPs) — validate specs against intent before proving code

IronSpec's methodology: prove that specific, manually chosen input/output
pairs are correctly accepted or rejected *by the specification itself*,
independent of whether the implementation satisfies it. This is a direct,
mechanized fix for the exact class of bug Gate 1 found by hand
(REQ-GIP-1-4-12's spec/evidence not matching its text) — an STP would
have caught that the "alarm" spec only encoded clamping before any proof
was attempted.

**Action:** every Dafny spec written for Phase C gets a small STP suite
alongside it, authored by whoever writes the spec, checked in as part of
the evidence chain.

### 2. Mutation testing (MutDafny operators) — catch weak/vacuous specs

Six operators with specific, testable purposes: Relational (ROR) and
Arithmetic (AOR) Operator Replacement test whether numeric bounds are
load-bearing; Set (SOR) and Heap (HOR) Operator Replacement target
predicate-membership and frame-condition weaknesses; Logical Operator
Replacement (LOR) finds redundant/vacuous boolean conditions; Constant
Operator Insertion (COI) inserts negations to check the spec actually
constrains the state space. IronSpec's three-pass framework (discard
logically-weaker mutants, discard vacuity-inducing mutants, re-verify
survivors) is the filtering logic to reuse rather than reinvent.

**Action:** run this against `dosage.py`'s eventual Dafny spec before
trusting any PROVEN claim. A mutation that survives (proof still passes)
on the max-dose boundary means that boundary isn't actually proven.

### 3. Four specific Dafny output-parsing vulnerabilities (sharpens the false-zero trap)

The original false-zero note said "assert the literal substring '0
errors'." That's necessary but not sufficient. Four distinct failure
modes need guarding against, each with a different signature:

- **Vacuous proofs from contradictory preconditions** — a `requires`
  clause that's unsatisfiable (e.g. `x > 0 && x < 0`) makes the empty
  logical state vacuously satisfy any postcondition. "0 errors" with an
  unreachable precondition is not a proof of anything.
- **Weak postconditions** — a one-way implication (`==>`) where a
  bi-implication (`<==>`) was needed lets a broken implementation (e.g.
  a function that always returns empty) still satisfy the spec.
- **Timeout/resource-limit masking** — if the CI wrapper doesn't capture
  the verifier's actual exit code and intermediate timeout warnings, a
  run that aborted partway can still report success for the sections that
  did complete, silently leaving complex paths unverified.
- **Specification stripping** (flagged, detail cut off in source — needs
  a follow-up read of the full document if the fourth vector matters for
  the LLM-self-healing-loop scenario it was describing).

**Action:** the Dafny adapter's parser needs explicit checks for the
first three at minimum — not just string-matching the output, but
verifying precondition satisfiability, checking for bi-implication
patterns on safety-critical postconditions, and capturing real exit
codes/timeout signals. Static coverage analysis (also from IronSpec-
adjacent research) gives a fourth check: flag implementation branches
that could be swapped for arbitrary logic without failing verification —
directly would have caught REQ-GIP-1-4-12's clamp/alarm gap mechanically.

### 4. NL-dialogue confirmation as a process control

Before the proof search runs: generate a plain-English summary of what
the formal spec actually asserts, get explicit human sign-off that the
summary matches intent. This is the process fix that prevents Gate 1's
finding from recurring — catch the intent/spec mismatch at authoring
time, not at review time.

### PROVEN's exclusivity (unchanged from prior version)

R2 (`assert_no_realized_proven`) still guarantees PROVEN never appears as
a realized strength anywhere in Phase B. Phase C's job is narrowly to earn
the right to lift that guarantee for Dafny-backed requirements only, via
the mechanisms above — not to relax the guarantee generally.

---

## What "done" looks like for this roadmap

Every gate resolved, blocked-and-named, or explicitly deferred with a
stated reason. Gate 3 is closed — tested empirically, not assumed. Gate 4
is decided (option 3) with its mechanism recorded; building it is Gate 2's
binder work. Gate 2's CONFLICT rule is now defined and ratified — two
sub-types (identity mismatch, outcome mismatch), tested against three
cases (two positive, one negative) — with only the build (the
vocabulary-agnostic binder, plus the Type 2 cross-manifest comparison
mechanism) still open. Gate 6 (FRN) is resolved and written into four
files. Phase C now has four concrete mechanisms to implement rather than
two open design questions.
