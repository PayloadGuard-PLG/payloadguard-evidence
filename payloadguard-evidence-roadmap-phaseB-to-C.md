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
- Gate 3 (bounds enforcement) — decided 2026-07-06 by an actual executed
  behavioral test (not just the corrected-technique writeup below): the
  seed-override patch produced no observable effect on two real targets.
  Stay-CLI. See `KNOWN_LIMITATIONS.md` for the full result.

## Guiding principle (unchanged)

Open questions get resolved at the gate where they're first encountered,
with the resolution documented inline — not batched and left for later.
If a gate can't be resolved when reached, name it explicitly as blocked
and why.

---

## Gate 2 — CONFLICT rule (still blocked, now with a candidate test case)

Still not defined anywhere in the Blueprint or SYSTEM_BLUEPRINT.md beyond
a to-do mention — correctly left unresolved rather than inferred.

**New input toward a definition:** the dual-authorship traceability
pattern (below, from external research) gives a concrete trigger
condition to test any proposed CONFLICT definition against: if a
top-down ALM-authored contract claims "REQ-X is verified at file F,
method M" and the bottom-up source-embedded assertion says the verified
method is actually at a different file/method/hash, that mismatch is a
strong CONFLICT candidate — evidence exists on both sides, but they
disagree about what was actually checked. REQ-GIP-1-4-12's kernel_scope
vs. system_scope split (one evidenced, one an explicit GAP) is a
different case — that's not a conflict, it's a documented absence. Useful
to have both a positive and negative test case before locking a
definition.

**Action:** define CONFLICT against these two contrasting cases before
building it, so the definition earns its keep rather than being invented
in the abstract.

## Gate 3 — Bounds enforcement via CrossHair API (DECIDED 2026-07-06: stay-CLI)

**max_iterations — real, confirmed against the installed package
(0.0.107), with one correction to the roadmap's own claim.** The roadmap
version of this section claimed `AnalysisOptions(max_iterations=...,
per_condition_timeout=...)` was "a real, documented constructor" usable
directly. Running it against the actually-installed 0.0.107 raised
`TypeError: missing 9 required positional arguments` — `AnalysisOptions`
has no defaults and was never the type `analyze_function` accepts.
`analyze_function`'s real second parameter is `AnalysisOptionSet`, the
partially-specified/defaultable sibling type — confirmed by reading the
installed package's source (`crosshair/options.py`,
`crosshair/core.py::analyze_function`). `AnalysisOptionSet(max_iterations=100000,
per_condition_timeout=30)` works and is threaded through into the
resolved `AnalysisOptions` correctly. This matches what the Gate 3
investigation already on file before this roadmap had found.

**seed — patched without error, but a real two-target behavioral test
found zero observable effect.** The corrected technique (patch
`crosshair.statespace.make_default_solver`, hyphenated Z3 param names
`random-seed` / `smt.random-seed`) was executed for real via
`examples/dosage_calculator/gate3_seed_patch_test.py`
(`CROSSHAIR_SOLVER_SEED=1` vs `=2`), after fixing two further problems
found only by running it:
1. `analyze_function` imported from bare `crosshair.core` raises
   `CrossHairInternal("Opcode patches haven't been loaded yet.")` when
   `.analyze()` is called on its returned `Checkable`s — the opcode-level
   tracing patches are only installed as a side effect of importing
   `crosshair.core_and_libs`. Fixed by importing `analyze_function` from
   `crosshair.core_and_libs` instead.
2. `analyze_function` alone only parses source into `Checkable` objects
   (one per postcondition) — it does not run the solver. Each `Checkable`
   needs `.analyze()` called on it to actually execute the symbolic
   search and produce real `AnalysisMessage`s.

With both fixes applied, two real runs were executed per seed value:
- `dosage.py::calculate_hourly_dose` (Sample A target, no counterexample
  either way): seed 1 and seed 2 both returned two
  `MessageType.CANNOT_CONFIRM` / "Not confirmed." messages at the same
  two lines — identical.
- `dosage_broken.py::calculate_hourly_dose` (has real counterexamples):
  seed 1 and seed 2 both returned the exact same two counterexamples —
  `calculate_hourly_dose(1.0, 1.0, 0.5, 0.25)` → `0.5` and
  `calculate_hourly_dose(0.5, 0.25, -0.125, 0.125)` → `-0.03125` — the
  same values already on file in `raw_crosshair_output_broken.txt`,
  captured under the CLI's own hard-coded seed 42.

**Decision:** stay-CLI. The patch installs without error, but produces no
measurable behavioral difference on either target tested. Documented as
a tool-version limitation, not an interface one: `seed` cannot be
demonstrated to work via this technique on 0.0.107, so the declared
`seed: 1` in `metadata.yaml` remains unenforceable and unenforced.
`max_iterations` is confirmed enforceable via the API
(`AnalysisOptionSet`) should a future decision revisit wiring the harness
through the API instead of the CLI — but that's a separate cost/benefit
call from the seed question, since CLI capture fidelity was the
counterweight in the original options list.

**Also flagged:** the CrossHair repo's latest *tagged* release is
v0.0.106 on GitHub at last check, while both this project's toolchain pin
and the actually-installed package are 0.0.107 (`pip show crosshair-tool`
confirmed) — consistent with each other. No discrepancy in practice; a
PyPI release can exist ahead of its corresponding git tag. Not an open
item.

## Gate 4 — Binding authorship (option 3 confirmed, now with a mechanism)

**Decision on record:** option 3 — both models, cross-checked, Tier-1
failure on disagreement. Matches the cross-validation philosophy already
built into the four-variant design.

**Mechanism from external research:** dual-authorship cross-checking via
verified code-location match —
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

**Action:** build Gate 2's generalized binder to perform this
intersection check as a Tier-1 gate, not just a convention. This also
gives Gate 2's CONFLICT rule its clearest concrete trigger (see above).

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
stated reason. Gate 3 is now closed (stay-CLI, decided 2026-07-06 by real
test). Gate 2 needs a definition tested against the two candidate cases
above. Gate 4's mechanism is specified; building it is Gate 2's binder
work. Phase C now has four concrete mechanisms to implement rather than
two open design questions.
