# PayloadGuard Evidence Layer — Roadmap: Phase B → Phase C

Updated 2026-07-06: Phase B's gate ledger is now fully closed (Gates
1–6 all resolved, decided, or complete — see below), and Phase C is
restructured from a two-mechanism sketch into a gate-sequenced plan
(Gates C1–C6) mirroring how Phase B was actually run. Gate C1's Dafny
toolchain blocker — resolved same day: modern Dafny 4.11.0 obtained via
NuGet (`dotnet tool install --global dafny`), no GitHub involvement,
verified against the real binary. Nothing else in Phase C is built yet
— capture runner, real spec, and PROVEN-exclusivity migration are all
still ahead.

## Where we are

- Phase A closed (R1–R3).
- Gate 1 (artifact generation) — clean pass. Fact-equality holds (7
  facts, consistent across A/B/C-split renders). Two defects found and
  fixed: the Notes-column cross-evidence-type leak/duplication, and
  REQ-GIP-1-4-12's evidence not matching its "shall trigger an alarm"
  text.
- Gate 5 (single-evidence-type fixture) — fully resolved 2026-07-06: the
  concrete-only case that was blocked (variant C bound symbolic evidence
  unconditionally) is now constructible, see below.
- Gate 6 (FRN) — resolved, see below.
- Gate 2 (CONFLICT rule + vocabulary-agnostic binder + CLI) — COMPLETE,
  see below.

## Guiding principle (unchanged)

Open questions get resolved at the gate where they're first encountered,
with the resolution documented inline — not batched and left for later.
If a gate can't be resolved when reached, name it explicitly as blocked
and why.

---

## Gate 2 — CONFLICT rule + binder + CLI: COMPLETE

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

**Vocabulary-agnostic binder — COMPLETE (Steps 1 through 4, plus the CLI).**
`evidence/render/matrix_variants.py` gained `build_matrix()`: a literal
extraction of all three existing variants' binding/rendering logic into
named, reusable functions, dispatched through one declarative table
instead of three top-level functions. Proven byte-identical (dict AND
JSON-string equality) to the original `build_matrix_variant_a/b/c` over
real committed data (`tests/test_binder_equivalence.py`, 5 tests). Step
2: `generate_matrix_a.py` / `_b.py` / `_c.py` now call `build_matrix()`
instead of the original functions — Steven approved with an explicit
request to keep a fallback available, so `build_matrix_variant_a/b/c`
are deliberately kept in place, unused, rather than deleted in the same
step (one-line revert per generator, or a plain `git revert`, if a
problem ever surfaces). Step 3: CONFLICT Type 1 is now folded into
`build_matrix()` itself — checked on every call, not just inside the
full pipeline, closing a real gap (previously running `generate_matrix_a.py`
alone would have bypassed it entirely). Type 2 was deliberately NOT
folded in: it compares raw manifests across the whole dataset, not any
single variant's binding, so it has no per-variant home and correctly
stays a standalone stage, the same way fact-equality does. The frozen
base matrix (never calling `build_matrix()`) keeps its own narrower
explicit check. Verified at every step, not assumed: the full pipeline
was re-run end to end after each change and every regenerated artifact
diffed against the pre-cutover committed versions — differs only by
timestamp throughout.

**CLI — built ahead of Step 4, at Steven's explicit direction** ("get
the CLI done first" before deleting the Step 2 fallback). `evidence/cli.py`
(`python -m evidence.cli build`) wraps `build_matrix()` with metadata/
manifest/concrete/schema paths as arguments instead of hardcoding
`examples/dosage_calculator` — the genuinely vocabulary-agnostic
surface Gate 2 was named for. tool_versions is now keyed by the
manifest's own declared tool name rather than a hardcoded `"crosshair"`
string. Two real bugs were caught and fixed while building it: an
uncaught `jsonschema.ValidationError` dumped the entire schema on a
validation failure (fixed to use `.message`), and omitting both output
paths printed JSON and markdown concatenated to stdout as invalid
combined output (fixed so markdown only ever goes where `--out-md`
explicitly says to). `tests/test_cli.py` (10 tests) drives the CLI via
subprocess for all four variants and proves byte-identical output to
the committed artifacts, plus both error paths. Suite: 44 passed.

**Step 4 — done.** Requested last, deliberately after the CLI landed:
`build_matrix_variant_a/b/c` deleted from `matrix_variants.py` (their
shared markdown renderers stayed — `build_matrix()` already used those);
`tests/test_binder_equivalence.py` deleted too, since its entire purpose
(proving old-function output equals `build_matrix()` output) is moot
once the old functions don't exist. `tests/test_single_evidence_type.py`
(Gate 5's fixture test) was the one other place calling
`build_matrix_variant_c` directly — migrated to `build_matrix()`.
Verified after deletion, not just before it: full suite (39 passed — 44
minus the 5 deleted equivalence tests), full pipeline re-run (every
regenerated artifact still differs only by timestamp), and the CLI
re-checked independently against a committed artifact. Git history
holds the deleted functions and test if a fallback is ever needed again
— that was the entire point of the Step 2→3→CLI→4 ordering rather than
deleting immediately after the cutover.

**Gate 2 is now structurally complete.** Nothing remains in its binder
work; the only item anywhere in Gate 2's scope was the CONFLICT rule's
own definition, already ratified.

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

## Gate 4 — Binding authorship: DECIDED (option 3), mechanism BUILT via Gate 2

**Decision:** option 3 — both models, cross-checked, Tier-1 failure on
disagreement. Matches the cross-validation philosophy already built into
the four-variant design.

**Mechanism, built as Gate 2's CONFLICT Type 1** (`evidence/conflict.py`,
folded into `build_matrix()`): dual-authorship cross-checking via
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
  missing — variant C's builder didn't verify evidence against the
  capture's actual target; the concrete-side check now runs (via
  `evidence/conflict.py`). C's concrete evidence *binding* stays
  evidence-store-carried by design (unchanged); the SYMBOLIC binding is
  no longer unconditional — see Gate 5.

**Status:** decision, mechanism, and build all done. `evidence/conflict.py`'s
`concrete_binding_conflicts` / `symbolic_binding_conflicts` implement the
intersection check for real, run inside `build_matrix()` on every call.

## Gate 5 — single-evidence-type fixture for variant C: FULLY RESOLVED (2026-07-06)

Originally resolved for the constructible half only: a symbolic-only
fixture (no `evidence` list declared) correctly appeared in exactly one
of variant C's two artifacts. Concrete-only was named as impossible —
`_bind_self_describing` bound a symbolic record to every requirement
unconditionally, regardless of what it declared, so nothing could ever
be concrete-only.

**Fix:** `_bind_self_describing` now checks each requirement's declared
`evidence` list before binding symbolic evidence — a requirement
declaring only `concrete_test` entries gets no symbolic record. When
`evidence` is absent entirely, the original unconditional behavior is
preserved (the existing symbolic-only fixture relies on exactly this
fallback, and still passes unchanged). Concrete binding is untouched —
still fully self-describing via `concrete_results.json`'s own
`requirement_id`, per Gate 4's decision for C.

No effect on committed data: every real requirement in `metadata.c.yaml`
declares `crosshair`, so nothing changed observably — confirmed by
regenerating and diffing (timestamp aside). `tests/test_single_evidence_type.py`
now proves both directions: symbolic-only and (new) concrete-only each
appear in exactly one artifact. Suite: 41 passed.

## Gate 6 — FRN: RESOLVED

`FRN` = FDA Product Code for "Infusion Pump" (21 CFR 880.5725). Within the
GIP taxonomy specifically, denotes general-purpose volumetric infusion
pumps (peristaltic mechanism, cassette-based administration set), distinct
from `All`. Resolved via NotebookLM's extraction of the full source PDF,
cross-checked against independent FDA-registry research landing on the
same code. Well-supported, not yet independently re-verified against the
raw Sec 2.4.1 text. Full trail in `sources/README.md`.

---

## Phase C — gate-sequenced plan (2026-07-06)

Restructured from a two-mechanism sketch into gates, mirroring how Phase
B was actually run: each gate has a scope, a dependency, and (where one
exists) a decision that has to land before building starts. Nothing
below is built yet — this is the plan, produced before any Phase C code,
per the same discipline Phase B used (design review before implementation,
verify against the real environment before assuming a tool works a
certain way).

### Environment check (done 2026-07-06; RESOLVED same day — modern Dafny obtained)

- **Z3 4.16.0 is present** — both the `z3` CLI and the `z3` Python
  bindings import cleanly (`import z3` succeeds). Usable directly for
  satisfiability-style checks (Gate C3) — confirmed working (see below).
- **Dafny was not installed**, and apt's only offering was
  `2.3.0+dfsg-0.1` — an Ubuntu-universe package from roughly 2015,
  Mono-based, not modern .NET. **Resolved by researching further rather
  than settling for it:** GitHub release downloads are genuinely blocked
  by egress policy (confirmed via the proxy's own status endpoint — a
  policy denial, not a config problem, so not routed around), but
  `api.nuget.org` is reachable and apt has `dotnet-sdk-8.0` directly
  (Ubuntu's own package). Installed the SDK, then ran
  `dotnet tool install --global dafny`, which pulled from NuGet — no
  GitHub involvement anywhere. Result: **Dafny 4.11.0**, a real current
  release.
- **Verified against the running binary, not documentation:** a clean
  pass on a valid clamping method produced exactly `Dafny program
  verifier finished with 1 verified, 0 errors`, exit 0 — matching
  `evidence/model.py`'s false-zero note precisely. A broken method
  produced per-line error blocks plus `0 verified, 2 errors`, **exit
  code 4** (not 1 — a real finding: Dafny's exit codes aren't a simple
  0/1 pair the way CrossHair's are). An unsatisfiable precondition
  (`x > 0 && x < 0`) against an obviously-false postcondition verified
  clean — confirming Gate C3's vector 1 is a real, reproducible risk on
  this binary, not speculative. `dafny audit` was checked against the
  same case and found nothing (`0 findings`) — it's scoped to
  un-annotated assumes/axioms/non-determinism, not general precondition
  satisfiability, so Gate C3's originally-planned Z3-based mitigation is
  still the right approach — confirmed technically feasible (`z3.Solver()`
  correctly returns `unsat`/`sat` for the contradictory/real cases
  respectively).
- **No alteration to the plan needed.** If anything the plan is on
  firmer ground than when it was written: the false-zero note holds
  exactly, the vacuous-precondition risk is empirically confirmed rather
  than assumed, and its mitigation is confirmed feasible with tools
  already present. One concrete addition to carry into Gate C1: capture
  the exit code as-is rather than assuming a specific nonzero value.
  Full findings: `KNOWN_LIMITATIONS.md`.
- **Not done yet:** this was toolchain research, not Gate C1 itself — no
  capture runner, no real Dafny spec for `dosage.py`, nothing committed
  to the repository. That's the next step.

### Gate C1 — Dafny adapter: capture + minimal false-zero guard (build first)

- A capture runner mirroring `run_verify.py`'s discipline: invoke Dafny
  as a subprocess, commit verbatim stdout+stderr, the exact command
  argv, exit code, and ISO-8601 UTC timestamp — no re-running evidence
  inside the generation pipeline, same as every existing capture.
- **Target decision:** reuse `dosage.py`'s existing contracts, translated
  to Dafny, rather than fork a second worked example — keeps one
  through-line for the REQ-GIP-* citations rather than forking a second
  audit trail. (Flagging as a recommendation, not assuming it's settled.)
- Parser asserts the literal substring `"0 errors"` — the minimum bar
  already named in `evidence/model.py`'s false-zero note. Gate C3
  hardens this further; C1 is the floor, not the ceiling.
- `verifier_completion_status` added to `VerificationResult` (already
  reserved for this in `KNOWN_LIMITATIONS.md` — the field exists in the
  schema/model now, capturing whether the verifier actually completed
  vs. timed out or aborted, feeding both C1's and C3's checks).

### Gate C2 — PROVEN's exclusivity migration (do this right after C1, before any real spec)

The highest-consequence change in Phase C — sequenced early, before a
real Dafny spec exists, so the structural guarantee is in place from the
first real capture rather than retrofitted onto existing data.

- Today, R2 (`assert_no_realized_proven`) hard-fails if ANY record
  anywhere claims PROVEN, full stop. Phase C's job is to earn the right
  to lift that ONLY for Dafny-sourced records — CrossHair/pytest-backed
  requirements must remain permanently excluded even after this lands.
- New structural rule (a ruling in the R1/R2/R2c lineage — call it R3
  when ratified): PROVEN may appear as a realized strength only when a
  record's `method` names the Dafny adapter AND that record passed Gate
  C1/C3's completion and false-zero checks.
- Needs two tests, not one: a positive case (a real Dafny PROVEN record
  is accepted) and a negative case (a CrossHair or concrete_test record
  can *never* carry PROVEN, checked explicitly, not just by omission).
  Recommend this gets the same review weight R1/R2 originally got — a
  ratified design decision, not just a code change — given what's at
  stake if it's wrong.

### Gate C3 — Dafny output-parsing hardening (sharpens the false-zero trap; 3 of 4 vectors scoped)

Four distinct failure modes, each with its own signature — "0 errors" in
the output is necessary but not sufficient:

- **Vacuous proofs from contradictory preconditions** — a `requires`
  clause that's unsatisfiable (e.g. `x > 0 && x < 0`) makes the empty
  logical state vacuously satisfy any postcondition. Checkable: extract
  the precondition and hand it to Z3 (available) for a satisfiability
  check, rather than trusting Dafny's own report.
- **Weak postconditions** — a one-way implication (`==>`) where a
  bi-implication (`<==>`) was needed lets a broken implementation (e.g.
  one that always returns empty) still satisfy the spec. Checkable as a
  pattern/heuristic on safety-critical postconditions — not a full
  proof, named as best-effort.
- **Timeout/resource-limit masking** — capture the real exit code and
  any intermediate timeout warnings (via `verifier_completion_status`
  from C1), not just "0 errors" appearing somewhere in output that may
  have been truncated by a timeout partway through.
- **Specification stripping** — **BLOCKED, named rather than dropped:**
  the source material describing this fourth vector was cut off before
  this session had it in full (an LLM-self-healing-loop scenario was
  referenced but not detailed). Needs a follow-up read of the original
  document before this vector can be scoped at all — per the standing
  discipline, not inferred from the name.

### Gate C4 — Spec-Testing Proofs (STPs)

IronSpec's methodology: prove that specific, manually chosen input/output
pairs are correctly accepted or rejected *by the specification itself*,
independent of whether the implementation satisfies it. Direct,
mechanized fix for the exact class of bug Gate 1 found by hand
(REQ-GIP-1-4-12's spec/evidence not matching its text) — an STP would
have caught that the "alarm" spec only encoded clamping before any proof
was attempted.

**Scope:** every Dafny spec written for Phase C gets a small STP suite
alongside it, authored by whoever writes the spec, checked in as part of
the evidence chain — starting with whatever Gate C1's first real spec is.

### Gate C5 — Mutation testing (MutDafny-style) — largest single piece, its own sub-plan

Six operators with specific, testable purposes: Relational (ROR) and
Arithmetic (AOR) Operator Replacement test whether numeric bounds are
load-bearing; Set (SOR) and Heap (HOR) Operator Replacement target
predicate-membership and frame-condition weaknesses; Logical Operator
Replacement (LOR) finds redundant/vacuous boolean conditions; Constant
Operator Insertion (COI) inserts negations to check the spec actually
constrains the state space. IronSpec's three-pass framework (discard
logically-weaker mutants, discard vacuity-inducing mutants, re-verify
survivors) is the filtering logic to reuse rather than reinvent.

**Scope:** run this against `dosage.py`'s eventual Dafny spec before
trusting any PROVEN claim. A mutation that survives (proof still passes)
on the max-dose boundary means that boundary isn't actually proven. This
is effectively building a mutation-testing harness for Dafny specs from
nothing — recommend treating it as its own multi-step sub-plan once
Gates C1–C2 are stable, not attempted in one pass the way Gate 2's
CONFLICT rule build was.

### Gate C6 — NL-dialogue confirmation (process control, lightest gate, adopt early)

Before the proof search runs: generate a plain-English summary of what
the formal spec actually asserts, get explicit human sign-off that the
summary matches intent. This is the process fix that prevents Gate 1's
finding from recurring — catch the intent/spec mismatch at authoring
time, not at review time.

This is a workflow practice more than software — the summary-and-sign-off
step itself could be a small script, but the actual artifact is a
recorded decision (mirroring `sources/req-gip-1-4-12-alarm-scope-decision.md`'s
pattern), not a database entry. **No technical dependency on any other
Gate C item** — recommend adopting it as a habit starting with the very
first real Dafny spec, not deferring it behind C1–C5.

### Suggested build order

1. **Environment decision** (which Dafny) — blocks C1 and everything
   downstream of it.
2. **Gate C6** (process habit) — costs nothing to start now, no
   technical blocker.
3. **Gate C1** (capture + minimal false-zero guard) — foundation.
4. **Gate C2** (PROVEN exclusivity migration) — immediately after C1,
   before any real spec exists.
5. **Gate C4** (STPs) — alongside the first real spec.
6. **Gate C3** (parser hardening, 3 of 4 vectors; 4th named-blocked) —
   before trusting any PROVEN claim in earnest.
7. **Gate C5** (mutation testing) — largest, last, its own sub-plan.

### PROVEN's exclusivity today (unchanged until Gate C2 lands)

R2 (`assert_no_realized_proven`) still guarantees PROVEN never appears as
a realized strength anywhere in this repository right now. Nothing in
this plan relaxes that guarantee by itself — Gate C2 is the only gate
that touches it, and only for Dafny-sourced records, never generally.

---

## What "done" looks like for this roadmap

Every gate resolved, blocked-and-named, or explicitly deferred with a
stated reason. Gate 3 is closed — tested empirically, not assumed. Gate 4
is decided (option 3) and its mechanism is built via Gate 2. Gate 2
itself is complete: the CONFLICT rule (two sub-types, tested against
three cases), the vocabulary-agnostic binder (`build_matrix()`, sole
implementation across all four variants, original per-variant functions
deleted), and the CLI (`evidence/cli.py`) are all built and verified.
Gate 6 (FRN) is resolved and written into four files. Gate 5 is now
fully resolved: variant C's binder no longer binds symbolic evidence
unconditionally, so a concrete-only fixture is constructible — the last
open item from the original six-gate ledger. **Phase B's gate ledger is
fully closed.**

Phase C is now a gate-sequenced plan (Gates C1–C6, suggested build order
above), not a two-mechanism sketch — produced with the same discipline
Phase B used: real environment check before assuming a tool works a
certain way. That check found Dafny not installed and apt's only
offering badly out of date (2.3.0+dfsg from roughly 2015) — researched
further rather than settling for it or asking for an under-informed
decision, and resolved same day: modern Dafny 4.11.0 obtained via NuGet,
verified against the real binary (exact false-zero match, real exit-code
behavior, the vacuous-precondition risk confirmed reproducible, its Z3
mitigation confirmed feasible). One gate (C3's fourth vector,
specification stripping) stays named as blocked on incomplete source
material rather than guessed at. Nothing in Phase C is *built* yet —
Gate C1's capture runner and a real Dafny spec for `dosage.py` are next.
